import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from sites import SITES

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7})

HERE = os.path.dirname(os.path.abspath(__file__))

INK, MUTED, RULE = "#1a1a18", "#6a6a62", "#c9c9c0"
RED, BLUE, GREEN, GOLD = "#a33a1c", "#2c5f8a", "#4a6040", "#8a6a2f"
LAT0 = 38.74
KX = 111.320 * math.cos(math.radians(LAT0))   # km per deg lon
KY = 110.574                                   # km per deg lat


def xy(lon, lat):
    return lon * KX, lat * KY


def by(name):
    for s in SITES:
        if s[3].startswith(name):
            return s
    raise KeyError(name)


def scalebar(ax, km, label=None, frac=0.06, fy=None):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    xs = x0 + (x1 - x0) * frac; ys = y0 + (y1 - y0) * (fy if fy is not None else frac)
    ax.plot([xs, xs + km], [ys, ys], color=INK, lw=2.2, solid_capstyle="butt", zorder=20)
    for x in (xs, xs + km):
        ax.plot([x, x], [ys - (y1 - y0) * .012, ys + (y1 - y0) * .012], color=INK, lw=1.4, zorder=20)
    ax.text(xs + km / 2, ys + (y1 - y0) * .022, label or f"{km:g} km",
            ha="center", va="bottom", fontsize=6.4, color=INK, zorder=20)


def north(ax, fx=.955, fy=.86):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    x = x0 + (x1 - x0) * fx; y = y0 + (y1 - y0) * fy; d = (y1 - y0) * .055
    ax.annotate("", xy=(x, y + d), xytext=(x, y - d),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.3), zorder=20)
    ax.text(x, y + d * 1.15, "N", ha="center", va="bottom", fontsize=7, fontweight="bold", color=INK, zorder=20)


def clean(ax):
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")


# ═══════════════ MAP 1 — JOURNEY (schematic strip) ═══════════════
def journey():
    fig, ax = plt.subplots(figsize=(7.3, 2.35))
    ax.set_xlim(0, 100); ax.set_ylim(0, 34); ax.axis("off")

    stops = [
        (5,  "Dushanbe",      "706 m",   "Arrive · OVIR registration\nfood, final details", "hotel"),
        (29, "Obigarm /\nRasht valley", "", "Transit", ""),
        (52, "Tavildara",     "~1600 m", "Overnight on the drive in\n(2025 pattern)", "hotel"),
        (74, "Sangvor",       "~1800 m", "District centre · 4G HERE\nBridge team engaged from here", "village"),
        (95, "Nissai\nroadhead", "~2430 m", "Drive in · camp\nNO phone coverage beyond", "camp"),
    ]
    ax.plot([5, 95], [21, 21], color=RULE, lw=6, solid_capstyle="round", zorder=1)
    ax.plot([5, 95], [21, 21], color=INK, lw=1.6, ls=(0, (5, 3)), zorder=2)

    for x, name, ele, note, kind in stops:
        big = kind in ("hotel", "camp", "village")
        ax.add_patch(Circle((x, 21), 1.5 if big else 1.0, facecolor="white",
                            edgecolor=INK, lw=1.6 if big else 1.1, zorder=5))
        if big:
            ax.add_patch(Circle((x, 21), .62, facecolor=INK, zorder=6))
        ax.text(x, 25.4, name, ha="center", va="bottom", fontsize=7.6,
                fontweight="bold", color=INK, linespacing=1.15)
        if ele:
            ax.text(x, 24.4, ele, ha="center", va="bottom", fontsize=6.2, color=MUTED)
        ax.text(x, 18.4, note, ha="center", va="top", fontsize=6.1,
                color=MUTED, linespacing=1.3)

    for xa, xb, lab in [(5, 52, "1 full day by road"), (52, 74, "part day"), (74, 95, "part day")]:
        xm = (xa + xb) / 2
        ax.annotate("", xy=(xb - 2.2, 30.6), xytext=(xa + 2.2, 30.6),
                    arrowprops=dict(arrowstyle="<|-|>", color=GOLD, lw=1.0,
                                    shrinkA=0, shrinkB=0, mutation_scale=8))
        ax.text(xm, 31.3, lab, ha="center", va="bottom", fontsize=6.2, color=GOLD, style="italic")

    for xt in (74, 95):
        ax.text(xt, 13.4, "▲", ha="center", va="top", fontsize=8, color=RED)

    ax.text(22, 9.4, "▲ At Sangvor — CALL AHEAD: confirm the Nissai foot bridge is standing, "
                     "and commission its rebuild in advance if not.",
            ha="left", va="top", fontsize=6.2, color=RED)
    ax.text(22, 5.6, "▲ At Nissai — the road bridge (Oct 2022) avoids fording the Nissai stream "
                     "on the drive in.",
            ha="left", va="top", fontsize=6.2, color=RED)

    ax.text(22, 1.6, "Schematic — sequence and overnight stops, not to scale. Road distances not verified; "
                     "durations from the 2024–25 field reports.",
            ha="left", va="top", fontsize=5.9, color=MUTED, style="italic")
    fig.tight_layout(pad=.15)
    fig.savefig(os.path.join(HERE, "map1_journey.png"), dpi=330, facecolor="white")
    plt.close(fig)


