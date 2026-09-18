#!/usr/bin/env python3
"""Append a season of converted Meteodata_Entire TOA5 files onto the combined
archive.

    python3 build_combined.py <toa5_dir> <archive_in.csv> <archive_out.csv>

Raw values are preserved (sensor error codes included) to match the existing
archive; physical filtering belongs in the QC step, not here.
"""
import sys, glob, os, warnings
import pandas as pd
warnings.filterwarnings('ignore')

src, old_csv, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]

old = pd.read_csv(old_csv, low_memory=False)
old['TIMESTAMP'] = pd.to_datetime(old['TIMESTAMP'], errors='coerce')
print(f'archive : {len(old):,} rows  {old.TIMESTAMP.min()} -> {old.TIMESTAMP.max()}')

frames = []
for p in sorted(glob.glob(os.path.join(src, 'TOA5_Meteodata_Entire_*.dat'))):
    try:
        d = pd.read_csv(p, skiprows=[0, 2, 3], header=0, na_values=['NAN'], low_memory=False)
    except Exception:
        continue
    if len(d): frames.append(d)
new = pd.concat(frames, ignore_index=True)
new['TIMESTAMP'] = pd.to_datetime(new['TIMESTAMP'], errors='coerce')
new = new.dropna(subset=['TIMESTAMP'])

# Torn records recovered at ring-buffer run boundaries read near-zero absolute
# pressure, which is impossible at 3909 m.
p = pd.to_numeric(new.PressureBarometricAbsolute, errors='coerce')
torn = ~p.between(500, 800)
if torn.any(): print(f'dropping {int(torn.sum())} torn record(s)')
new = new[~torn]
new = new[(new.TIMESTAMP > '2025-01-01') & (new.TIMESTAMP < '2027-01-01')]
print(f'new     : {len(new):,} rows  {new.TIMESTAMP.min()} -> {new.TIMESTAMP.max()}')

if list(old.columns) != list(new.columns):
    sys.exit('column mismatch - refusing to append')

overlap = set(old.TIMESTAMP) & set(new.TIMESTAMP)
print(f'overlapping timestamps: {len(overlap):,}')

comb = pd.concat([old, new], ignore_index=True)
comb = comb.drop_duplicates('TIMESTAMP', keep='first').sort_values('TIMESTAMP')
print(f'combined: {len(comb):,} rows  {comb.TIMESTAMP.min()} -> {comb.TIMESTAMP.max()}')

comb['TIMESTAMP'] = comb['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M:%S')
comb.to_csv(out_csv, index=False)
print(f'wrote {out_csv}  ({os.path.getsize(out_csv)/1e6:.1f} MB)')
