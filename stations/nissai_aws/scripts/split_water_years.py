#!/usr/bin/env python3
"""Split the combined Nissai record into water-year files.

Water year N runs 1 October (N-1) to 30 September (N) - the convention for
snow and hydrology, and it also matches the early-September download campaigns,
so each file closes just after the card is pulled.

    python3 split_water_years.py combined_meteodata2026.csv data/water_years
"""
import sys, os
import pandas as pd, warnings
warnings.filterwarnings('ignore')

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)

df = pd.read_csv(src, low_memory=False)
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
df = df.dropna(subset=['TIMESTAMP']).sort_values('TIMESTAMP')

wy = df.TIMESTAMP.dt.year + (df.TIMESTAMP.dt.month >= 10).astype(int)
print(f'{len(df):,} records  {df.TIMESTAMP.min()} -> {df.TIMESTAMP.max()}\n')
print(f'{"file":34s} {"records":>9s} {"MB":>6s}  period')
total = 0
for y, g in df.groupby(wy):
    out = os.path.join(outdir, f'nissai_meteodata_WY{y}.csv')
    g2 = g.copy()
    g2['TIMESTAMP'] = g2['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M:%S')
    g2.to_csv(out, index=False)
    mb = os.path.getsize(out) / 1e6
    total += mb
    print(f'{os.path.basename(out):34s} {len(g):9,d} {mb:6.1f}  '
          f'{g.TIMESTAMP.min():%Y-%m-%d} -> {g.TIMESTAMP.max():%Y-%m-%d}')
print(f'\n{total:.1f} MB across {wy.nunique()} files (largest well under any git limit)')
