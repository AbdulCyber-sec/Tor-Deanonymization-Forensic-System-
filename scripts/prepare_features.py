"""
Feature Engineering for TOR Guard Prediction
Generates ML-ready dataset with ~40 features (WITHOUT temporal features)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
import pickle
import warnings
warnings.filterwarnings('ignore')

def engineer_features(df):
    """Apply all feature engineering transformations"""
    
    print("Starting feature engineering...")
    print(f"Input shape: {df.shape}")
    
    # A. Bandwidth features (7 features)
    print("\n[1/5] Creating bandwidth features...")
    df['bw_ratio_guard_middle'] = df['guard_bandwidth'] / (df['middle_bandwidth'] + 1)
    df['bw_ratio_guard_exit'] = df['guard_bandwidth'] / (df['exit_bandwidth'] + 1)
    df['bw_ratio_middle_exit'] = df['middle_bandwidth'] / (df['exit_bandwidth'] + 1)
    df['bw_total'] = df['guard_bandwidth'] + df['middle_bandwidth'] + df['exit_bandwidth']
    df['bw_min'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].min(axis=1)
    df['bw_max'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].max(axis=1)
    df['bw_std'] = df[['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth']].std(axis=1)
    
    # B. Geographic features (5 features)
    print("[2/5] Creating geographic features...")
    df['same_country_guard_middle'] = (df['guard_country'] == df['middle_country']).astype(int)
    df['same_country_guard_exit'] = (df['guard_country'] == df['exit_country']).astype(int)
    df['same_country_middle_exit'] = (df['middle_country'] == df['exit_country']).astype(int)
    df['all_same_country'] = ((df['guard_country'] == df['middle_country']) & 
                               (df['guard_country'] == df['exit_country'])).astype(int)
    df['country_diversity'] = df[['guard_country', 'middle_country', 'exit_country']].nunique(axis=1)
    
    # C. Historical/Aggregate features (8 features)
    print("[3/5] Creating historical aggregate features...")
    
    # Usage frequencies
    guard_freq = df['guard_fingerprint'].value_counts().to_dict()
    df['guard_usage_freq'] = df['guard_fingerprint'].map(guard_freq)
    
    middle_freq = df['middle_fingerprint'].value_counts().to_dict()
    exit_freq = df['exit_fingerprint'].value_counts().to_dict()
    df['middle_usage_freq'] = df['middle_fingerprint'].map(middle_freq)
    df['exit_usage_freq'] = df['exit_fingerprint'].map(exit_freq)
    
    # Guard-Exit pair frequency (VERY IMPORTANT for prediction!)
    pair_freq = df.groupby(['guard_fingerprint', 'exit_fingerprint']).size().to_dict()
    df['guard_exit_pair_freq'] = df.apply(
        lambda x: pair_freq.get((x['guard_fingerprint'], x['exit_fingerprint']), 0), axis=1
    )
    
    # Average bandwidth by guard
    guard_avg_bw = df.groupby('guard_fingerprint')['guard_bandwidth'].mean().to_dict()
    df['guard_avg_bandwidth'] = df['guard_fingerprint'].map(guard_avg_bw)
    
    # Guard-Middle pair frequency
    guard_middle_freq = df.groupby(['guard_fingerprint', 'middle_fingerprint']).size().to_dict()
    df['guard_middle_pair_freq'] = df.apply(
        lambda x: guard_middle_freq.get((x['guard_fingerprint'], x['middle_fingerprint']), 0), axis=1
    )
    
    # Country preference score
    guard_country_pref = df.groupby(['guard_fingerprint', 'exit_country']).size()
    guard_country_pref = guard_country_pref.reset_index(name='count')
    guard_top_country = guard_country_pref.sort_values('count', ascending=False).groupby('guard_fingerprint')['exit_country'].first().to_dict()
    df['guard_prefers_exit_country'] = (df.apply(
        lambda x: x['exit_country'] == guard_top_country.get(x['guard_fingerprint'], ''), axis=1
    )).astype(int)
    
    # D. Label Encoding (5 features)
    print("[4/5] Encoding categorical features...")
    encoders = {}
    
    # Encode fingerprints and countries
    for col in ['middle_fingerprint', 'exit_fingerprint', 
                'guard_country', 'middle_country', 'exit_country']:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col])
        encoders[col] = le
    
    # Target encoding (THIS IS OUR PREDICTION TARGET)
    le_target = LabelEncoder()
    df['guard_label'] = le_target.fit_transform(df['guard_fingerprint'])
    encoders['guard_fingerprint'] = le_target
    
    print(f"  Encoded {len(encoders)} categorical variables")
    print(f"  Target classes: {df['guard_label'].nunique()}")
    
    # E. Interaction features (2 features)
    print("[5/5] Creating interaction features...")
    df['bw_guard_x_setup'] = df['guard_bandwidth'] * df['circuit_setup_duration']
    df['bw_total_x_bytes'] = df['bw_total'] * df['total_bytes']
    
    print(f"\n✓ Feature engineering complete!")
    print(f"  Output shape: {df.shape}")
    print(f"  New features created: {df.shape[1] - 23}")
    
    return df, encoders


if __name__ == "__main__":
    print("="*80)
    print(" TOR GUARD PREDICTION - FEATURE ENGINEERING")
    print("="*80)
    print()
    
    # Load raw data
    data_path = Path("data/circuit_data_20251120_221959.csv")
    
    if not data_path.exists():
        print(f"❌ Error: Dataset not found at {data_path}")
        print("Please ensure the circuit data file exists.")
        exit(1)
    
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df):,} circuits with {df.shape[1]} raw features")
    
    # Engineer features
    df_engineered, encoders = engineer_features(df)
    
    # Save processed dataset
    output_path = Path("data/circuit_data_engineered.csv")
    output_path.parent.mkdir(exist_ok=True)
    df_engineered.to_csv(output_path, index=False)
    print(f"\n✓ Saved engineered dataset: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024**2:.2f} MB")
    
    # Save encoders for inference
    encoder_path = Path("models/encoders.pkl")
    encoder_path.parent.mkdir(exist_ok=True)
    with open(encoder_path, 'wb') as f:
        pickle.dump(encoders, f)
    print(f"✓ Saved {len(encoders)} encoders: {encoder_path}")
    
    # Print feature summary
    print("\n" + "="*80)
    print(" FEATURE SUMMARY")
    print("="*80)
    
    feature_categories = {
        'Bandwidth Features': 7,
        'Geographic Features': 5,
        'Historical/Aggregate Features': 8,
        'Encoded Categorical Features': 5,
        'Interaction Features': 2,
        'Target Variable': 1
    }
    
    print("\nFeature Breakdown:")
    total_new = 0
    for category, count in feature_categories.items():
        print(f"  {category:35s}: {count:2d} features")
        if category != 'Target Variable':
            total_new += count
    
    print(f"\n  Total new features: {total_new}")
    print(f"  Original features: 23")
    print(f"  Final feature count: {df_engineered.shape[1]}")
    
    print("\n✓ Feature engineering pipeline complete!")
    print("  Next step: python scripts/train_xgboost.py")
