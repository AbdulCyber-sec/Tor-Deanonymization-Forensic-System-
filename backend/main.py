"""
TOR Guard Node Prediction System - FastAPI Backend
Integrates XGBoost model with real-time prediction and explainability
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import random
import joblib
import pandas as pd
import numpy as np
import csv
from pathlib import Path
import time
import json

# Initialize FastAPI app
app = FastAPI(
    title="TGNP API",
    description="TOR Guard Node Prediction System REST API",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite/React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model storage
MODEL_PATH = Path("../models/xgboost_guard_predictor.json")
ENCODERS_PATH = Path("../models/encoders.pkl")
FEATURE_COLS_PATH = Path("../models/feature_columns.pkl")

model = None
encoders = None
feature_columns = None
guard_fingerprints = None  # For inverse transform
guard_meta = {}


class PredictionRequest(BaseModel):
    """Request schema for guard node prediction"""
    exit_fingerprint: str = Field(..., description="Exit relay fingerprint (40-char hex)")
    exit_country: str = Field(..., description="Exit node country")
    bandwidth: float = Field(default=0.0, description="Observed bandwidth in MB/s")
    setup_time: float = Field(default=0.0, description="Circuit setup time in seconds")
    middle_fingerprint: Optional[str] = Field(default=None, description="Middle node fingerprint if known")
    middle_country: Optional[str] = Field(default=None, description="Middle node country")


class GuardPrediction(BaseModel):
    """Individual guard node prediction"""
    guard_fingerprint: str
    guard_nickname: str
    guard_address: str
    guard_country: str
    confidence: float
    rank: int


class FeatureImportance(BaseModel):
    """Feature contribution to prediction"""
    feature: str
    importance: float
    value: Any
    impact: str  # "high", "medium", "low"


class PredictionResponse(BaseModel):
    """Response schema with predictions and explainability"""
    predictions: List[GuardPrediction]
    prediction_time_ms: float
    model_version: str
    explainability: Optional[Dict[str, Any]] = None


class NodeType(str, Enum):
    guard = "guard"
    middle = "middle"
    exit = "exit"


class TopologyNode(BaseModel):
    id: str
    fingerprint: str
    nickname: str
    role: NodeType
    country: str
    bandwidth: float
    degree: int


class TopologyLink(BaseModel):
    source: str
    target: str
    circuit_weight: float
    latency_ms: float


class TopologyResponse(BaseModel):
    generated_at: str
    node_count: int
    link_count: int
    nodes: List[TopologyNode]
    links: List[TopologyLink]
    note: str


@app.on_event("startup")
async def load_model():
    """Load model and encoders on startup"""
    global model, encoders, feature_columns, guard_fingerprints
    
    try:
        # Load XGBoost model
        import xgboost as xgb
        model = xgb.XGBClassifier()
        model.load_model(str(MODEL_PATH))
        
        # Load encoders
        with open(ENCODERS_PATH, 'rb') as f:
            encoders = joblib.load(f)
        
        # Load feature columns
        with open(FEATURE_COLS_PATH, 'rb') as f:
            feature_columns = joblib.load(f)
        
        # Extract guard fingerprints from label encoder
        guard_fingerprints = encoders['guard_fingerprint'].classes_
        
        print(f"✓ Model loaded successfully")
        print(f"✓ {len(guard_fingerprints)} guard nodes available")
        print(f"✓ {len(feature_columns)} features configured")
        # Load guard/middle/exit metadata from engineered CSV (supports headered or raw positional)
        try:
            csv_path = Path(__file__).resolve().parents[1] / 'data' / 'circuit_data_engineered.csv'
            if not csv_path.exists():
                print(f"i Metadata CSV not found at {csv_path}; continuing without relay enrichment")
            else:
                loaded = 0
                with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                    first_line = f.readline()
                    f.seek(0)
                    has_header = 'guard_fingerprint' in first_line.lower()
                    if has_header:
                        reader = csv.DictReader(f)
                        for row in reader:
                            fp = (row.get('guard_fingerprint') or '').strip()
                            if len(fp) != 40:
                                continue
                            guard_meta[fp] = {
                                'guard_nickname': row.get('guard_nickname') or f"Guard_{fp[:6]}",
                                'guard_address': row.get('guard_address') or 'Unknown',
                                'guard_country': row.get('guard_country') or 'Unknown',
                            }
                            loaded += 1
                    else:
                        reader = csv.reader(f)
                        for row in reader:
                            if not row or len(row) < 8:
                                continue
                            fp = row[4].strip()
                            if len(fp) != 40:
                                continue
                            nickname = row[5].strip() if len(row) > 5 else ''
                            ip_addr = row[6].strip() if len(row) > 6 else ''
                            country = row[7].strip() if len(row) > 7 else ''
                            guard_meta[fp] = {
                                'guard_nickname': nickname or f"Guard_{fp[:6]}",
                                'guard_address': ip_addr or 'Unknown',
                                'guard_country': country or 'Unknown',
                            }
                            loaded += 1
                print(f"✓ Loaded guard metadata for {loaded} guards from CSV (header: {has_header})")
        except Exception as e:
            print(f"⚠ Metadata load failed: {e}")
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        raise


def engineer_features(request: PredictionRequest) -> pd.DataFrame:
    """
    Replicate feature engineering from training pipeline
    Creates same 31 features expected by the model
    """
    
    # Start with basic features - use defaults for guard node (which we're predicting)
    data = {
        'guard_bandwidth': 8.5,  # Default typical value
        'middle_bandwidth': 7.0,
        'exit_bandwidth': request.bandwidth if request.bandwidth > 0 else 6.5,
        'circuit_setup_duration': request.setup_time,
        'total_bytes': request.bandwidth * request.setup_time * 1e6 if request.bandwidth > 0 else 1e7,
    }
    
    # Guard and middle countries (guard is what we're predicting, use placeholder)
    guard_country = 'US'  # Default placeholder
    middle_country = request.middle_country if request.middle_country else 'Unknown'
    exit_country = request.exit_country
    
    df = pd.DataFrame([data])
    
    # === BANDWIDTH RATIOS ===
    df['bw_ratio_guard_middle'] = df['guard_bandwidth'] / (df['middle_bandwidth'] + 1e-6)
    df['bw_ratio_guard_exit'] = df['guard_bandwidth'] / (df['exit_bandwidth'] + 1e-6)
    df['bw_ratio_middle_exit'] = df['middle_bandwidth'] / (df['exit_bandwidth'] + 1e-6)
    df['bw_total'] = df['guard_bandwidth'] + df['middle_bandwidth'] + df['exit_bandwidth']
    df['bw_min'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].min(axis=1)
    df['bw_max'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].max(axis=1)
    df['bw_std'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].std(axis=1)
    
    # === GEOGRAPHIC FEATURES ===
    df['same_country_guard_middle'] = int(guard_country == middle_country)
    df['same_country_guard_exit'] = int(guard_country == exit_country)
    df['same_country_middle_exit'] = int(middle_country == exit_country)
    df['all_same_country'] = int((guard_country == middle_country) and (guard_country == exit_country))
    unique_countries = len(set([guard_country, middle_country, exit_country]))
    df['country_diversity'] = unique_countries / 3.0
    
    # === HISTORICAL FEATURES (using defaults for real-time prediction) ===
    df['guard_usage_freq'] = 0.5  # Average usage
    df['middle_usage_freq'] = 0.5
    df['exit_usage_freq'] = 0.5
    df['guard_exit_pair_freq'] = 0.1
    df['guard_avg_bandwidth'] = df['guard_bandwidth']
    df['guard_middle_pair_freq'] = 0.1
    df['guard_prefers_exit_country'] = 0.5
    
    # === ENCODE CATEGORICAL FEATURES ===
    try:
        df['middle_fingerprint_encoded'] = encoders['middle_fingerprint'].transform([request.middle_fingerprint or 'UNKNOWN'])[0]
    except:
        df['middle_fingerprint_encoded'] = -1
    
    try:
        df['exit_fingerprint_encoded'] = encoders['exit_fingerprint'].transform([request.exit_fingerprint])[0]
    except:
        df['exit_fingerprint_encoded'] = -1
    
    try:
        df['guard_country_encoded'] = encoders['guard_country'].transform([guard_country])[0]
    except:
        df['guard_country_encoded'] = -1
    
    try:
        df['middle_country_encoded'] = encoders['middle_country'].transform([middle_country])[0]
    except:
        df['middle_country_encoded'] = -1
    
    try:
        df['exit_country_encoded'] = encoders['exit_country'].transform([exit_country])[0]
    except:
        df['exit_country_encoded'] = -1
    
    # === INTERACTION FEATURES ===
    df['bw_guard_x_setup'] = df['guard_bandwidth'] * df['circuit_setup_duration']
    df['bw_total_x_bytes'] = df['bw_total'] * df['total_bytes']
    
    # Select only the features used during training
    X = df[feature_columns]
    
    return X


def get_top_k_predictions(probabilities: np.ndarray, k: int = 10) -> List[GuardPrediction]:
    """Convert model probabilities to ranked predictions"""
    
    # Get top-K indices
    top_k_indices = np.argsort(probabilities[0])[::-1][:k]
    
    predictions = []
    for rank, idx in enumerate(top_k_indices, 1):
        guard_fp = guard_fingerprints[idx]
        confidence = float(probabilities[0][idx])
        
        # In production, fetch from database; here we use placeholders
        meta = guard_meta.get(guard_fp, {})
        predictions.append(GuardPrediction(
            guard_fingerprint=guard_fp,
            guard_nickname=meta.get('guard_nickname') or f"GuardNode{idx:03d}",
            guard_address=meta.get('guard_address') or "Unknown",
            guard_country=meta.get('guard_country') or "Unknown",
            confidence=confidence,
            rank=rank
        ))
    
    return predictions


def get_feature_importance(model, feature_values: pd.DataFrame, top_n: int = 5) -> List[FeatureImportance]:
    """Extract top feature importance for explainability"""
    
    # Get feature importance from XGBoost
    importance_dict = model.get_booster().get_score(importance_type='weight')
    
    # Map to feature names
    feature_importance = []
    for i, col in enumerate(feature_columns):
        feat_name = f"f{i}"
        importance = importance_dict.get(feat_name, 0.0)
        
        if importance > 0:
            value = feature_values[col].iloc[0]
            feature_importance.append({
                'feature': col,
                'importance': importance,
                'value': value
            })
    
    # Sort by importance and take top N
    feature_importance.sort(key=lambda x: x['importance'], reverse=True)
    top_features = feature_importance[:top_n]
    
    # Normalize importance to 0-1
    max_importance = max([f['importance'] for f in top_features]) if top_features else 1.0
    
    result = []
    for feat in top_features:
        normalized_imp = feat['importance'] / max_importance
        impact = "high" if normalized_imp > 0.7 else "medium" if normalized_imp > 0.4 else "low"
        
        result.append(FeatureImportance(
            feature=feat['feature'],
            importance=normalized_imp,
            value=feat['value'],
            impact=impact
        ))
    
    return result


def generate_topology(limit: int = 40) -> TopologyResponse:
    """Generate a synthetic relay interaction topology for visualization.

    This constructs a small force-directed style graph consisting of sampled guard,
    middle, and exit nodes plus circuit links. In production this would be replaced
    with real circuit co-occurrence statistics and relay consensus data.
    """

    # Fallback if model not loaded yet
    fingerprints = guard_fingerprints if guard_fingerprints is not None else [f"FAKE{i:04X}" for i in range(200)]

    # Sample unique guard nodes
    sample_size = min(max(10, limit // 3), len(fingerprints))
    sampled_guards = random.sample(list(fingerprints), sample_size)

    # Create synthetic middle & exit nodes derived from guard fingerprints for now
    sampled_middles = [f"MID-{fp[:12]}" for fp in sampled_guards[: sample_size]]
    sampled_exits = [f"EXT-{fp[-12:]}" for fp in sampled_guards[: sample_size]]

    countries_pool = ["US", "DE", "FR", "GB", "NL", "CA", "SE", "NO", "CH", "JP"]

    nodes: List[TopologyNode] = []

    def mk_node(fingerprint: str, role: NodeType) -> TopologyNode:
        return TopologyNode(
            id=fingerprint,
            fingerprint=fingerprint,
            nickname=("Guard" if role == NodeType.guard else ("Middle" if role == NodeType.middle else "Exit")) + fingerprint[-5:],
            role=role,
            country=random.choice(countries_pool),
            bandwidth=round(random.uniform(2.0, 15.0), 2),
            degree=0,  # will be updated
        )

    for fp in sampled_guards:
        nodes.append(mk_node(fp, NodeType.guard))
    for fp in sampled_middles:
        nodes.append(mk_node(fp, NodeType.middle))
    for fp in sampled_exits:
        nodes.append(mk_node(fp, NodeType.exit))

    # Build circuit style links guard -> middle -> exit
    links: List[TopologyLink] = []
    for g, m, e in zip(sampled_guards, sampled_middles, sampled_exits):
        # Guard -> Middle
        links.append(TopologyLink(
            source=g,
            target=m,
            circuit_weight=round(random.uniform(0.1, 1.0), 3),
            latency_ms=round(random.uniform(5, 60), 1)
        ))
        # Middle -> Exit
        links.append(TopologyLink(
            source=m,
            target=e,
            circuit_weight=round(random.uniform(0.1, 1.0), 3),
            latency_ms=round(random.uniform(5, 60), 1)
        ))

    # Update node degrees
    degree_map: Dict[str, int] = {}
    for lk in links:
        degree_map[lk.source] = degree_map.get(lk.source, 0) + 1
        degree_map[lk.target] = degree_map.get(lk.target, 0) + 1
    for n in nodes:
        n.degree = degree_map.get(n.id, 0)

    return TopologyResponse(
        generated_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        node_count=len(nodes),
        link_count=len(links),
        nodes=nodes,
        links=links,
        note="Synthetic topology for visualization; replace with consensus + circuit data in production."
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "TGNP API",
        "status": "operational",
        "model_loaded": model is not None,
        "guard_count": len(guard_fingerprints) if guard_fingerprints is not None else 0
    }


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_guard_nodes(request: PredictionRequest):
    """
    Predict probable guard nodes for a given exit event
    
    Returns top-K ranked predictions with confidence scores and explainability
    """
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    start_time = time.time()
    
    try:
        # Engineer features
        X = engineer_features(request)
        
        # Get predictions
        probabilities = model.predict_proba(X)
        
        # Extract top-10 predictions
        predictions = get_top_k_predictions(probabilities, k=10)
        
        # Get feature importance for explainability
        top_features = get_feature_importance(model, X, top_n=5)
        
        # Calculate prediction time
        prediction_time_ms = (time.time() - start_time) * 1000
        
        return PredictionResponse(
            predictions=predictions,
            prediction_time_ms=round(prediction_time_ms, 2),
            model_version="1.0.0-xgboost",
            explainability={
                "top_features": [f.dict() for f in top_features],
                "total_features": len(feature_columns),
                "model_type": "XGBoost Multi-Class Classifier"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/api/model/info")
async def model_info():
    """Get model metadata and statistics"""
    return {
        "model_type": "XGBoost",
        "num_classes": len(guard_fingerprints) if guard_fingerprints else 0,
        "num_features": len(feature_columns) if feature_columns else 0,
        "feature_list": feature_columns if feature_columns else [],
        "version": "1.0.0"
    }


@app.get("/api/topology", response_model=TopologyResponse)
async def topology(limit: int = 40):
    """Return a synthetic relay interaction topology for visualization.

    Query Parameters:
      limit: approximate max nodes (guard + middle + exit groups)
    """
    if limit < 10:
        raise HTTPException(status_code=400, detail="limit must be >= 10")
    if limit > 150:
        raise HTTPException(status_code=400, detail="limit too large for demo (<=150)")

    topo = generate_topology(limit=limit)
    return topo


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
