# Nissai / Sangvor 2026 field campaign

Field card, long protocol, and geo packages for the **early September 2026**
campaign. Landed from a Cowork handoff on 27 Aug 2026 — see [HANDOFF.md](HANDOFF.md)
for the original session notes, open items and owners.

`HANDOFF.md` is the record of what the Cowork session established. This file is
the record of how to rebuild the deliverables **on a Mac**, and where the rebuild
chain is broken.

## Deliverables

| File | What it is |
|---|---|
| `Nissai_Field_Card_2026.pdf` | **Primary.** Print and carry. Pack list, pre-departure checklist, maps, 4 activity SOPs. |
| `Nissai_Sangvor_Field_Protocol_2026.pdf` | Long-form reference, 21 pp. Adds the SLF BLE network and the stream gauge, which the card omits. |
| `Nissai_2026_geo_package.zip` | Full survey: GPX / KML / GeoJSON / CSV, 23 status-coded points. Load on both GPS units. |
| `stakes/nissai_stakes_2026.gpx`<br>`stakes/nissai_stakes_2026.kml` | **Stakes only** — the 7 NI x-25 ablation stakes + NS8-24 accumulation stake, for navigating the glacier day without 14 logger waypoints in the list. |

## Sources

| File | Role |
|---|---|
| `sites.py` | **Single source of truth for all coordinates.** Maps, geo package and stakes package all read from it. Change a coordinate here and regenerate. |
| `short.html` | Source for the field card. **Edit this, not the PDF.** |
| `protocol.html` | Source for the long protocol. |
| `mkgeo.py` | Full geo package → `geo/` + `Nissai_2026_geo_package.zip` |
| `mkstakes.py` | Stakes-only GPX/KML → `stakes/` |
| `mkmaps.py` | Journey / hike / site maps → `map*.png` |
| `fig1..3_region/approach/valley.png` | Figures 1–3 lifted from the 2025 field report (satellite basemaps). |

## Rebuild

```bash
cd field_2026
python3 mkgeo.py       # full geo package   — reproduces the shipped zip byte-for-byte
python3 mkstakes.py    # stakes-only GPX/KML
python3 mkmaps.py      # maps — see "Known gaps" before trusting map2
```

For the PDFs, via WeasyPrint:

```bash
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib \
  python3 -c "from weasyprint import HTML; HTML('short.html').write_pdf('Nissai_Field_Card_2026.pdf')"
```

**The `DYLD_FALLBACK_LIBRARY_PATH` prefix is required on this Mac.** pango, glib,
cairo, gdk-pixbuf, harfbuzz and fontconfig are all installed under Homebrew, but
the conda Python at `~/miniconda3/bin/python3` does not search `/opt/homebrew/lib`,
so WeasyPrint fails with `cannot load library 'libgobject-2.0-0'`. Nothing needs
installing — it is purely a loader-path problem.

Verified on this Mac (Python 3.11, matplotlib 3.10.8, WeasyPrint 69.0): `mkgeo.py`
reproduces the shipped `Nissai_2026_geo_package.zip` **contents byte-identically**;
`mkmaps.py` reproduces `map1_journey.png` and `map3_site.png` faithfully (PNG bytes
differ by encoder version only); `short.html` builds to a 9-page card with all five
figures embedded and the page-number footers intact.

## Known gaps

Three places where the rebuild chain does not actually close. All three were
inherited from the handoff, not introduced here.

1. **`map2_profile.png` cannot be regenerated.** `mkmaps.py`'s `hike()` produces a
   *two-panel* figure (route plan + elevation profile) and writes it to
   `map2_hike.png`. The figure actually embedded in the card is the **profile
   panel alone**. Whatever produced that crop is not in the handoff. Do not point
   `hike()` at `map2_profile.png` — it would silently replace the card's image
   with a different figure. To change map 2, either re-derive the profile-only
   figure or accept the two-panel version and re-embed deliberately.

2. **Re-embedding a regenerated PNG is manual.** Images live in the HTML as base64
   data URIs, so regenerating a PNG does not update the card. The handoff notes
   the embedding code "is in the session history" — i.e. it is gone. A replacement
   would swap the `src` of the matching `<img alt="...">`.

3. **`mkgeo.py` zip bytes differ across runs** (timestamps in the archive), though
   the contents are identical. Compare extracted members, not the zip itself.

## Layout note — no CSS multi-column

The pack list on page 1 is an explicit two-cell `table.packgrid`, not
`column-count: 2`. WeasyPrint ignores `column-fill: balance` and pours the whole
list into the first column, leaving the right half of the page blank — it looks
correct in a browser and wrong in the PDF. If you add pack-list categories, move
them between the two `<td class="pack">` cells by hand to keep the columns even.

## Sandbox-path fix

`mkgeo.py` and `mkmaps.py` shipped with hardcoded `/home/claude/...` output paths
from the Cowork sandbox, so the documented rebuild failed immediately here. Both
now resolve output relative to the script's own directory. This is the only
behavioural change made to the generators.

## Before departure

Six blocking items with named owners are on **page 2 of the field card** and in
[HANDOFF.md](HANDOFF.md). The two that are Joel's: the **glacier station
replacement decision** (hardware travels in on this trip or not at all), and
chasing Evan for the **sensor depth register + CR350 security code** (without the
register the recovered temperatures cannot be assigned to depths; without the code
the logger reads as dead hardware).
