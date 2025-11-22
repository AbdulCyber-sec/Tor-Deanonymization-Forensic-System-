"""
Comprehensive EDA and Feature Engineering for TOR Guard Prediction
Analyzes circuit_data_20251120_221959.csv with 25,000 circuits and 500 guards
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print(" TOR GUARD PREDICTION: EXPLORATORY DATA ANALYSIS & FEATURE ENGINEERING")
print("="*80)
print()

# ============================================================================
# 1. DATA LOADING & INITIAL INSPECTION
# ============================================================================
print("📊 STEP 1: DATA LOADING & INITIAL INSPECTION")
print("-" * 80)

data_path = Path("data/circuit_data_20251120_221959.csv")
df = pd.read_csv(data_path)

print(f"✓ Loaded dataset: {data_path.name}")
print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print()

# Basic info
print("Dataset Structure:")
print(df.dtypes)
print()

print("First 3 rows:")
print(df.head(3))
print()

# ============================================================================
# 2. MISSING VALUES & DATA QUALITY
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 2: DATA QUALITY ASSESSMENT")
print("-" * 80)

missing = df.isnull().sum()
if missing.sum() == 0:
    print("✓ No missing values detected")
else:
    print("⚠ Missing values found:")
    print(missing[missing > 0])
print()

# Check duplicates
duplicates = df.duplicated().sum()
print(f"Duplicate rows: {duplicates}")

# Check circuit path uniqueness
circuit_paths = df[['guard_fingerprint', 'middle_fingerprint', 'exit_fingerprint']].drop_duplicates()
print(f"Unique circuit paths: {len(circuit_paths):,} / {len(df):,} ({len(circuit_paths)/len(df)*100:.1f}%)")
print()

# ============================================================================
# 3. TARGET VARIABLE ANALYSIS (Guard Fingerprint)
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 3: TARGET VARIABLE ANALYSIS")
print("-" * 80)

target_col = 'guard_fingerprint'
n_guards = df[target_col].nunique()
print(f"Target: {target_col}")
print(f"Number of unique guards: {n_guards}")
print()

# Class distribution
guard_counts = df[target_col].value_counts()
print("Guard usage statistics:")
print(f"  Min circuits per guard: {guard_counts.min()}")
print(f"  Max circuits per guard: {guard_counts.max()}")
print(f"  Mean circuits per guard: {guard_counts.mean():.2f}")
print(f"  Median circuits per guard: {guard_counts.median():.0f}")
print(f"  Std deviation: {guard_counts.std():.2f}")
print()

# Check class imbalance
imbalance_ratio = guard_counts.max() / guard_counts.min()
print(f"Class imbalance ratio: {imbalance_ratio:.2f}:1")
if imbalance_ratio > 3:
    print("  ⚠ High imbalance detected - consider class weighting or SMOTE")
else:
    print("  ✓ Relatively balanced classes")
print()

# Top 10 most used guards
print("Top 10 most frequently used guards:")
for i, (guard, count) in enumerate(guard_counts.head(10).items(), 1):
    guard_nickname = df[df[target_col] == guard]['guard_nickname'].iloc[0]
    print(f"  {i:2d}. {guard_nickname}: {count} circuits ({count/len(df)*100:.2f}%)")
print()

# ============================================================================
# 4. FEATURE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 4: FEATURE ANALYSIS")
print("-" * 80)

# Categorical features
print("\n4.1 CATEGORICAL FEATURES")
print("-" * 40)

categorical_cols = ['guard_country', 'middle_country', 'exit_country', 'status', 'purpose']
for col in categorical_cols:
    if col in df.columns:
        n_unique = df[col].nunique()
        print(f"\n{col}:")
        print(f"  Unique values: {n_unique}")
        print(f"  Distribution:")
        for val, count in df[col].value_counts().head(5).items():
            print(f"    {val}: {count:,} ({count/len(df)*100:.1f}%)")

# Numeric features
print("\n\n4.2 NUMERIC FEATURES")
print("-" * 40)

numeric_cols = ['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth', 
                'circuit_setup_duration', 'total_bytes']

numeric_stats = df[numeric_cols].describe()
print(numeric_stats)
print()

# Check for outliers using IQR method
print("\nOutlier detection (IQR method):")
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
    print(f"  {col}: {outliers:,} outliers ({outliers/len(df)*100:.2f}%)")
print()

# ============================================================================
# 5. CORRELATION ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 5: CORRELATION ANALYSIS")
print("-" * 80)

# Compute correlation matrix for numeric features
corr_matrix = df[numeric_cols].corr()
print("\nCorrelation Matrix:")
print(corr_matrix.round(3))
print()

# Find highly correlated pairs
high_corr_pairs = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        if abs(corr_matrix.iloc[i, j]) > 0.7:
            high_corr_pairs.append((
                corr_matrix.columns[i], 
                corr_matrix.columns[j], 
                corr_matrix.iloc[i, j]
            ))

if high_corr_pairs:
    print("⚠ Highly correlated features (|r| > 0.7):")
    for feat1, feat2, corr in high_corr_pairs:
        print(f"  {feat1} <-> {feat2}: {corr:.3f}")
else:
    print("✓ No highly correlated feature pairs found")
print()

# ============================================================================
# 6. GEOGRAPHIC ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 6: GEOGRAPHIC DISTRIBUTION ANALYSIS")
print("-" * 80)

print("\nGuard country distribution:")
guard_countries = df['guard_country'].value_counts()
for country, count in guard_countries.head(10).items():
    print(f"  {country}: {count:,} circuits ({count/len(df)*100:.1f}%)")
print()

# Cross-country patterns
print("\nTop 5 Guard-Exit country pairs:")
country_pairs = df.groupby(['guard_country', 'exit_country']).size().sort_values(ascending=False)
for (guard_c, exit_c), count in country_pairs.head(5).items():
    print(f"  {guard_c} → {exit_c}: {count:,} circuits")
print()

# Geographic diversity score
def calculate_diversity(df, prefix):
    """Calculate geographic diversity (entropy)"""
    country_col = f'{prefix}_country'
    probs = df[country_col].value_counts(normalize=True)
    entropy = -np.sum(probs * np.log2(probs))
    max_entropy = np.log2(len(probs))
    diversity_score = entropy / max_entropy if max_entropy > 0 else 0
    return diversity_score

guard_diversity = calculate_diversity(df, 'guard')
middle_diversity = calculate_diversity(df, 'middle')
exit_diversity = calculate_diversity(df, 'exit')

print("Geographic diversity scores (0-1, higher = more diverse):")
print(f"  Guard nodes:  {guard_diversity:.3f}")
print(f"  Middle nodes: {middle_diversity:.3f}")
print(f"  Exit nodes:   {exit_diversity:.3f}")
print()

# ============================================================================
# 7. TEMPORAL ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 7: TEMPORAL PATTERN ANALYSIS")
print("-" * 80)

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['build_time'] = pd.to_datetime(df['build_time'])

# Time range
time_range = df['timestamp'].max() - df['timestamp'].min()
print(f"Time range: {time_range}")
print(f"Start: {df['timestamp'].min()}")
print(f"End: {df['timestamp'].max()}")
print()

# Circuit build time distribution
print("Circuit setup duration statistics:")
print(f"  Mean: {df['circuit_setup_duration'].mean():.3f} seconds")
print(f"  Median: {df['circuit_setup_duration'].median():.3f} seconds")
print(f"  Min: {df['circuit_setup_duration'].min():.3f} seconds")
print(f"  Max: {df['circuit_setup_duration'].max():.3f} seconds")
print()

# ============================================================================
# 8. FEATURE ENGINEERING RECOMMENDATIONS
# ============================================================================
print("\n" + "="*80)
print("🔧 STEP 8: FEATURE ENGINEERING STRATEGY")
print("-" * 80)

print("""
Recommended Feature Engineering Pipeline:

