# nissaiEx — Nissai / Sangvor, Western Pamir, Tajikistan

Everything for the Nissai field site in one place: the automatic weather
station, the glacier thermistor string, the ground-surface-temperature loggers,
field materials, docs and reports.

Named for the glacier and catchment rather than the district, because
`sangvor*` is heavily overloaded — `~/data/sangvor_station`,
`~/data/SANGVOR_LOGGERS`, `TajGST/data/sangvor`, and a `sangvorGST` folder in
Drive all mean different things. `nissaiEx` greps clean.

Upper Khingob watershed, Sangvor district. Deployed September 2021 under SNF
"Precipitation in extreme environments" (179130) and the SDC-funded
CROMO-ADAPT project — WSL/SLF, UNIFR, EPFL CRYOS and CRG Dushanbe.

## Instruments

| | Logger | Position | Record |
|---|---|---|---|
| **Nissai AWS** | CR1000X | 38.74287 N, 71.35392 E, 3909 m | 2021-09-22 → 2026-09-07, 10 min |
| **Glacier station** | CR350 | — | 2025-09-05 → 2026-09-06, hourly, 8-channel thermistor string |
| **GST WP100** | GeoPrecision FG2 `A542D3` | 71.371561 E, 38.733798 N, 4416 m, rock | 2022-09-07 → 2026-09-06, 6-hourly |

Full AWS sensor list and site description: `docs/sangvor_factsheet.pdf`.

Maps: [AWS topography](reports/nissai_aws_topo.png) ·
[GST logger network](reports/nissai_gst_map.png) — coordinates and data links
for every logger in [`stations/gst/`](stations/gst/README.md).

## Layout

```
stations/nissai_aws/    AWS: water-year data, QC report, processing scripts
stations/glacier/       CR350 thermistor string
stations/gst/           ground-surface temperature (see note below)
scripts/                Campbell TOB1/TOB3 conversion, plotting
field/                  protocols, field cards, maps, geo packages
docs/                   factsheet, station documentation
reports/                generated figures and reports
```

**Data is split by water year** (1 Oct → 30 Sep, labelled by the closing year).
That keeps every file well under any git size limit and matches the early-
September download campaigns, so each file closes just after the card is pulled.

## Card conversion

Campbell writes the cards in binary TOB1/TOB3, normally readable only by PC400 /
LoggerNet CardConvert on Windows. `scripts/` converts both natively:

| script | format | validation |
|---|---|---|
| `cardconvert.py` + `tob.py` | TOB1 → TOA5 | 2,000,000 values byte-exact vs logger TOA5 |
| `tob3convert.py` + `tob3.py` | TOB3 → TOA5 | 85,881 rows byte-exact vs CardConvert output |

Both reproduce CardConvert's own conventions, including Campbell's mixed
endianness (integer types big-endian, IEEE floats little-endian), 7-significant-
digit rounding with halves away from zero, and E-notation below 1e-4.

`tob3.py` additionally recovers records CardConvert discards when it hits a
corrupt frame — it stops at the first bad frame, losing everything after it.

## Known data issues

- **AWS 2025-09-03 → 09-29 (25.5 d)**: not a station outage. `RECORD` runs
  79 → 3753 across the gap — 3,674 records, exactly the duration — so the logger
  recorded throughout and wrote to the card. Those records are in
  `Meteodata_Entire_225/226/227`, which carry no valid validation stamps.
  **Card corruption; possibly recoverable from a raw card image.**
- **AWS 2021-09-22 → 10-18 (25.8 d)**: same shape (`RECORD` 35 → 3750) but the
  records were never retrieved into the archive. May still exist on an old card.
- **`RECORD` is not monotonic** across 2025-09-03: the logger program changed at
  that service visit (signature 47999 → 46199) and the counter reset. Key on
  `TIMESTAMP`.
- **Glacier station lost 232 days** (2025-12-16 → 2026-08-05) to battery
  exhaustion. See `stations/glacier/README.md`.
- **QC thresholds must be site-specific.** Station pressure here is 615–645 hPa;
  a sea-level 800–1100 hPa filter rejects 100 % of valid readings. See
  `stations/nissai_aws/data_quality_report.md`.

## Note on the GST loggers

The Sangvor GST data currently lives in the `TajGST` repo under
`data/fanmountains/A542D3/`, together with the Fan Mountains loggers, because
`plot_ground_temperature.py` there selects its file-format parser by testing
whether the path contains "sangvor" — that branch expects the older `2005-00XX`
format, and these are GeoPrecision FG2 files. **Moving them here requires fixing
that parser to sniff the format instead of the path.** Until then TajGST remains
authoritative for GST.

## Licence and citation

Data, documentation and code in this repository are released under
[CC-BY-4.0](LICENSE). You may reuse them freely provided you give credit.

Please cite:

> Fiddes, J. *nissaiEx: Nissai / Sangvor field-site observations, Western
> Pamir, Tajikistan.* https://github.com/joelfiddes/nissaiEx

and acknowledge the Swiss National Science Foundation project
"Precipitation in extreme environments" (179130) and the SDC-funded
CROMO-ADAPT project, carried out by WSL/SLF, UNIFR, EPFL CRYOS and CRG
Dushanbe. Machine-readable citation metadata is in `CITATION.cff`.

## History

This repo consolidates work previously split across `nissaiStation` and
`TajGST`. Those repos are retained as the historical record — their git history
was not imported, because it contains large combined CSVs that the water-year
split exists to avoid.
