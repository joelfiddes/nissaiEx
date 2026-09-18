"""Stakes-only GPX + KML for the September 2026 campaign.

Subset of the full geo package (mkgeo.py): just the ablation stake network, for
loading onto a GPS as the day's navigation targets without the ~14 logger and
station waypoints cluttering the list.

Positions are AS LEFT SEPTEMBER 2025. The ice has moved them since — treat every
point as a search origin and record a fresh waypoint at each stake.

Writes into stakes/:  nissai_stakes_2026.gpx, nissai_stakes_2026.kml
"""
import os
from xml.sax.saxutils import escape
from sites import SITES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stakes")
os.makedirs(OUT, exist_ok=True)
STAMP = "2026-08-27"

# The 7 NI x-25 ablation stakes plus the NS8-24 accumulation stake — row 1..8 of
# the field card's stake table. NS8-24 keeps its 2024 label because that is what
# is physically written on the stake.
STAKES = [s for s in SITES if s[4] in ("stake", "stake_acc")]

# Projected emergent length at Sep 2026 and whether redrilling is near-certain,
# from the field card table (emergent_2025 + 24-25 ablation).
PROJECTED = {
    "NI 1-25": ("~486 cm emergent", "NEAR MELT-OUT"),
    "NI 2-25": ("~492 cm emergent", "NEAR MELT-OUT"),
    "NI 3-25": ("~370 cm emergent", "redrill"),
    "NI 4-25": ("~332 cm emergent", "redrill"),
    "NI 5-25": ("~308 cm emergent", "NEAR MELT-OUT"),
    "NI 6-25": ("~206 cm emergent", "redrill"),
    "NI 7-25": ("~280 cm emergent", "NEAR MELT-OUT"),
    # No ablation projection — this is the accumulation stake, not an ablation stake.
    "NS8-24":  ("", "Accumulation stake, reinforced; 2024 firn core site"),
}


def desc(name, ele, note):
    proj, flag = PROJECTED.get(name, ("", ""))
    # The sites.py note repeats the melt-out warning the flag already carries,
    # and for NS8-24 it repeats the flag wholesale. Drop the duplication, but
    # keep NI 6-25's ELEVATION SUSPECT tail — that one is not said anywhere else.
    note = note.replace("; near melt-out", "")
    if name == "NS8-24":
        note = ""
    bits = [f"{ele} m", "as left Sep 2025"]
    if proj:
        bits.append(f"Sep 2026 projected: {proj}")
    if flag:
        bits.append(flag)
    if note:
        bits.append(note)
    return " | ".join(bits)


# ---------- GPX ----------
gpx = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<gpx version="1.1" creator="Nissai stakes 2026" '
       'xmlns="http://www.topografix.com/GPX/1/1">',
       '<metadata><name>Nissai ablation stakes 2026</name>'
       '<desc>Positions as left September 2025 - search origins, not fixed points.</desc>'
       f'<time>{STAMP}T00:00:00Z</time></metadata>']
for lon, lat, ele, name, typ, st, note in STAKES:
    gpx += [f'<wpt lat="{lat:.6f}" lon="{lon:.6f}">',
            f'  <ele>{ele}</ele>',
            f'  <name>{escape(name)}</name>',
            f'  <desc>{escape(desc(name, ele, note))}</desc>',
            f'  <sym>{"Flag, Blue" if typ == "stake_acc" else "Flag, Red"}</sym>',
            f'  <type>{escape(typ)}</type>',
            '</wpt>']
gpx.append('</gpx>')
open(f"{OUT}/nissai_stakes_2026.gpx", "w").write("\n".join(gpx))

# ---------- KML ----------
kml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
       '<name>Nissai ablation stakes 2026</name>',
       '<description>Positions as left September 2025. Ice flow has moved them; '
       'treat as search origins and record a new waypoint at each.</description>',
       '<Style id="stake"><IconStyle><color>ff3643a3</color><scale>1.1</scale>'
       '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>'
       '</Icon></IconStyle></Style>',
       '<Style id="stake_acc"><IconStyle><color>ffd4a52c</color><scale>1.1</scale>'
       '<Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href>'
       '</Icon></IconStyle></Style>']
for label, want in (("Ablation stakes", "stake"), ("Accumulation stake", "stake_acc")):
    rows = [s for s in STAKES if s[4] == want]
    if not rows:
        continue
    kml.append(f'<Folder><name>{escape(label)}</name>')
    for lon, lat, ele, name, typ, st, note in rows:
        kml += ['<Placemark>', f'<name>{escape(name)}</name>',
                f'<description>{escape(desc(name, ele, note))}</description>',
                f'<styleUrl>#{typ}</styleUrl>',
                '<Point><altitudeMode>absolute</altitudeMode>'
                f'<coordinates>{lon:.6f},{lat:.6f},{ele}</coordinates></Point>',
                '</Placemark>']
    kml.append('</Folder>')
kml.append('</Document></kml>')
open(f"{OUT}/nissai_stakes_2026.kml", "w").write("\n".join(kml))

for fn in sorted(os.listdir(OUT)):
    print(f"  {fn:26} {os.path.getsize(f'{OUT}/{fn}'):>6} bytes")
print(f"{len(STAKES)} stakes written")