1. ENCODING FEATURES
   ✓ Label Encoding: guard_fingerprint (target), middle_fingerprint, exit_fingerprint
   ✓ One-Hot Encoding: guard_country, middle_country, exit_country
   ✓ Binary Encoding: status, purpose (if multiple values)

2. NUMERIC TRANSFORMATIONS
   ✓ Log transform: bandwidth features (reduce skewness)
   ✓ StandardScaler: circuit_setup_duration, total_bytes
   ✓ Normalization: All numeric features to [0,1] range

3. DERIVED FEATURES (Behavioral Patterns)
   ✓ bandwidth_ratio_guard_middle = guard_bandwidth / middle_bandwidth
   ✓ bandwidth_ratio_guard_exit = guard_bandwidth / exit_bandwidth
   ✓ total_path_bandwidth = guard_bandwidth + middle_bandwidth + exit_bandwidth
   ✓ min_path_bandwidth = min(guard, middle, exit bandwidth)
   ✓ max_path_bandwidth = max(guard, middle, exit bandwidth)
   ✓ bandwidth_variance = std([guard, middle, exit bandwidth])

4. GEOGRAPHIC FEATURES
   ✓ same_country_guard_middle (binary)
   ✓ same_country_guard_exit (binary)
   ✓ same_country_middle_exit (binary)
   ✓ all_same_country (binary)
   ✓ country_diversity_score (count unique countries in path)

