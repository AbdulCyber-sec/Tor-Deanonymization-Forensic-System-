"""
Prediction Script for TOR Guard Node Ranking
Loads trained model and predicts top-K guards for new circuit data
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from pathlib import Path
import pickle
import json

def load_model_and_artifacts():
    """Load trained model, encoders, and feature columns"""
    
    model_dir = Path("models")
    
    # Load model
    model = xgb.XGBClassifier()
    model.load_model(model_dir / "xgboost_guard_predictor.json")
    
    # Load encoders
    with open(model_dir / "encoders.pkl", 'rb') as f:
        encoders = pickle.load(f)
    
    # Load feature columns
    with open(model_dir / "feature_columns.pkl", 'rb') as f:
        feature_cols = pickle.load(f)
    
    return model, encoders, feature_cols


def predict_top_k_guards(circuit_data, model, encoders, feature_cols, k=10):
    """
    Predict top-K most likely guards for circuit data
    
    Args:
        circuit_data: DataFrame with circuit information
        model: Trained XGBoost model
        encoders: Dictionary of label encoders
        feature_cols: List of feature column names
        k: Number of top predictions to return
    
    Returns:
        DataFrame with top-K guard predictions and probabilities
    """
    
    # Prepare features (same engineering as training)
    df = circuit_data.copy()
    
    # Feature engineering
    df['bw_ratio_guard_middle'] = df['guard_bandwidth'] / (df['middle_bandwidth'] + 1)
    df['bw_ratio_guard_exit'] = df['guard_bandwidth'] / (df['exit_bandwidth'] + 1)
    df['bw_ratio_middle_exit'] = df['middle_bandwidth'] / (df['exit_bandwidth'] + 1)
    df['bw_total'] = df['guard_bandwidth'] + df['middle_bandwidth'] + df['exit_bandwidth']
    df['bw_min'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].min(axis=1)
    df['bw_max'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].max(axis=1)
    df['bw_std'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].std(axis=1)
    
    # Geographic features
    df['same_country_guard_middle'] = (df['guard_country'] == df['middle_country']).astype(int)
    df['same_country_guard_exit'] = (df['guard_country'] == df['exit_country']).astype(int)
    df['same_country_middle_exit'] = (df['middle_country'] == df['exit_country']).astype(int)
    df['all_same_country'] = ((df['guard_country'] == df['middle_country']) & 
                               (df['guard_country'] == df['exit_country'])).astype(int)
    df['country_diversity'] = df[['guard_country', 'middle_country', 'exit_country']].nunique(axis=1)
    
    # Encoding
    for col in ['middle_fingerprint', 'exit_fingerprint', 'guard_country', 'middle_country', 'exit_country']:
        le = encoders[col]
        df[f'{col}_encoded'] = le.transform(df[col])
    
    # Interaction features
    df['bw_guard_x_setup'] = df['guard_bandwidth'] * df['circuit_setup_duration']
    df['bw_total_x_bytes'] = df['bw_total'] * df['total_bytes']
    
    # Select features
    X = df[feature_cols].fillna(0)
    
    # Predict probabilities
    probabilities = model.predict_proba(X)
    
    # Get top-K predictions
    results = []
    guard_encoder = encoders['guard_fingerprint']
    
    for i in range(len(X)):
        top_k_indices = np.argsort(probabilities[i])[::-1][:k]
        top_k_probs = probabilities[i][top_k_indices]
        top_k_guards = guard_encoder.inverse_transform(top_k_indices)
        
        results.append({
            'circuit_id': circuit_data.iloc[i]['circuit_id'],
            'top_k_guards': top_k_guards.tolist(),
            'top_k_probabilities': top_k_probs.tolist()
        })
    
    return pd.DataFrame(results)


if __name__ == "__main__":
    print("="*80)
    print(" TOR GUARD PREDICTION - INFERENCE")
    print("="*80)
    print()
    
    # Load model
    print("Loading model and artifacts...")
    model, encoders, feature_cols = load_model_and_artifacts()
    print(f"✓ Model loaded with {len(feature_cols)} features")
    print(f"✓ {len(encoders)} encoders loaded")
    
    # Load evaluation metrics
    with open("models/evaluation_metrics.json", 'r') as f:
        metrics = json.load(f)
    
    print(f"\nModel Performance:")
    print(f"  Top-1 Accuracy: {metrics['topk_accuracy']['Top-1']*100:.2f}%")
    print(f"  Top-5 Accuracy: {metrics['topk_accuracy']['Top-5']*100:.2f}%")
    print(f"  MRR: {metrics['mrr']:.4f}")
    
    # Example: Predict on test data
    print("\n" + "="*80)
    print(" EXAMPLE PREDICTION")
    print("="*80)
    
    # Load some test data
    df = pd.read_csv("data/circuit_data_engineered.csv")
    sample = df.sample(5, random_state=42)
    
    # Predict
    predictions = predict_top_k_guards(sample, model, encoders, feature_cols, k=5)
    
    print("\nTop-5 Guard Predictions:")
    for idx, row in predictions.iterrows():
        print(f"\nCircuit {row['circuit_id']}:")
        for i, (guard, prob) in enumerate(zip(row['top_k_guards'], row['top_k_probabilities']), 1):
            print(f"  {i}. {guard[:16]}... (probability: {prob:.4f})")
    
    print("\n✓ Prediction complete!")
