# eda_tor_circuits.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

pd.set_option('display.width', 160)
pd.set_option('display.max_columns', 200)

def load_dataset(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Parse timestamps to datetime
    for col in ['timestamp', 'build_time']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    # Enforce numeric where expected
    numeric_cols = ['guard_bandwidth', 'middle_bandwidth', 'exit_bandwidth',
                    'circuit_setup_duration', 'total_bytes']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def basic_overview(df: pd.DataFrame):
    print("\n=== Dataset Overview ===")
    print(f"Rows: {len(df)}, Columns: {df.shape[1]}")
    print("\nColumns:", list(df.columns))
    print("\nDtypes:\n", df.dtypes)
    print("\nHead:\n", df.head(10))
    print("\nTail:\n", df.tail(10))

def quality_checks(df: pd.DataFrame):
    print("\n=== Missing Values per Column ===")
    print(df.isna().sum().sort_values(ascending=False))
    if 'circuit_id' in df.columns:
        dup = df.duplicated(subset=['circuit_id']).sum()
        print(f"\nDuplicate circuit_id count: {dup}")
    else:
        print("\nNo circuit_id column found for duplicate check.")

def categorical_profile(df: pd.DataFrame):
    cat_cols = ['status', 'purpose', 'guard_country', 'middle_country', 'exit_country',
                'guard_fingerprint', 'middle_fingerprint', 'exit_fingerprint',
                'guard_nickname', 'middle_nickname', 'exit_nickname']
    print("\n=== Categorical Cardinalities ===")
    for col in cat_cols:
        if col in df.columns:
            nunique = df[col].nunique(dropna=True)
            top = df[col].value_counts(dropna=True).head(5)
            print(f"\n{col}: unique={nunique}")
            print(top)

def derive_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    # Time delta between build and timestamp
    if {'timestamp','build_time'}.issubset(out.columns):
        out['build_to_stamp_secs'] = (out['timestamp'] - out['build_time']).dt.total_seconds()
    # Bandwidth ratios
    if {'guard_bandwidth','exit_bandwidth'}.issubset(out.columns):
        out['guard_exit_bw_ratio'] = out['guard_bandwidth'] / out['exit_bandwidth'].replace({0: np.nan})
    if {'middle_bandwidth','exit_bandwidth'}.issubset(out.columns):
        out['middle_exit_bw_ratio'] = out['middle_bandwidth'] / out['exit_bandwidth'].replace({0: np.nan})
    # Bytes per second proxy
    if {'total_bytes','circuit_setup_duration'}.issubset(out.columns):
        out['bytes_per_setup_sec'] = out['total_bytes'] / out['circuit_setup_duration'].replace({0: np.nan})
    # Hour of day and day of week for temporal patterns
    if 'timestamp' in out.columns:
        out['hour'] = out['timestamp'].dt.hour
        out['dow'] = out['timestamp'].dt.dayofweek
    return out

def numeric_distributions(df: pd.DataFrame, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    num_cols = ['guard_bandwidth','middle_bandwidth','exit_bandwidth',
                'circuit_setup_duration','total_bytes','build_to_stamp_secs',
                'guard_exit_bw_ratio','middle_exit_bw_ratio','bytes_per_setup_sec']
    num_cols = [c for c in num_cols if c in df.columns]
    for col in num_cols:
        plt.figure(figsize=(8,4))
        sns.histplot(df[col].dropna(), bins=50, kde=True)
        plt.title(f'Distribution of {col}')
        plt.xlabel(col)
        plt.tight_layout()
        plt.savefig(outdir / f'dist_{col}.png', dpi=160)
        plt.close()

def correlation_heatmap(df: pd.DataFrame, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    num_df = df.select_dtypes(include=[np.number]).copy()
    if num_df.shape[1] >= 2:
        corr = num_df.corr(numeric_only=True)
        plt.figure(figsize=(10,8))
        sns.heatmap(corr, cmap='vlag', center=0, annot=False, linewidths=0.3)
        plt.title('Correlation Heatmap (Numeric Features)')
        plt.tight_layout()
        plt.savefig(outdir / 'corr_heatmap.png', dpi=160)
        plt.close()

def temporal_profiles(df: pd.DataFrame, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    if 'timestamp' in df.columns:
        ts = df.set_index('timestamp').sort_index()
        res = ts['total_bytes'].resample('1T').sum().rename('bytes_per_min') if 'total_bytes' in ts.columns else None
        if res is not None and res.notna().any():
            plt.figure(figsize=(10,4))
            res.plot()
            plt.title('Total Bytes per Minute')
            plt.ylabel('bytes_per_min')
            plt.tight_layout()
            plt.savefig(outdir / 'bytes_per_min.png', dpi=160)
            plt.close()
        if 'hour' in df.columns:
            plt.figure(figsize=(8,4))
            sns.countplot(x='hour', data=df)
            plt.title('Circuit Counts by Hour of Day')
            plt.tight_layout()
            plt.savefig(outdir / 'counts_by_hour.png', dpi=160)
            plt.close()

def main():
    csv_path = r'C:\Users\zhagh\OneDrive\Desktop\phack253\data\circuit_data_20251120_221959.csv'  # change to your CSV filename
    outdir = Path('eda_outputs')
    df = load_dataset(csv_path)
    basic_overview(df)
    quality_checks(df)
    categorical_profile(df)
    df2 = derive_features(df)
    numeric_distributions(df2, outdir)
    correlation_heatmap(df2, outdir)
    temporal_profiles(df2, outdir)
    print(f"\nEDA figures saved under: {outdir.resolve()}")

if __name__ == '__main__':
    main()