5. AGGREGATE FEATURES (Historical Patterns)
   ✓ guard_usage_frequency (how often each guard is used)
   ✓ guard_avg_bandwidth (average bandwidth for guard's circuits)
   ✓ guard_exit_pair_frequency (how often this guard-exit pair occurs)
   ✓ guard_country_preference (guard's most common exit country)

6. INTERACTION FEATURES
   ✓ guard_fingerprint × middle_country
   ✓ guard_country × exit_country
   ✓ bandwidth_guard × setup_duration

7. TEMPORAL FEATURES
   ✓ hour_of_day (extract from timestamp)
   ✓ day_of_week (extract from timestamp)
   ✓ time_since_first_circuit (sequential ordering)

8. DIMENSIONALITY REDUCTION (Optional)
   ✓ PCA on bandwidth features (3 → 2 components)
   ✓ Target encoding for high-cardinality categoricals
""")
print()

# ============================================================================
# 9. PRELIMINARY FEATURE IMPORTANCE (Random Forest)
# ============================================================================
print("\n" + "="*80)
print("📊 STEP 9: PRELIMINARY FEATURE IMPORTANCE")
print("-" * 80)

print("\nTraining quick Random Forest to assess raw feature importance...")

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Prepare minimal feature set
feature_cols = [
    'middle_fingerprint', 'exit_fingerprint',
    'guard_country', 'middle_country', 'exit_country',
    'guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth',
    'circuit_setup_duration', 'total_bytes'
]

# Encode categorical features
df_encoded = df.copy()
le_dict = {}
for col in ['guard_fingerprint', 'middle_fingerprint', 'exit_fingerprint', 
            'guard_country', 'middle_country', 'exit_country']:
    le = LabelEncoder()
    df_encoded[col] = le.fit_transform(df[col].astype(str))
    le_dict[col] = le

# Prepare data
X = df_encoded[feature_cols]
y = df_encoded['guard_fingerprint']

# Train on small sample for speed
sample_size = min(5000, len(X))
X_sample = X.sample(n=sample_size, random_state=42)
y_sample = y.loc[X_sample.index]

X_train, X_test, y_train, y_test = train_test_split(
    X_sample, y_sample, test_size=0.2, random_state=42, stratify=y_sample
)

rf = RandomForestClassifier(
    n_estimators=50,
    max_depth=10,
    random_state=42,
    n_jobs=-1,
    verbose=0
)

rf.fit(X_train, y_train)
accuracy = rf.score(X_test, y_test)

print(f"✓ Quick RF trained on {sample_size:,} samples")
print(f"  Test accuracy: {accuracy*100:.2f}%")
print()

# Feature importance
feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 10 Most Important Features (Raw):")
for i, row in feature_importance.head(10).iterrows():
    print(f"  {row['feature']:30s}: {row['importance']:.4f}")
print()

# ============================================================================
# 10. MODEL RECOMMENDATIONS
# ============================================================================
print("\n" + "="*80)
print("🎯 STEP 10: MODEL TRAINING RECOMMENDATIONS")
print("-" * 80)

print(f"""
DATASET SUMMARY
---------------
• Total circuits: {len(df):,}
• Unique guards: {n_guards}
• Samples per guard: ~{len(df)/n_guards:.1f} (avg)
• Class imbalance: {imbalance_ratio:.2f}:1
• Quick RF baseline: {accuracy*100:.2f}% accuracy

RECOMMENDED MODEL PIPELINE
---------------------------

1. DATA PREPROCESSING
   • Train/Val/Test split: 70/15/15
   • Stratified sampling by guard_fingerprint
   • Handle class imbalance with class_weight='balanced'

2. FEATURE ENGINEERING
   • Apply all 8 feature groups above (~50-60 features total)
   • Remove highly correlated features (|r| > 0.9)
   • Feature selection: Keep top 30-40 by importance

3. MODEL ARCHITECTURES (Priority Order)

   A. XGBoost (PRIMARY RECOMMENDATION)
      • Best for tabular data with categorical features
      • Handles class imbalance well
      • Expected accuracy: 50-60% Top-1, 75-85% Top-5
      
      Hyperparameters:
      - n_estimators: 300-500
      - max_depth: 8-12
      - learning_rate: 0.05-0.1
      - subsample: 0.8
      - colsample_bytree: 0.8
      - objective: 'multi:softmax'
      - eval_metric: 'mlogloss'
   
   B. LightGBM (ALTERNATIVE)
      • Faster training than XGBoost
      • Better with large feature spaces
      • Expected accuracy: 48-58% Top-1, 73-83% Top-5
      
      Hyperparameters:
      - num_leaves: 31-63
      - learning_rate: 0.05-0.1
      - feature_fraction: 0.8
      - bagging_fraction: 0.8
      - min_data_in_leaf: 20
   
   C. CatBoost (IF TIME PERMITS)
      • Best for high-cardinality categoricals
      • Auto handles categorical encoding
      • Expected accuracy: 52-62% Top-1, 76-86% Top-5

4. EVALUATION METRICS
   ✓ PRIMARY: Mean Reciprocal Rank (MRR)
   ✓ Top-K Accuracy (K=1, 3, 5, 10)
   ✓ Confusion Matrix (for top 20 guards)
   ✓ Per-class precision/recall/F1

5. OPTIMIZATION STRATEGY
   • Use Optuna for hyperparameter tuning
   • 5-fold cross-validation
   • Early stopping on validation loss
   • Feature importance analysis with SHAP

6. ENSEMBLE METHODS (ADVANCED)
   • Weighted voting: XGBoost (0.4) + LightGBM (0.3) + CatBoost (0.3)
   • Stacking: Use meta-learner on model predictions
   • Expected boost: +3-5% accuracy

EXPECTED PERFORMANCE
--------------------
With engineered features:
• Baseline (current RF):     {accuracy*100:.1f}%
• XGBoost (optimized):       50-60% Top-1, 75-85% Top-5
• LightGBM (optimized):      48-58% Top-1, 73-83% Top-5
• Ensemble (3 models):       55-65% Top-1, 78-88% Top-5

MRR Target: 0.65-0.75

TRAINING TIME ESTIMATES
-----------------------
• Feature engineering:       5-10 minutes
• XGBoost training:          15-20 minutes
• LightGBM training:         10-15 minutes
• Hyperparameter tuning:     1-2 hours (Optuna 50 trials)
• Total pipeline:            2-3 hours

NEXT STEPS
----------
1. Run feature_engineering.py script (creates processed dataset)
2. Train baseline XGBoost model
3. Evaluate with Top-K metrics and MRR
4. Hyperparameter optimization with Optuna
5. Generate SHAP explanations
6. Create prediction API for deployment
""")

print("\n" + "="*80)
print("✓ EDA COMPLETE - Ready for model development")
print("="*80)
print()

# Save summary statistics
output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

summary_stats = {
    'dataset_info': {
        'total_circuits': len(df),
        'unique_guards': n_guards,
        'unique_middles': df['middle_fingerprint'].nunique(),
        'unique_exits': df['exit_fingerprint'].nunique(),
        'unique_circuit_paths': len(circuit_paths),
        'time_range': str(time_range),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    },
    'target_stats': {
        'min_circuits_per_guard': int(guard_counts.min()),
        'max_circuits_per_guard': int(guard_counts.max()),
        'mean_circuits_per_guard': float(guard_counts.mean()),
        'class_imbalance_ratio': float(imbalance_ratio)
    },
    'feature_stats': {
        'numeric_features': len(numeric_cols),
        'categorical_features': len(categorical_cols),
        'baseline_accuracy': float(accuracy)
    },
    'diversity_scores': {
        'guard_diversity': float(guard_diversity),
        'middle_diversity': float(middle_diversity),
        'exit_diversity': float(exit_diversity)
    }
}

import json
summary_file = output_dir / 'eda_summary.json'
with open(summary_file, 'w') as f:
    json.dump(summary_stats, f, indent=2)

print(f"\n✓ Summary statistics saved to: {summary_file}")
print(f"\nReady to proceed with model training!")
