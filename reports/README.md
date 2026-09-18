# Reports

## Field reports (Google Drive)

The annual field reports live in Google Drive and are **not duplicated here**.
They are living documents, edited collaboratively after each season, and each is
75–97 MB of embedded photography — both reasons to link rather than copy.

| Season | Doc | Size | Last modified |
|---|---|---|---|
| 2023-09 | [Field_report_Sangvor_2023_09](https://docs.google.com/document/d/1OgvrowZb_Gt9Hkpd5WR_N5SO6TARtJw7g3-FG1LuLPY/edit) | 86.5 MB | 2024-05-28 |
| 2024-09 | [Field_report_Sangvor_2024_09](https://docs.google.com/document/d/1kYVW4QyJ_T24e3OPvn8penawtsyq7E39qeTG4W52TBo/edit) | 75.2 MB | 2025-11-04 |
| 2025-09 | [Field_report_Sangvor_2025_09](https://docs.google.com/document/d/1FGmFMTfwPDqaHSzEi4F2qLR1CWM7x-w9l4uI5a0BwOc/edit) | 97.5 MB | 2026-09-01 |
| 2025-09 | [backup, pre-edit 2026-09-01](https://docs.google.com/document/d/14mmwY8iOdvaTNEvQac2favC3zKrnjvWLetPZTDKWEsI/edit) | 97.5 MB | 2026-09-01 |
| 2026-09 | [Field_report_Sangvor_2026_09](https://docs.google.com/document/d/1vNbnvb_vErsQDvDJZKP0iTwmkcx_MrYIGZ0rKcQFbE8/edit) | 97.5 MB | 2026-09-18 |

Earlier seasons (2021, 2022) were not returned by the search used to build this
list — check Drive directly before assuming they are absent.

Related Drive folder: [sangvorGST](https://drive.google.com/drive/folders/1Po59j0eTwiiHF9QXgkXbR2DTxI_1J3gT)

> **The 2026 report is not yet written.** It was created 2026-09-18 as a verbatim
> copy of the 2025 report and has not been edited since. Its text still describes
> the 2025 season — participants, itinerary and findings all belong to 30/08–08/09
> 2025.

## Report structure (as used since 2023)

1. Data download and maintenance of the CRG automated meteorological station
2. Data download and maintenance of the ground temperature network
3. Catchment stream gauge
4. Ablation stake network
5. Glacier ice thermistor station
- Appendix 1: meteorological timeseries
- Appendix 2: logger metadata
- Appendix 3: expedition photos

## Material available for the 2026 report

Processed this session and ready to go into sections 1, 2 and 5:

**Section 1 — AWS.** WY2026 record is 49,154 records, 2025-10-01 → 2026-09-07,
93.1 % complete. The single gap (2025-09-03 23:50 → 09-29 12:10, 25.5 d) is
**card corruption, not a station outage** — `RECORD` runs 79 → 3753 across it,
exactly 3,674 records, so the logger recorded throughout and wrote to the card.
Files `Meteodata_Entire_225/226/227` carry no valid validation stamps. Possibly
recoverable from a raw card image. Overview figure: `sangvor_2026_overview.png`.

**Section 2 — ground temperature.** A542D3 (WP100, 4416 m) continues cleanly to
2026-09-06. A542D1/D2 deployed this season; everything downloaded from them so
far is pre-deployment office storage and their field records start next season.
Loggers sample 6-hourly despite headers declaring hourly.

**Section 5 — glacier thermistor station.** Installed 2025-09-05, **lost 232 days
to battery exhaustion** (2025-12-16 → 2026-08-05); the record is 35.1 % complete
and the entire winter and spring are missing. Battery declined 12.45 V → 9.63 V
over three weeks before cutoff. Channel depths are not recorded anywhere and are
needed to interpret the profile.

## Generated figures

| file | contents |
|---|---|
| `sangvor_2026_overview.png` | AWS year, 8 panels: temperature, snow height, wind, blowing-snow flux, SW/LW radiation, humidity, pressure |
