import pandas as pd

# Load the data
df = pd.read_csv('data/circuit_data_20251119_230754.csv')

# Analyze full circuit paths
full = df[['guard_fingerprint', 'middle_fingerprint', 'exit_fingerprint']]
guard_exit = df[['guard_fingerprint', 'exit_fingerprint']]

print('=== ULTRA-MASSIVE DATASET: 1000 Guards x 1000 Middles x 1000 Exits ===\n')
print(f'Total Circuits: {len(df):,}')
print(f'Network Size: 1,000 Guards x 1,000 Middles x 1,000 Exits\n')

print('FULL CIRCUIT PATHS (Guard-Middle-Exit):')
unique_paths = full.drop_duplicates().shape[0]
print(f'  Unique paths: {unique_paths:,}')
print(f'  Duplicates: {len(df) - unique_paths:,}')
print(f'  Uniqueness: {unique_paths/len(df)*100:.2f}%')

dup_count = full.groupby(list(full.columns)).size()
print(f'  Max repeats: {dup_count.max()} times')

print(f'\nGUARD-EXIT PAIRS:')
print(f'  Unique pairs: {guard_exit.drop_duplicates().shape[0]:,}')

print(f'\nINDIVIDUAL NODE USAGE:')
print(f'  Guards used: {df["guard_fingerprint"].nunique():,} / 1,000')
print(f'  Middles used: {df["middle_fingerprint"].nunique():,} / 1,000')
print(f'  Exits used: {df["exit_fingerprint"].nunique():,} / 1,000')

print(f'\n=== PERFECT FOR ML TRAINING ===')
if unique_paths == len(df):
    print('✓ 100% UNIQUE CIRCUITS - ZERO DUPLICATES!')
else:
    print(f'  {unique_paths/len(df)*100:.1f}% unique circuits')