# ═══════════════ MAP 2 — HIKE IN (plan + profile) ═══════════════
ROUTE = ["WP114", "WP62", "WP60", "WP59", "AWS"]


def hike():
    fig = plt.figure(figsize=(7.3, 5.55))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.32, 1], hspace=.30)
    ax = fig.add_subplot(gs[0]); clean(ax)

    pts = [by(n) for n in ROUTE]
    rx = [xy(p[0], p[1])[0] for p in pts]
    ry = [xy(p[0], p[1])[1] for p in pts]

    allx = [xy(s_[0], s_[1])[0] for s_ in SITES]
    ally = [xy(s_[0], s_[1])[1] for s_ in SITES]
    cx, cy = (min(allx) + max(allx)) / 2, (min(ally) + max(ally)) / 2
    ax.set_xlim(cx - 5.4, cx + 5.4); ax.set_ylim(cy - 2.7, cy + 2.7)

    ax.plot(rx, ry, color=INK, lw=2.1, ls=(0, (5, 2.6)), zorder=3, solid_capstyle="round")

    for lon, lat, ele, name, typ, st, note in SITES:
        x, y = xy(lon, lat)
        if typ in ("stake", "stake_acc"):
            ax.plot(x, y, "^", ms=4.4, color="#d99878", mec="white", mew=.5, zorder=4)
        elif typ == "logger_geop":
            ax.plot(x, y, "s", ms=4.8, color=RED, mec="white", mew=.6, zorder=6)
        elif typ == "station":
            ax.plot(x, y, "*", ms=16, color=GREEN, mec="white", mew=.8, zorder=8)
        elif typ == "logger_ble":
            c = {"active": BLUE, "suspended": RED, "lost": "#c4c4bc", "never_read": GOLD}[st]
            ax.plot(x, y, "o", ms=4.6, color=c, mec="white", mew=.6, zorder=5)

    lab = {"WP114": ("NISSAI ROADHEAD · 2429 m\ndrive in, camp", 0, -.34, "center", "top", True, INK),
           "WP62":  ("WP62 · 2801 m", -.15, -.30, "center", "top", False, BLUE),
           "WP60":  ("WP60 · 3236 m — terrace camp area (approx.)", 0, .34, "center", "bottom", False, BLUE),
           "WP59":  ("WP59 · 3591 m", .55, .05, "left", "center", False, BLUE),
           "AWS":   ("AWS + BASECAMP AREA\n3909 m", -.55, -.34, "center", "top", True, INK)}
    for k, (t, dx, dy, ha, va, bold, col) in lab.items():
        p = by(k); x, y = xy(p[0], p[1])
        ax.text(x + dx, y + dy, t, fontsize=6.4, ha=ha, va=va, color=col,
                fontweight="bold" if bold else "normal", linespacing=1.3, zorder=9)

    p = by("NI 6-25"); x, y = xy(p[0], p[1])
    ax.text(x + .45, y - .30, "ABLATION STAKES\nsee map 3", fontsize=6.6, color=RED,
            ha="left", va="top", fontweight="bold", linespacing=1.3, zorder=9)
    gp = by("WP100"); gx, gy = xy(gp[0], gp[1])
    ax.annotate("WP100 + suspended ridge loggers\nradio readout only — do not climb",
                xy=(gx, gy), xytext=(gx - .55, gy - .55), fontsize=6.1, color=RED,
                ha="center", va="top", linespacing=1.3, zorder=9,
                arrowprops=dict(arrowstyle="-", color=RED, lw=.7, shrinkA=2, shrinkB=4))
    p = by("WP54"); x, y = xy(p[0], p[1])
    ax.text(x, y + .40, "WP54 · 4616 m\nnever read since 2021", fontsize=6.1, color=GOLD,
            ha="center", va="bottom", linespacing=1.3, zorder=9)

    scalebar(ax, 2, "2 km", frac=.60, fy=.055); north(ax, fx=.045, fy=.84)
    ax.set_title("Hike in — Nissai roadhead to basecamp, with the ground-temperature network",
                 fontsize=8, fontweight="bold", color=INK, loc="left", pad=14)
    fig.text(.985, .962, "★ AWS   ● BLE logger — blue active · red suspended · grey lost · gold never read\n"
                         "■ Geoprecision   ▲ ablation stake        dashed line = route in",
             fontsize=5.9, ha="right", va="top", color=MUTED, linespacing=1.45)

    # ---- profile ----
    axp = fig.add_subplot(gs[1])
    d = [0.0]
    for i in range(1, len(pts)):
        a0 = xy(pts[i - 1][0], pts[i - 1][1]); a1 = xy(pts[i][0], pts[i][1])
        d.append(d[-1] + math.hypot(a1[0] - a0[0], a1[1] - a0[1]))
    e = [p[2] for p in pts]
    axp.fill_between(d, 2150, e, color="#eceae2", zorder=1)
    axp.plot(d, e, color=INK, lw=1.6, zorder=3)
    axp.plot(d, e, "o", ms=4.6, color="white", mec=INK, mew=1.3, zorder=4)
    names = ["Nissai roadhead", "WP62", "WP60 · terrace camp", "WP59", "AWS / basecamp"]
    for di, ei, nm in zip(d, e, names):
        axp.text(di, ei + 85, f"{ei} m", ha="center", va="bottom", fontsize=6.1,
                 color=INK, fontweight="bold")
        axp.text(di, 2215, nm, ha="center", va="bottom", fontsize=5.9, color=MUTED)
    axp.set_ylim(2150, 4450); axp.set_xlim(-.55, d[-1] + .55)
    axp.set_ylabel("m a.s.l.", fontsize=6.4, color=MUTED)
    axp.set_xlabel("straight-line distance along the valley (km) — walking distance is longer",
                   fontsize=6.2, color=MUTED)
    axp.tick_params(labelsize=6, colors=MUTED, length=2)
    for s_ in ("top", "right"):
        axp.spines[s_].set_visible(False)
    for s_ in ("left", "bottom"):
        axp.spines[s_].set_color(RULE)
    axp.grid(axis="y", color=RULE, lw=.4, alpha=.6, zorder=0)
    axp.text(d[-1] * .5, 4360, f"≈{d[-1]:.1f} km horizontal · ≈{e[-1]-e[0]} m ascent · "
             "two days in the 2024–25 pattern (terrace camp, then basecamp)",
             ha="center", va="top", fontsize=6.3, color=GOLD, style="italic")
    # NOTE: writes map2_hike.png (plan + profile), NOT map2_profile.png.
    # The card embeds a profile-ONLY figure; the code that made it is not in this
    # handoff. See README.md "Known gaps". Do not point this at map2_profile.png —
    # it would overwrite the card's image with a different figure.
    fig.savefig(os.path.join(HERE, "map2_hike.png"), dpi=330, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ═══════════════ MAP 3 — AWS + STAKES ═══════════════
def site():
    fig, ax = plt.subplots(figsize=(7.3, 3.7)); clean(ax)
    stakes = [s for s in SITES if s[4] == "stake"]
    acc = by("NS8-24"); aws = by("AWS"); geop = by("WP100")

    sx = [xy(s[0], s[1])[0] for s in stakes]
    sy = [xy(s[0], s[1])[1] for s in stakes]
    ax.plot(sx, sy, color=RED, lw=1.1, ls=(0, (4, 2.4)), alpha=.55, zorder=2)

    ax_, ay_ = xy(aws[0], aws[1])
    ax.plot([ax_, sx[0]], [ay_, sy[0]], color=INK, lw=1.5, ls=(0, (5, 2.6)), zorder=2)
    ax.plot(ax_, ay_, "*", ms=19, color=GREEN, mec="white", mew=1.0, zorder=8)
    ax.text(ax_, ay_ - .085, f"AWS  {aws[2]} m\n{aws[0]:.5f}, {aws[1]:.5f}", fontsize=6.6, ha="center",
            va="top", fontweight="bold", color=INK, linespacing=1.3)

    # stake labels: above the line, except NI 6 which sits south of it
    PLACE = {"1": ("center", "bottom", 0, .055), "2": ("center", "bottom", 0, .055),
             "3": ("center", "bottom", 0, .055), "4": ("center", "bottom", 0, .055),
             "5": ("center", "bottom", .02, .055), "6": ("left", "center", .05, -.005),
             "7": ("center", "bottom", 0, .055)}
    for (lon, lat, ele, name, *_), x, y in zip(stakes, sx, sy):
        n = name.split()[1].split("-")[0]
        melt = n in ("1", "2", "5", "7")
        ha, va, dx, dy = PLACE[n]
        ax.plot(x, y, "^", ms=9.5, color=RED if melt else "#d99878", mec="white", mew=.9, zorder=7)
        ax.text(x + dx, y + dy, f"{name}\n{ele} m" + ("\nnear melt-out" if melt else ""),
                fontsize=5.9, ha=ha, va=va,
                color=RED if melt else INK, linespacing=1.25,
                fontweight="bold" if melt else "normal", zorder=9)

    x, y = xy(acc[0], acc[1])
    ax.plot(x, y, "^", ms=9.5, color=BLUE, mec="white", mew=.9, zorder=7)
    ax.text(x + .06, y - .02, f"NS8-24 · {acc[2]} m\naccumulation stake\n+ firn core site",
            fontsize=5.9, ha="left", va="center", color=BLUE, linespacing=1.25)

    # ridge cluster: WP100 + WP44/47/48 all lie within ~100 m of each other
    gx, gy = xy(geop[0], geop[1])
    for lon, lat, ele, name, typ, st, note in SITES:
        if typ == "logger_ble" and st == "suspended":
            xx, yy = xy(lon, lat)
            ax.plot(xx, yy, "o", ms=4.2, color=RED, mec="white", mew=.6, zorder=6)
    ax.plot(gx, gy, "s", ms=8, color=RED, mec="white", mew=.9, zorder=7)
    ax.add_patch(Circle((gx, gy), .085, facecolor="none", edgecolor=RED, lw=.8,
                        ls=(0, (2.5, 2)), alpha=.85, zorder=5))
    ax.annotate("RIDGE CLUSTER — all within ~100 m\n"
                "WP100 Geoprecision 4416 m · read by radio from the glacier\n"
                "WP44 / 47 / 48 BLE · SUSPENDED — do not climb the block slope",
                xy=(gx, gy - .085), xytext=(gx - .12, gy - .32),
                fontsize=5.9, ha="right", va="top", color=RED, linespacing=1.3, zorder=9,
                arrowprops=dict(arrowstyle="-", color=RED, lw=.7, shrinkA=2, shrinkB=2))

    xx, yy = xy(*by("WP55")[:2])
    ax.plot(xx, yy, "o", ms=4.2, color=BLUE, mec="white", mew=.6, zorder=6)
    ax.text(xx - .015, yy - .050, "WP55 · 4002 m", fontsize=5.9, ha="center", va="top", color=BLUE)

    ax.margins(.14)
    scalebar(ax, 1, "1 km"); north(ax)
    ax.set_title("AWS and ablation stake network — positions as left September 2025",
                 fontsize=8, fontweight="bold", color=INK, loc="left", pad=5)
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    ax.text(x0 + (x1 - x0) * .02, y1 - (y1 - y0) * .02,
            "▲ stake (red = projected near melt-out)   ★ AWS   ■ Geoprecision   ● BLE logger\n"
            "Stakes move with the ice — treat these as search origins and record a new waypoint at each.",
            fontsize=6.0, ha="left", va="top", color=MUTED, linespacing=1.4)
    fig.tight_layout(pad=.2)
    fig.savefig(os.path.join(HERE, "map3_site.png"), dpi=330, facecolor="white", bbox_inches="tight")
    plt.close(fig)


journey(); hike(); site()
print("maps written")
