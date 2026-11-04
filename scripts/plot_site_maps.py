#!/usr/bin/env python3
"""Topographic maps of the Nissai site: the GST logger network and the AWS.

Base map is Copernicus GLO-30 (30 m DSM), hillshaded with contours. The tile is
fetched once into ~/data/dem/copernicus_glo30/ (override with $NISSAI_DEM).
Site coordinates come from field/2026/sites.py, the single source of truth.

    python scripts/plot_site_maps.py        # writes reports/nissai_gst_map.png
                                            #        reports/nissai_aws_topo.png
"""
import os, sys, math, urllib.request
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource, LinearSegmentedColormap
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import rasterio
from rasterio.windows import from_bounds

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "field", "2026"))
from sites import SITES  # noqa: E402

TILE = "Copernicus_DSM_COG_10_N38_00_E071_00_DEM"
DEM = os.environ.get("NISSAI_DEM",
                     os.path.expanduser(f"~/data/dem/copernicus_glo30/{TILE}.tif"))
URL = f"https://copernicus-dem-30m.s3.amazonaws.com/{TILE}/{TILE}.tif"
OUT = os.path.join(ROOT, "reports")

INK, MUTED = "#1a1a18", "#55554e"
HALO = [pe.withStroke(linewidth=2.6, foreground="white")]
# muted hypsometric tint: valley green -> scree beige -> snow white
TERRAIN = LinearSegmentedColormap.from_list(
    "nissai", ["#a9b98f", "#cfc9a4", "#ddd2b8", "#e9e4dc", "#f7f7f5"])


def dem_window(w, e, s, n):
    if not os.path.exists(DEM):
        os.makedirs(os.path.dirname(DEM), exist_ok=True)
        print(f"fetching {URL}")
        urllib.request.urlretrieve(URL, DEM)
    with rasterio.open(DEM) as r:
        win = from_bounds(w, s, e, n, r.transform)
        z = r.read(1, window=win, boundless=False).astype(float)
        t = r.window_transform(win)
    lon = t.c + t.a * (np.arange(z.shape[1]) + .5)
    lat = t.f + t.e * (np.arange(z.shape[0]) + .5)
    return lon, lat, z


def basemap(ax, w, e, s, n, minor=50, major=250):
    lon, lat, z = dem_window(w, e, s, n)
    dx = 30.0  # ~1 arcsec in metres, close enough for shading
    ls = LightSource(azdeg=315, altdeg=40)
    rgb = ls.shade(z, cmap=TERRAIN, blend_mode="soft", vert_exag=1.4, dx=dx, dy=dx,
                   vmin=np.nanpercentile(z, 1), vmax=np.nanpercentile(z, 99.5))
    ax.imshow(rgb, extent=(lon[0], lon[-1], lat[-1], lat[0]), interpolation="bilinear")
    LON, LAT = np.meshgrid(lon, lat)
    lo, hi = math.floor(np.nanmin(z) / minor) * minor, math.ceil(np.nanmax(z) / minor) * minor
    ax.contour(LON, LAT, z, levels=np.arange(lo, hi, minor), colors="#5b4a33",
               linewidths=.25, alpha=.45)
    cs = ax.contour(LON, LAT, z, levels=np.arange(lo, hi, major), colors="#5b4a33",
                    linewidths=.7, alpha=.75)
    ax.clabel(cs, fmt="%d", fontsize=5.5, inline_spacing=2)
    ax.set_xlim(w, e); ax.set_ylim(s, n)
    ax.set_aspect(1 / math.cos(math.radians((s + n) / 2)))
    ax.tick_params(labelsize=6.5, colors=MUTED, length=2)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.2f}°E")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.3f}°N")
    for sp in ax.spines.values():
        sp.set_color(MUTED); sp.set_linewidth(.6)


