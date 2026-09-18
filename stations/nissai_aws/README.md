# Nissai AWS — CR1000X

38.74287 N, 71.35392 E, 3909 m asl. 10-minute records, 41 variables,
2021-09-22 → 2026-09-07 (253,283 records).

`data/water_years/nissai_meteodata_WY<year>.csv` — water year runs 1 Oct → 30
Sep, labelled by the closing year.

| file | records | period |
|---|---|---|
| WY2021 | 36 | 2021-09-22 (deployment day) |
| WY2022 | 49,955 | 2021-10-18 → 2022-09-30 |
| WY2023 | 52,560 | 2022-10-01 → 2023-09-30 |
| WY2024 | 52,699 | 2023-10-01 → 2024-09-30 |
| WY2025 | 48,879 | 2024-10-01 → 2025-09-30 |
| WY2026 | 49,154 | 2025-10-01 → 2026-09-07 |

## Scripts

| script | purpose |
|---|---|
| `scripts/build_combined.py` | append a converted season to the combined record |
| `scripts/split_water_years.py` | split the combined record into water years |
| `scripts/qc_report.py` | physical QC with site-correct thresholds |

Card conversion (TOB1/TOB3 → TOA5) is in the repo-level `scripts/`.

## Adding a season

1. Convert the card with `scripts/cardconvert.py` (TOB1) and
   `scripts/tob3convert.py` (TOB3).
2. `build_combined.py <toa5_dir> <previous_combined.csv> <new_combined.csv>`
3. `split_water_years.py <new_combined.csv> data/water_years`
4. `qc_report.py <new_combined.csv> data_quality_report.md`

Check the join: seasons should abut with no overlapping timestamps. Do **not**
rely on `RECORD` being continuous — it reset at the 2025-09-03 program change.
