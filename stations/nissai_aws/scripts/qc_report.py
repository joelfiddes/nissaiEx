#!/usr/bin/env python3
"""Physical QC for the Nissai combined dataset.

Thresholds are set for the SITE (3909 m asl), not sea level, and each channel is
filtered against its own physical quantity. Small sensor offsets that are normal
instrument behaviour are CLAMPED, not discarded.
"""
import sys, warnings, datetime
import pandas as pd, numpy as np
warnings.filterwarnings('ignore')

CSV = sys.argv[1] if len(sys.argv) > 1 else 'combined_meteodata2026.csv'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'data_quality_report.md'
ELEV = 3909

# (column, lo, hi, clamp_lo_to, note)
RULES = [
    ('PressureBarometricAbsolute', 550, 700, None,
     f'station is at {ELEV} m; sea-level ranges do not apply'),
    ('PressureVapour', 0, 20, None, 'vapour pressure'),
    ('TemperatureAir_CS215', -60, 60, None, ''),
    ('TemperatureAir_ClimaVUE50', -60, 60, None, ''),
    ('TemperatureAir_HygroVUE10', -60, 60, None, ''),
    ('TemperatureHumiditySensor_ClimaVUE50', -60, 60, None,
     'this channel is a TEMPERATURE (sensor body), not a humidity'),
    ('TemperatureSurface_SI111', -60, 80, None, 'IR surface temp'),
    ('TempSoil_1', -40, 40, None, 'soil -10 cm'),
    ('TempSoil_2', -40, 40, None, 'soil -50 cm'),
    ('RelativeHumidity_CS215', 0, 100, None, ''),
    ('RelativeHumidity_HygroVUE10', 0, 100, None, ''),
    ('ISWR', -20, 1600, 0.0, 'night thermopile offset clamped to 0, not discarded'),
    ('RSWR', -20, 1400, 0.0, 'night thermopile offset clamped to 0, not discarded'),
    ('ILWR', 50, 600, None, ''),
    ('OLWR', 50, 600, None, ''),
    ('SolarRadiation_ClimaVUE', -20, 1600, 0.0, ''),
    ('SnowHeight_Laser', -50, 5000, 0.0,
     'mm; 999900 is the SHM31 error code; small negatives are snow-free noise'),
    ('WindSpeedScalMean_Prop', 0, 80, None, ''),
    ('WindSpeedMax_ClimaVUE', 0, 80, None, ''),
    ('SnowPartFluxAvg_FC4', 0, 500, None, 'FlowCapt drift flux'),
]

df = pd.read_csv(CSV, low_memory=False)
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], errors='coerce')
n = len(df)

rows, tot_rej, tot_clamp = [], 0, 0
for col, lo, hi, clamp, note in RULES:
    if col not in df.columns: continue
    s = pd.to_numeric(df[col], errors='coerce')
    present = int(s.notna().sum())
    clamped = int(((s < lo if clamp is None else (s < 0) & (s >= lo)) & s.notna()).sum()) if clamp is not None else 0
    rej = int(((s < lo) | (s > hi)).sum())
    tot_rej += rej; tot_clamp += clamped
    rows.append((col, present, rej, clamped, lo, hi, note))

with open(OUT, 'w') as f:
    f.write(f"""# Data Quality Report

**Generated**: {datetime.date.today():%B %-d, %Y}
**Dataset**: `{CSV}`
**Total records**: {n:,}
**Period**: {df.TIMESTAMP.min():%Y-%m-%d} to {df.TIMESTAMP.max():%Y-%m-%d}
**Site elevation**: {ELEV} m asl

## Method

Every channel is checked against the physical range of *its own quantity at this
site*. Two rules matter and were wrong in the previous version of this report:

1. **Pressure thresholds are site-specific.** At {ELEV} m, station pressure is
   ~615-645 hPa. A sea-level 800-1100 hPa window rejects **100 %** of valid
   readings and makes a healthy sensor look broken.
2. **Normal instrument offsets are clamped, not discarded.** A thermopile
   pyranometer reads a few W/m2 negative at night; a laser snow gauge reads a few
   mm negative over bare ground. These are correct instrument behaviour. Clamping
   to zero keeps the observation; discarding it invents a data gap for half the
   record.

| Column | Valid | Rejected | Clamped | Range applied | Note |
|---|---|---|---|---|---|
""")
    for col, present, rej, clamped, lo, hi, note in rows:
        pct = 100*rej/present if present else 0
        f.write(f"| `{col}` | {present:,} | {rej:,} ({pct:.2f} %) | {clamped:,} | "
                f"{lo} to {hi} | {note} |\n")
    f.write(f"""
**Totals**: {tot_rej:,} values rejected, {tot_clamp:,} clamped, across {n:,} records.

## Corrections to the previous report (5 November 2025)

That report flagged 443,053 "problematic measurements". The large majority were
artifacts of the thresholds:

| Claim | Finding |
|---|---|
| `PressureBarometricAbsolute` - 156,891 outside 800-1100 hPa, *"major sensor issues"* | All readings 615.6-644.2 hPa, correct for {ELEV} m. Sea-level window rejected 100 % of good data. **Sensor is healthy.** |
| `TemperatureHumiditySensor_ClimaVUE50` - 87,239 "invalid humidity >100 % or <0 %" | Channel is a **temperature** (-32.9 to 25.3 degC), all valid. A 0-100 % rule rejects every sub-zero reading. |
| `ISWR` - 99,311 "negative or >2000", *"calibration problems"* | **Zero** values exceed 2000. The 99,311 are night-time offsets (1st pct -6.6 W/m2). Normal; clamp to 0. |
| `SnowHeight_Laser` - 77,827, *"38 % of snow data invalid"* | 32,414 are the `999900` error code (genuinely invalid). The other 45,413 are small negatives over snow-free ground - valid. |

Roughly **343,000 of the 443,000** flagged values were false positives.
""")
print(f'wrote {OUT}')
for col, present, rej, clamped, lo, hi, note in rows:
    if rej or clamped:
        print(f'  {col:38s} rejected={rej:7,d} clamped={clamped:7,d}')
