# Nissai / Sangvor 2026 field campaign — handoff

Handoff from a Cowork session, 27 Aug 2026. Everything below is either finished
and in this folder, or listed as an open item. Campaign is early September 2026,
so the blocking items are urgent.

---

## What exists

| File | What it is |
|---|---|
| `Nissai_Field_Card_2026.pdf` | **Primary deliverable.** 8 pages: maps, pack list, and 4 SOPs (AWS, stakes, glacier station, Geoprecision). Print this and carry it. |
| `Nissai_Sangvor_Field_Protocol_2026.pdf` | Long-form reference, 21 pages. Includes the SLF BLE logger network and the stream gauge, which the card deliberately omits. |
| `Nissai_2026_geo_package.zip` | GPX / KML / GeoJSON / CSV — 23 surveyed points, status-coded. Load on both GPS units. |
| `short.html` | Source for the field card. Edit this, not the PDF. |
| `protocol.html` | Source for the long protocol. |
| `sites.py` | **Single source of truth** for all coordinates. Maps and geo package both read from it. Change a coordinate here and regenerate. |
| `mkmaps.py` | Generates the schematic journey map and the elevation profile. |
| `mkgeo.py` | Generates the geo package from `sites.py`. |
| `fig1_region.png`, `fig2_approach.png`, `fig3_valley.png` | Figures 1–3 lifted from the 2025 field report (satellite basemaps). |
| `map1_journey.png`, `map2_profile.png`, `map3_site.png` | Generated maps. |

### Rebuild

```bash
pip install weasyprint matplotlib pypdf --break-system-packages
python3 mkgeo.py        # regenerates the geo package
python3 mkmaps.py       # regenerates journey + site maps
python3 -c "from weasyprint import HTML; HTML('short.html').write_pdf('Nissai_Field_Card_2026.pdf')"
```

Images are embedded in the HTML as base64 data URIs, so regenerating a PNG means
re-embedding it. The embedding code is in the session history; simplest approach
is a small script that replaces the `src` of the matching `<img alt="...">`.

---

## BLOCKING before departure

These five stop data being collected or interpreted. Owner in brackets.

1. **Glacier station package** [Evan Miles] — coordinates, 2025 summary from
   Stefan Fugger / Ines Dussaillant, the **sensor depth register**, emergent mast
   height at install, and **any CR350 security code / PakBus encryption key**.
   Without the depth register the recovered temperatures cannot be assigned to
   depths. Without the security code the logger will not respond and will read as
   dead hardware. Evan was retrieving this as of 18 Aug.

2. **Astrocast / AstroNode decision** [Andi] — telemetry dead since 15 Mar 2026,
   vendor unreachable and possibly out of business. Decide whether a replacement
   telemetry path is fitted in 2026; if so the hardware travels with the team.

3. **Glacier station replacement decision** [Joel / Evan] — if the station is
   found destroyed (considered likely) and brought down, is it replaced this
   season? Replacement hardware travels in on the same trip or not at all.

4. **Readout phone** [field team] — the SLF-Logger Manager APK targets API 19.
   **Android 14+ refuses to install it.** Either take a phone on Android 13 or
   older, or prove `adb install --bypass-low-target-sdk-block app-release.apk`
   works on the actual handset. Do not factory-reset a phone that already has it.
   (Only needed if the BLE ground-temperature network is being read — the card
   omits it, the long protocol covers it.)

5. **GP5W-Shell + 433 MHz dongle** [field team] — install GP5W-Shell on the field
   laptop and confirm the 433 MHz GeoPrecision dongle works. Without that dongle
   WP100 cannot be read at all, and it is now the only sensor reporting from the
   suspended ridge.

## Non-blocking, but resolve

- **NI 6-25 elevation**: 4343 m (2025) vs 4383 m (2024) at a near-identical
  position. Re-survey in the field.
- **NS8-24**: the 107 cm reading appears against both the 2024 and 2025 columns
  in the source tables. Establish which year it belongs to.
- **Stream gauge**: the 2025 report appears to carry the 2024 text forward
  unchanged, so what is actually on the ground is unknown. Not in the card.

---

## Things established this session that are easy to lose

- **Stake convention, verified against 2024–25 data.** `measured` = emergent
  length above the ice. `ablation (cm i.e.) = emergent_now − emergent_last`,
  where `emergent_last = length − in_ice`. `b (m w.e.) = −cm i.e. × 0.9 / 100`.
  Reproduces the published figures for stakes 3,4,5,6,7 exactly.
- **All 7 stakes are projected to need redrilling in 2026**; stakes 1, 2, 5 and 7
  are within ~120 cm of melting out. Stake 1 melted out completely in 2025.
- **CR350 has no SD card.** Internal flash, ~50 MB, ring memory by default —
  **check the FIRST record timestamp**, not just the last, to see if it wrapped.
  In the EZSetup wizard select **"CR300 Series"**; there is no "CR350" entry.
  USB supplies 5 V, so it can be downloaded even with a flat station battery.
- **Three different clock conventions on one trip**: AWS/CR350 local UTC+5,
  GeoPrecision **UTC** (set PC clock to UTC to the second, DST off), SLF BLE
  whatever device reads them. Record which was used, every time.
- **WP100 and the three suspended BLE loggers are all within ~100 m** of each
  other on the ridge. WP100 is read by radio from the glacier at ~100 m; the
  block slope must not be entered.
- **SLF BLE loggers advertise once per 10 s and the scan window times out after
  30 s.** The commonest field error is declaring a live logger dead. Restart the
  scan at least three times from more than one position.

## Sources

Drive: `Field_report_Sangvor_2025_09`, `Field_report_Sangvor_2024_09`,
`UPDATE_Nissai_massbalance_Sangvor_PAMIR`, `BLE sangvor loggers`,
`Datasheet_BLE_EN.pdf`, `Dokumentation_BLE.pdf`.
Correspondence: Evan Miles on the CR350 (18 Aug 2026); Andi on the AstroNode
faults and the Astrocast outage (April 2026).
Vendor docs: Campbell CR350 help pages; GLORIA M-Log5W guide.
