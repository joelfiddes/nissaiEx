# Data Quality Report

**Generated**: September 18, 2026
**Dataset**: `combined_meteodata2026.csv`
**Total records**: 253,283
**Period**: 2021-09-22 to 2026-09-07
**Site elevation**: 3909 m asl

## Method

Every channel is checked against the physical range of *its own quantity at this
site*. Two rules matter and were wrong in the previous version of this report:

1. **Pressure thresholds are site-specific.** At 3909 m, station pressure is
   ~615-645 hPa. A sea-level 800-1100 hPa window rejects **100 %** of valid
   readings and makes a healthy sensor look broken.
2. **Normal instrument offsets are clamped, not discarded.** A thermopile
   pyranometer reads a few W/m2 negative at night; a laser snow gauge reads a few
   mm negative over bare ground. These are correct instrument behaviour. Clamping
   to zero keeps the observation; discarding it invents a data gap for half the
   record.

| Column | Valid | Rejected | Clamped | Range applied | Note |
|---|---|---|---|---|---|
| `PressureBarometricAbsolute` | 206,334 | 0 (0.00 %) | 0 | 550 to 700 | station is at 3909 m; sea-level ranges do not apply |
| `PressureVapour` | 206,334 | 0 (0.00 %) | 0 | 0 to 20 | vapour pressure |
| `TemperatureAir_CS215` | 252,942 | 57 (0.02 %) | 0 | -60 to 60 |  |
| `TemperatureAir_ClimaVUE50` | 206,334 | 6 (0.00 %) | 0 | -60 to 60 |  |
| `TemperatureAir_HygroVUE10` | 253,068 | 14 (0.01 %) | 0 | -60 to 60 |  |
| `TemperatureHumiditySensor_ClimaVUE50` | 206,334 | 0 (0.00 %) | 0 | -60 to 60 | this channel is a TEMPERATURE (sensor body), not a humidity |
| `TemperatureSurface_SI111` | 253,283 | 0 (0.00 %) | 0 | -60 to 80 | IR surface temp |
| `TempSoil_1` | 253,283 | 0 (0.00 %) | 0 | -40 to 40 | soil -10 cm |
| `TempSoil_2` | 253,283 | 0 (0.00 %) | 0 | -40 to 40 | soil -50 cm |
| `RelativeHumidity_CS215` | 253,283 | 58 (0.02 %) | 0 | 0 to 100 |  |
| `RelativeHumidity_HygroVUE10` | 253,283 | 15 (0.01 %) | 0 | 0 to 100 |  |
| `ISWR` | 253,282 | 5 (0.00 %) | 123,480 | -20 to 1600 | night thermopile offset clamped to 0, not discarded |
| `RSWR` | 253,283 | 0 (0.00 %) | 22,929 | -20 to 1400 | night thermopile offset clamped to 0, not discarded |
| `ILWR` | 253,283 | 2 (0.00 %) | 0 | 50 to 600 |  |
| `OLWR` | 253,283 | 2 (0.00 %) | 0 | 50 to 600 |  |
| `SolarRadiation_ClimaVUE` | 206,334 | 6 (0.00 %) | 0 | -20 to 1600 |  |
| `SnowHeight_Laser` | 253,283 | 36,888 (14.56 %) | 60,254 | -50 to 5000 | mm; 999900 is the SHM31 error code; small negatives are snow-free noise |
| `WindSpeedScalMean_Prop` | 253,283 | 0 (0.00 %) | 0 | 0 to 80 |  |
| `WindSpeedMax_ClimaVUE` | 206,308 | 0 (0.00 %) | 0 | 0 to 80 |  |
| `SnowPartFluxAvg_FC4` | 253,263 | 0 (0.00 %) | 0 | 0 to 500 | FlowCapt drift flux |

**Totals**: 37,053 values rejected, 206,663 clamped, across 253,283 records.

## Corrections to the previous report (5 November 2025)

That report flagged 443,053 "problematic measurements". The large majority were
artifacts of the thresholds:

| Claim | Finding |
|---|---|
| `PressureBarometricAbsolute` - 156,891 outside 800-1100 hPa, *"major sensor issues"* | All readings 615.6-644.2 hPa, correct for 3909 m. Sea-level window rejected 100 % of good data. **Sensor is healthy.** |
| `TemperatureHumiditySensor_ClimaVUE50` - 87,239 "invalid humidity >100 % or <0 %" | Channel is a **temperature** (-32.9 to 25.3 degC), all valid. A 0-100 % rule rejects every sub-zero reading. |
| `ISWR` - 99,311 "negative or >2000", *"calibration problems"* | **Zero** values exceed 2000. The 99,311 are night-time offsets (1st pct -6.6 W/m2). Normal; clamp to 0. |
| `SnowHeight_Laser` - 77,827, *"38 % of snow data invalid"* | 32,414 are the `999900` error code (genuinely invalid). The other 45,413 are small negatives over snow-free ground - valid. |

Roughly **343,000 of the 443,000** flagged values were false positives.