def furniture(ax, km):
    w, e = ax.get_xlim(); s, n = ax.get_ylim()
    kx = 111.320 * math.cos(math.radians((s + n) / 2))
    x0, y0 = w + (e - w) * .05, s + (n - s) * .06
    ax.plot([x0, x0 + km / kx], [y0, y0], color=INK, lw=2.4, solid_capstyle="butt")
    ax.text(x0 + km / kx / 2, y0 + (n - s) * .02, f"{km:g} km", ha="center", va="bottom",
            fontsize=6.5, color=INK, path_effects=HALO)
    xn, yn = w + (e - w) * .955, s + (n - s) * .82
    ax.annotate("", xy=(xn, yn + (n - s) * .08), xytext=(xn, yn),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
    ax.text(xn, yn + (n - s) * .09, "N", ha="center", va="bottom", fontsize=7.5,
            fontweight="bold", color=INK, path_effects=HALO)


def credit(ax, extra=""):
    ax.text(0, -.075, "Base: Copernicus GLO-30 DSM © ESA/DLR/Airbus. "
             "Positions: handheld GPS at install (WGS84). " + extra,
             fontsize=5.3, color=MUTED, ha="left", va="top", transform=ax.transAxes)


def site(prefix):
    for s in SITES:
        if s[3].startswith(prefix):
            return s
    raise KeyError(prefix)


def label(ax, lon, lat, text, dx=6, dy=4, ha="left", **kw):
    ax.annotate(text, (lon, lat), xytext=(dx, dy), textcoords="offset points",
                fontsize=kw.pop("fontsize", 6.4), color=kw.pop("color", INK), ha=ha, va="center",
                path_effects=HALO, **kw)


# ─────────────────────────── GST logger network ───────────────────────────
def gst_map():
    w, e, s, n = 71.285, 71.402, 38.714, 38.758
    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    basemap(ax, w, e, s, n)

    # (status) -> face, edge; identity is also carried by the label and legend text
    style = {"active": ("#2c5f8a", "white"), "suspended": ("white", "#a33a1c"),
             "never_read": ("white", "#2c5f8a"), "lost": ("#8b8b84", "white")}
    offsets = {"WP49": (6, 6), "WP50": (-6, 4, "right"), "WP44": (-6, -6, "right"),
               "WP47": (6, 10), "WP48": (-6, 6, "right"), "WP100": (7, -7),
               "WP63": (6, -7), "WP114": (6, 5), "WP58": (6, -6)}
    for lon, lat, ele, name, kind, status, _ in SITES:
        if kind not in ("logger_ble", "logger_geop", "station"):
            continue
        wp = name.split()[0]
        if kind == "station":
            ax.plot(lon, lat, marker="*", ms=12, mfc="#a33a1c", mec="white", mew=.8, zorder=6)
            label(ax, lon, lat, "AWS", -8, -6, "right", fontweight="bold")
            continue
        fc, ec = style[status]
        mk = "^" if kind == "logger_geop" else "o"
        ax.plot(lon, lat, marker=mk, ms=7.5 if mk == "^" else 6.2, mfc=fc, mec=ec,
                mew=1.3, zorder=5 + (status == "active"))
        o = offsets.get(wp, (6, 4))
        bold = wp in ("WP59", "WP60", "WP62", "WP100")
        label(ax, lon, lat, f"{wp} · {ele} m", o[0], o[1], o[2] if len(o) > 2 else "left",
              fontweight="bold" if bold else "normal")

    hand = [
        Line2D([], [], ls="", marker="o", ms=6, mfc="#2c5f8a", mec="white", mew=1.2, label="SLF BLE logger, active"),
        Line2D([], [], ls="", marker="^", ms=7, mfc="#2c5f8a", mec="white", mew=1.2, label="GeoPrecision M-Log5W rock, active"),
        Line2D([], [], ls="", marker="o", ms=6, mfc="white", mec="#a33a1c", mew=1.3, label="suspended (unsafe access)"),
        Line2D([], [], ls="", marker="o", ms=6, mfc="white", mec="#2c5f8a", mew=1.3, label="never read out"),
        Line2D([], [], ls="", marker="o", ms=6, mfc="#8b8b84", mec="white", mew=1.2, label="lost"),
        Line2D([], [], ls="", marker="*", ms=10, mfc="#a33a1c", mec="white", mew=.8, label="Nissai AWS"),
    ]
    ax.legend(handles=hand, loc="lower right", fontsize=6, frameon=True, framealpha=.9,
              edgecolor="none", borderpad=.6)
    ax.set_title("Nissai ground-surface-temperature loggers", fontsize=9, color=INK,
                 loc="left", fontweight="bold")
    furniture(ax, 1)
    credit(ax, "Contours 50 m, labelled every 250 m. WP44/47/48 and WP100 sit within ~100 m on the ridge.")
    fig.tight_layout()
    p = os.path.join(OUT, "nissai_gst_map.png")
    fig.savefig(p, dpi=250, facecolor="white", bbox_inches="tight", pad_inches=.08); plt.close(fig)
    print(p)


# ──────────────────────────────── AWS topo ────────────────────────────────
def locator(fig, lon, lat):
    import cartopy.crs as ccrs, cartopy.feature as cf
    fig.canvas.draw()
    b = fig.axes[0].get_position()
    wid = b.width * .27
    hgt = wid * (fig.get_figwidth() / fig.get_figheight()) * (9.5 / 20.5)
    ax = fig.add_axes([b.x0 + .008, b.y1 - hgt - .012, wid, hgt], projection=ccrs.PlateCarree())
    ax.set_extent([60, 80.5, 35, 44.5])
    ax.add_feature(cf.LAND, facecolor="#efece4")
    ax.add_feature(cf.LAKES, facecolor="#cfdde8", edgecolor="none")
    ax.add_feature(cf.BORDERS, linewidth=.4, edgecolor=MUTED)
    ax.plot(lon, lat, marker="s", ms=5, mfc="#a33a1c", mec="white", mew=.7,
            transform=ccrs.PlateCarree())
    for x, y, t in [(70.0, 37.3, "TAJIKISTAN"), (74.5, 41.5, "KYRGYZSTAN"),
                    (64, 41.3, "UZBEKISTAN"), (66.5, 35.6, "AFGHANISTAN")]:
        ax.text(x, y, t, fontsize=4.2, color=MUTED, ha="center", transform=ccrs.PlateCarree())
    ax.spines["geo"].set_edgecolor(MUTED); ax.spines["geo"].set_linewidth(.5)


def aws_map():
    aws = site("AWS")
    lon0, lat0 = aws[0], aws[1]
    w, e, s, n = lon0 - .040, lon0 + .040, lat0 - .020, lat0 + .016
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    basemap(ax, w, e, s, n, minor=25, major=100)

    stakes = [x for x in SITES if x[4] in ("stake", "stake_acc") and w < x[0] < e and s < x[1] < n]
    ax.plot([x[0] for x in stakes], [x[1] for x in stakes], ls="", marker="o", ms=3.4,
            mfc="white", mec=INK, mew=.7, zorder=4)
    if stakes:
        lo = min(stakes, key=lambda x: x[1])
        label(ax, lo[0], lo[1], "glacier mass-balance stakes", 0, -9, "center",
              fontsize=5.8, color=MUTED, style="italic")
    ridge = ("WP44", "WP47", "WP48")  # within ~100 m of WP100; labelled as a group
    for x in SITES:
        wp = x[3].split()[0]
        if x[4] in ("logger_ble", "logger_geop") and w < x[0] < e and s < x[1] < n and x[5] != "lost":
            geo = x[4] == "logger_geop"
            ax.plot(x[0], x[1], marker="^" if geo else "o", ms=6 if geo else 4.2,
                    mfc="#2c5f8a", mec="white", mew=.9, zorder=5 + geo)
            if wp in ridge:
                continue
            label(ax, x[0], x[1], "WP100 + WP44/47/48" if geo else wp,
                  5, -6 if geo else 3, fontsize=5.8)
    ax.plot(lon0, lat0, marker="*", ms=17, mfc="#a33a1c", mec="white", mew=1, zorder=7)
    ax.annotate(f"Nissai AWS\n{lat0:.5f} N, {lon0:.5f} E · {aws[2]} m", (lon0, lat0),
                xytext=(-40, -38), textcoords="offset points", ha="right", va="top",
                fontsize=7, fontweight="bold", color=INK, linespacing=1.3, zorder=8,
                bbox=dict(boxstyle="round,pad=.35", fc="white", ec="none", alpha=.92),
                arrowprops=dict(arrowstyle="-", color=INK, lw=.7, shrinkB=7))
    ax.set_title("Nissai automatic weather station — Campbell CR1000X, since 2021",
                 fontsize=9, color=INK, loc="left", fontweight="bold")
    furniture(ax, .5)
    try:
        locator(fig, lon0, lat0)
    except Exception as ex:  # cartopy data unavailable offline
        print("locator inset skipped:", ex)
    credit(ax, "Contours 25 m, labelled every 100 m. Blue: GST loggers (triangle = GeoPrecision).")
    p = os.path.join(OUT, "nissai_aws_topo.png")
    fig.savefig(p, dpi=250, facecolor="white", bbox_inches="tight", pad_inches=.08); plt.close(fig)
    print(p)


if __name__ == "__main__":
    gst_map()
    aws_map()
