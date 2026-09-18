# Nissai / Sangvor site database — single source of truth for maps + geo package
# lon, lat, elev(m), name, type, status, note

SITES = [
 # --- ablation stakes: positions as left Sep 2025 = 2026 targets ---
 (71.362939, 38.741813, 4068, "NI 1-25", "stake", "target", "600cm, 595 in ice; 24-25 abl 481cm; near melt-out"),
 (71.365724, 38.739660, 4127, "NI 2-25", "stake", "target", "600cm, 600 in ice; 24-25 abl 492cm; near melt-out"),
 (71.369215, 38.739268, 4234, "NI 3-25", "stake", "target", "600cm, 600 in ice; 24-25 abl 370cm"),
 (71.372995, 38.738883, 4313, "NI 4-25", "stake", "target", "600cm, 588 in ice; 24-25 abl 320cm"),
 (71.375987, 38.738293, 4341, "NI 5-25", "stake", "target", "400cm, 391 in ice; 24-25 abl 299cm; near melt-out"),
 (71.376728, 38.735352, 4343, "NI 6-25", "stake", "target", "400cm, 400 in ice; 24-25 abl 206cm; ELEVATION SUSPECT (4383 in 2024)"),
 (71.381125, 38.739402, 4387, "NI 7-25", "stake", "target", "400cm, 391 in ice; 24-25 abl 271cm; near melt-out"),
 (71.380200, 38.730950, 4450, "NS8-24", "stake_acc", "target", "Accumulation stake, reinforced; co-located with 2022/2024 firn core site"),
 # --- stations ---
 (71.353920, 38.742870, 3909, "AWS Nissai (WP51)", "station", "active", "Campbell CR1000X, established 2021; AstroNode telemetry dead since 15 Mar 2026"),
 (71.371561, 38.733798, 4416, "WP100 Geoprecision", "logger_geop", "active", "M-Log5W-Rock; 433MHz; ID A542D3; code DE10; READ BY RADIO ~100m FROM GLACIER"),
 # --- SLF BLE ground temperature loggers ---
 (71.295810, 38.722870, 2429, "WP114 2005-0092", "logger_ble", "active", "Lowest logger; between copse of trees; replaced 2005-0079"),
 (71.307500, 38.737387, 2801, "WP62 2005-0091", "logger_ble", "active", ""),
 (71.330360, 38.750384, 3236, "WP60 2005-0081", "logger_ble", "active", ""),
 (71.341133, 38.748462, 3591, "WP59 2005-0070", "logger_ble", "active", ""),
 (71.353654, 38.745178, 3938, "WP50 2005-0071", "logger_ble", "active", "Near AWS"),
 (71.354001, 38.746032, 3942, "WP49 2005-0077", "logger_ble", "active", "Near AWS"),
 (71.360396, 38.742309, 4002, "WP55 2005-0080", "logger_ble", "active", "En route to lower stakes"),
 (71.393875, 38.737510, 4616, "WP54 2005-0085", "logger_ble", "never_read", "Never read out since 2021; hard access; decide before departure"),
 (71.371821, 38.733970, 4389, "WP44 2005-0086", "logger_ble", "suspended", "UNSTABLE BLOCK SLOPE - DO NOT ACCESS"),
 (71.371571, 38.733873, 4412, "WP47 2005-0082", "logger_ble", "suspended", "UNSTABLE BLOCK SLOPE - DO NOT ACCESS"),
 (71.371490, 38.733920, 4404, "WP48 2005-0074", "logger_ble", "suspended", "UNSTABLE BLOCK SLOPE - DO NOT ACCESS"),
 (71.352994, 38.740310, 3951, "WP58 2005-0076", "logger_ble", "lost", "Lost 2024 under collapsed block, ice-cored moraine; do not search"),
 (71.295889, 38.722846, 2431, "WP63 2005-0079", "logger_ble", "lost", "Lost 2023 to ploughed field; superseded by WP114"),
]

# Approximate / for orientation only — not surveyed
APPROX = [
 (71.2197, 38.7775, 1800, "Sangvor village", "settlement", "approx", "District centre; 4G coverage; source of bridge-building team"),
]

