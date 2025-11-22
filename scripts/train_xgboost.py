"""
XGBoost Multi-Class Classifier for Guard Node Prediction
Optimized for Top-K accuracy and MRR metrics
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, top_k_accuracy_score, classification_report
from pathlib import Path
import pickle
import json
import time
import warnings
warnings.filterwarnings('ignore')

def calculate_mrr(y_true, y_pred_proba, k=50):
    """
    Calculate Mean Reciprocal Rank
    MRR measures ranking quality - higher is better
    """
    mrr = 0
    for i, true_label in enumerate(y_true):
        # Get top-k predictions (highest probabilities)
        top_k_indices = np.argsort(y_pred_proba[i])[::-1][:k]
        
        # Find rank of true label
        if true_label in top_k_indices:
            rank = np.where(top_k_indices == true_label)[0][0] + 1
            mrr += 1.0 / rank
    
    return mrr / len(y_true)


def evaluate_topk(y_true, y_pred_proba, k_values=[1, 3, 5, 10, 20, 50]):
    """Calculate Top-K accuracies"""
    results = {}
    
    for k in k_values:
        if k == 1:
            # Top-1 is standard accuracy
            y_pred = np.argmax(y_pred_proba, axis=1)
            acc = accuracy_score(y_true, y_pred)
        else:
            acc = top_k_accuracy_score(y_true, y_pred_proba, k=k, labels=np.arange(y_pred_proba.shape[1]))
        
        results[f'Top-{k}'] = acc
    
    return results


def train_xgboost_model(X_train, y_train, X_val, y_val, n_classes):
    """Train XGBoost multi-class classifier"""
    
    print("\n" + "="*80)
    print(" TRAINING XGBOOST MODEL")
    print("="*80)
    print(f"\nTraining Configuration:")
    print(f"  Training samples: {len(X_train):,}")
    print(f"  Validation samples: {len(X_val):,}")
    print(f"  Number of classes (guards): {n_classes}")
    print(f"  Number of features: {X_train.shape[1]}")
    
    # XGBoost parameters optimized for multi-class ranking
    params = {
        'objective': 'multi:softprob',  # Output probabilities for ranking
        'num_class': n_classes,
        'eval_metric': 'mlogloss',
        'max_depth': 10,
        'learning_rate': 0.1,
        'n_estimators': 300,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 3,
        'gamma': 0.1,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'tree_method': 'hist',
        'random_state': 42,
        'n_jobs': -1,
        'early_stopping_rounds': 20
    }
    
    print("\nXGBoost Hyperparameters:")
    for key, value in params.items():
        print(f"  {key:20s}: {value}")
    
    # Initialize model
    model = xgb.XGBClassifier(**params)
    
    # Train with early stopping
    print("\nTraining in progress...")
    start_time = time.time()
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train), (X_val, y_val)],
        verbose=50
    )
    
    training_time = time.time() - start_time
    
    print(f"\n✓ Training complete!")
    print(f"  Training time: {training_time:.2f} seconds ({training_time/60:.2f} minutes)")
    print(f"  Best iteration: {model.best_iteration}")
    print(f"  Best validation score: {model.best_score:.4f}")
    
    return model


def main():
    print("="*80)
    print(" TOR GUARD PREDICTION - XGBOOST TRAINING PIPELINE")
    print("="*80)
    print()
    
    # Load engineered dataset
    data_path = Path("data/circuit_data_engineered.csv")
    
    if not data_path.exists():
        print(f"❌ Error: Engineered dataset not found at {data_path}")
        print("Please run: python scripts/prepare_features.py first")
        exit(1)
    
    df = pd.read_csv(data_path)
    print(f"✓ Loaded dataset: {len(df):,} samples, {df.shape[1]} columns")
    
    # Define feature columns (exclude identifiers and target)
    exclude_cols = [
        'request_id', 'circuit_id', 'timestamp', 'build_time', 'status', 'purpose',
        'guard_fingerprint', 'guard_nickname', 'guard_address', 'guard_country',
        'middle_fingerprint', 'middle_nickname', 'middle_address', 'middle_country',
        'exit_fingerprint', 'exit_nickname', 'exit_address', 'exit_country',
        'guard_label'  # This is our target
    ]
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    print(f"\nFeature columns ({len(feature_cols)}):")
    for i, col in enumerate(feature_cols, 1):
        print(f"  {i:2d}. {col}")
    
    # Prepare data
    X = df[feature_cols]
    y = df['guard_label']
    n_classes = df['guard_label'].nunique()
    
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {len(X):,}")
    print(f"  Number of guards (classes): {n_classes}")
    print(f"  Samples per guard (avg): {len(X)/n_classes:.1f}")
    
    # Check for missing values
    if X.isnull().sum().sum() > 0:
        print("\n⚠ Warning: Missing values detected!")
        print(X.isnull().sum()[X.isnull().sum() > 0])
        print("Filling missing values with 0...")
        X = X.fillna(0)
    
    # Train/Val/Test split (70/15/15)
    print("\nSplitting data...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp  # 0.176 * 0.85 ≈ 0.15
    )
    
    print(f"\nData Split:")
    print(f"  Train: {len(X_train):,} samples ({len(X_train)/len(X)*100:.1f}%)")
    print(f"  Val:   {len(X_val):,} samples ({len(X_val)/len(X)*100:.1f}%)")
    print(f"  Test:  {len(X_test):,} samples ({len(X_test)/len(X)*100:.1f}%)")
    
    # Train model
    model = train_xgboost_model(X_train, y_train, X_val, y_val, n_classes)
    
    # Evaluate on test set
    print("\n" + "="*80)
    print(" MODEL EVALUATION ON TEST SET")
    print("="*80)
    
    print("\nGenerating predictions...")
    y_pred_proba = model.predict_proba(X_test)
    y_pred = np.argmax(y_pred_proba, axis=1)
    
    # Top-K accuracies
    topk_results = evaluate_topk(y_test, y_pred_proba, k_values=[1, 3, 5, 10, 20, 50, 100])
    
    print("\n📊 Top-K Accuracy Results:")
    print("-" * 40)
    for metric, score in topk_results.items():
        print(f"  {metric:12s}: {score*100:6.2f}%")
    
    # MRR
    print("\nCalculating Mean Reciprocal Rank...")
    mrr = calculate_mrr(y_test.values, y_pred_proba, k=50)
    print(f"\n🎯 Mean Reciprocal Rank (MRR@50): {mrr:.4f}")
    print(f"   (Higher is better, range: 0-1)")
    
    # Feature importance
    print("\n📈 Top 20 Most Important Features:")
    print("-" * 60)
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for i, row in feature_importance.head(20).iterrows():
        print(f"  {i+1:2d}. {row['feature']:40s}: {row['importance']:.4f}")
    
    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "xgboost_guard_predictor.json"
    model.save_model(model_path)
    print(f"\n✓ Model saved: {model_path}")
    
    # Save feature columns for inference
    feature_cols_path = model_dir / "feature_columns.pkl"
    with open(feature_cols_path, 'wb') as f:
        pickle.dump(feature_cols, f)
    print(f"✓ Feature columns saved: {feature_cols_path}")
    
    # Save feature importance
    feature_importance.to_csv(model_dir / "feature_importance.csv", index=False)
    print(f"✓ Feature importance saved: {model_dir / 'feature_importance.csv'}")
    
    # Save evaluation metrics
    metrics = {
        'topk_accuracy': {k: float(v) for k, v in topk_results.items()},
        'mrr': float(mrr),
        'n_classes': int(n_classes),
        'n_features': len(feature_cols),
        'train_samples': len(X_train),
        'val_samples': len(X_val),
        'test_samples': len(X_test),
        'best_iteration': int(model.best_iteration),
        'hyperparameters': {
            'max_depth': 10,
            'learning_rate': 0.1,
            'n_estimators': 300,
            'subsample': 0.8,
            'colsample_bytree': 0.8
        }
    }
    
    metrics_path = model_dir / "evaluation_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Metrics saved: {metrics_path}")
    
    # Print summary
    print("\n" + "="*80)
    print(" TRAINING COMPLETE - SUMMARY")
    print("="*80)
    print(f"\n✓ Model: XGBoost Multi-Class Classifier")
    print(f"✓ Classes: {n_classes} guards")
    print(f"✓ Features: {len(feature_cols)}")
    print(f"✓ Top-1 Accuracy: {topk_results['Top-1']*100:.2f}%")
    print(f"✓ Top-5 Accuracy: {topk_results['Top-5']*100:.2f}%")
    print(f"✓ Top-10 Accuracy: {topk_results['Top-10']*100:.2f}%")
    print(f"✓ MRR@50: {mrr:.4f}")
    
    print("\n📁 Saved Files:")
    print(f"  • {model_path}")
    print(f"  • {feature_cols_path}")
    print(f"  • {metrics_path}")
    print(f"  • {model_dir / 'feature_importance.csv'}")
    
    print("\n🚀 Next Steps:")
    print("  1. Review feature importance to understand predictions")
    print("  2. Test model with: python scripts/predict_guard.py")
    print("  3. (Optional) Optimize hyperparameters: python scripts/optimize_hyperparameters.py")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
