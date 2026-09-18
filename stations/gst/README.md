# Ground surface temperature — Sangvor

GST data is **not stored here yet**. It lives in the `TajGST` repo:

- `data/fanmountains/A542D3/` — WP100, the deployed Sangvor logger
- `data/fanmountains/A542D1`, `A542D2`, `A542D4` — pre-deployment storage only
- `data/sangvor/` — the older `2005-00XX` BLE logger series
- `data/metadata/BLE_sangvor_loggers.csv` — site metadata incl. WP100

## Why it has not moved

`TajGST/scripts/plot_ground_temperature.py` picks its file-format parser by
testing whether the path contains `"sangvor"`. That branch expects the older
`2005-00XX` format; the `A542Dx` loggers are GeoPrecision FG2, matching the
`fanmountains` branch. In a repo *called* sangvor every path matches, so every
FG2 file would be silently mis-parsed.

**Fix the parser to sniff the file header rather than the path, then migrate.**

## What to know about the A542Dx loggers

- **Only A542D3 has a field record**, from 2022-09-07 at WP100 (4416 m, rock).
  Trim to that date — the preceding ~14 months are office storage and will bias
  MAGST and freezing-index badly.
- **A542D1, D2 and D4 read office temperatures** (18–31 °C year-round, tracking
  one another to 0.1 °C) for their whole 2021–2026 record. D1 and D2 were
  deployed at Sangvor in September 2026, so their field records begin with the
  *next* download; nothing collected so far belongs in a GST analysis.
- **Sampling is 6-hourly**, despite file headers declaring `PERIOD: 3600 sec`.
- New sites deployed in 2026 still need waypoints and coordinates adding to
  `BLE_sangvor_loggers.csv`.
