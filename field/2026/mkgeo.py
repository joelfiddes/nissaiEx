import json, os, zipfile, csv
from xml.sax.saxutils import escape
from sites import SITES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "geo")
os.makedirs(OUT, exist_ok=True)
STAMP = "2026-08-27"

SYM = {"stake": "Flag, Red", "stake_acc": "Flag, Blue", "station": "Pin, Green",
       "logger_geop": "Circle, Red", "logger_ble": "Circle, Blue", "settlement": "City (Small)"}

# ---------- CSV ----------
with open(f"{OUT}/nissai_2026.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["name", "type", "status", "lon", "lat", "elev_m", "note"])
    for lon, lat, ele, name, typ, st, note in SITES:
        w.writerow([name, typ, st, f"{lon:.6f}", f"{lat:.6f}", ele, note])

# ---------- GeoJSON ----------
fc = {"type": "FeatureCollection",
      "name": "Nissai_Sangvor_2026",
      "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
      "features": [
          {"type": "Feature",
           "geometry": {"type": "Point", "coordinates": [lon, lat, ele]},
           "properties": {"name": name, "type": typ, "status": st, "elev_m": ele, "note": note}}
          for lon, lat, ele, name, typ, st, note in SITES]}
with open(f"{OUT}/nissai_2026.geojson", "w") as f:
    json.dump(fc, f, indent=1)

# ---------- GPX ----------
gpx = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<gpx version="1.1" creator="Nissai field protocol 2026" xmlns="http://www.topografix.com/GPX/1/1">',
       f'<metadata><name>Nissai Sangvor 2026</name><time>{STAMP}T00:00:00Z</time></metadata>']
for lon, lat, ele, name, typ, st, note in SITES:
    desc = f"{typ} | {st} | {note}".strip(" |")
    gpx += [f'<wpt lat="{lat:.6f}" lon="{lon:.6f}">',
            f'  <ele>{ele}</ele>',
            f'  <name>{escape(name)}</name>',
            f'  <desc>{escape(desc)}</desc>',
            f'  <sym>{escape(SYM.get(typ, "Waypoint"))}</sym>',
            f'  <type>{escape(typ)}</type>',
            '</wpt>']
gpx.append('</gpx>')
open(f"{OUT}/nissai_2026.gpx", "w").write("\n".join(gpx))

# ---------- KML ----------
STYLE = {"stake": ("ff3643a3", "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"),
         "stake_acc": ("ffd4a52c", "http://maps.google.com/mapfiles/kml/paddle/blu-circle.png"),
         "station": ("ff50a05a", "http://maps.google.com/mapfiles/kml/paddle/grn-stars.png"),
         "logger_geop": ("ff1c3aa3", "http://maps.google.com/mapfiles/kml/paddle/red-stars.png"),
         "logger_ble": ("ffd48a2c", "http://maps.google.com/mapfiles/kml/paddle/blu-blank.png"),
         "settlement": ("ff888888", "http://maps.google.com/mapfiles/kml/paddle/wht-blank.png")}
kml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
       '<name>Nissai Sangvor 2026</name>']
for t, (col, icon) in STYLE.items():
    kml += [f'<Style id="{t}"><IconStyle><color>{col}</color><scale>1.1</scale>',
            f'<Icon><href>{icon}</href></Icon></IconStyle></Style>']
groups = {}
for s in SITES:
    groups.setdefault(s[4], []).append(s)
LABEL = {"stake": "Ablation stakes", "stake_acc": "Accumulation stake", "station": "Weather station",
         "logger_geop": "Geoprecision bedrock logger", "logger_ble": "SLF BLE ground temperature loggers"}
for typ, rows in groups.items():
    kml.append(f'<Folder><name>{escape(LABEL.get(typ, typ))}</name>')
    for lon, lat, ele, name, t, st, note in rows:
        kml += ['<Placemark>', f'<name>{escape(name)}</name>',
                f'<description>{escape(f"{ele} m a.s.l. | status: {st} | {note}")}</description>',
                f'<styleUrl>#{t}</styleUrl>',
                f'<Point><altitudeMode>absolute</altitudeMode>'
                f'<coordinates>{lon:.6f},{lat:.6f},{ele}</coordinates></Point>', '</Placemark>']
    kml.append('</Folder>')
kml.append('</Document></kml>')
open(f"{OUT}/nissai_2026.kml", "w").write("\n".join(kml))

# ---------- README ----------
open(f"{OUT}/README.txt", "w").write(
"""NISSAI / SANGVOR GEO PACKAGE - September 2026 campaign
Generated 2026-08-27. WGS84 (EPSG:4326), decimal degrees, elevations in metres a.s.l.

FILES
  nissai_2026.gpx      Waypoints for handheld GPS (Garmin etc.) and QGIS
  nissai_2026.kml      Google Earth / Google Maps, grouped and styled by type
  nissai_2026.geojson  QGIS / web mapping, elevation carried as Z
  nissai_2026.csv      Plain table for any other use

CONTENTS (23 points)
  8  stakes    NI 1-25 .. NI 7-25 plus accumulation stake NS8-24
  1  station   AWS Nissai (WP51)
  1  logger    WP100 Geoprecision M-Log5W-Rock
 13  loggers   SLF BLE ground temperature network

STATUS FIELD
  target      Stake position as left Sep 2025 - this is what to navigate to in 2026
  active      Expected working; read out this visit
  never_read  Installed 2021, never yet downloaded (WP54, 4616 m)
  suspended   DO NOT ACCESS - unstable block slope (WP44, WP47, WP48)
  lost        Confirmed lost; do not search (WP58 2024, WP63 2023)

CAVEATS
  - Stake positions are where stakes were left in Sep 2025. Ice flow will have moved
    them; treat as search origins, not fixed points, and record a new waypoint at each.
  - Elevations are GPS-derived. NI 6-25 elevation is suspect: 4343 m (2025) vs 4383 m
    (2024) at a near-identical position. Re-survey.
  - No terrain or imagery basemap is included - load these over your own basemap.
""")

with zipfile.ZipFile(os.path.join(HERE, "Nissai_2026_geo_package.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(OUT)):
        z.write(f"{OUT}/{fn}", fn)

for fn in sorted(os.listdir(OUT)):
    print(f"  {fn:24} {os.path.getsize(f'{OUT}/{fn}'):>7} bytes")
print("zip:", os.path.getsize(os.path.join(HERE, "Nissai_2026_geo_package.zip")), "bytes")
