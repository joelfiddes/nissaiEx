#!/usr/bin/env python3
"""Glacier thermistor string overview: profile heatmap + power record.

Temperatures are encoded with a single-hue sequential ramp: every post-
deployment reading sits at or below the melting point, so the quantity is
"how far below 0 C", a magnitude, not a polarity.
"""
import sys, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import warnings; warnings.filterwarnings('ignore')

SURFACE, INK, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#d8d7d2'
BLUE = ['#cde2fb','#9ec5f4','#6da7ec','#3987e5','#256abf','#184f95','#0d366b']
CMAP = LinearSegmentedColormap.from_list('ice', BLUE[::-1])   # dark = coldest
CRITICAL = '#d03b3b'

src, out = sys.argv[1], sys.argv[2]
d = pd.read_csv(src, skiprows=[0,2,3], header=0, na_values=['NAN'], low_memory=False)
d['TIMESTAMP'] = pd.to_datetime(d['TIMESTAMP'], errors='coerce')
d = d.dropna(subset=['TIMESTAMP']).sort_values('TIMESTAMP').set_index('TIMESTAMP')
for c in d.columns: d[c] = pd.to_numeric(d[c], errors='coerce')

DEPLOY = pd.Timestamp('2025-09-05')
d = d[d.index >= DEPLOY]                      # drop pre-deployment storage
chans = [f'Temp{i}_Avg' for i in range(1, 9)]

# regular hourly grid so the outage renders as a true blank, not an interpolation
grid = pd.date_range(d.index.min().floor('h'), d.index.max().ceil('h'), freq='h')
g = d.reindex(grid)
Z = np.ma.masked_invalid(g[chans].to_numpy().T)

fig = plt.figure(figsize=(13, 7.2), facecolor=SURFACE)
# dedicated colorbar column: a colorbar attached with ax= would shrink the top
# axes only, breaking horizontal alignment with the shared-x panel below.
gs = fig.add_gridspec(2, 2, height_ratios=[2.35, 1], width_ratios=[60, 1],
                      hspace=0.30, wspace=0.018,
                      left=0.075, right=0.90, top=0.885, bottom=0.085)

# --- profile heatmap -------------------------------------------------------
ax  = fig.add_subplot(gs[0, 0]); ax.set_facecolor(SURFACE)
cax = fig.add_subplot(gs[0, 1])
m = ax.pcolormesh(grid, np.arange(1, 9), Z, cmap=CMAP, vmin=-9.5, vmax=0,
                  shading='nearest')
ax.set_ylim(8.5, 0.5)                          # channel 1 at top
ax.set_yticks(np.arange(1, 9))
ax.set_yticklabels([f'Temp{i}' for i in range(1, 9)], fontsize=8.5)
ax.set_ylabel('thermistor channel', color=MUTED, fontsize=9)
ax.set_title('Ice temperature profile', loc='left', color=INK, fontsize=11,
             pad=5, fontweight='medium')
cb = fig.colorbar(m, cax=cax)
cb.set_label('°C', color=MUTED, fontsize=9)
cb.ax.tick_params(colors=MUTED, labelsize=8); cb.outline.set_visible(False)
ax.text(1.0, 1.035, 'blank = no data', transform=ax.transAxes, ha='right',
        color=MUTED, fontsize=8)

# --- power -----------------------------------------------------------------
ax2 = fig.add_subplot(gs[1, 0], sharex=ax); ax2.set_facecolor(SURFACE)
b = g['BattV_Avg']
ax2.plot(b.index, b.values, lw=0.9, color=BLUE[4], solid_capstyle='round')
ax2.axhline(9.6, lw=1.0, color=CRITICAL, ls=(0, (4, 3)), zorder=1)
ax2.text(grid[0], 9.6, ' cutoff ~9.6 V', color=CRITICAL, fontsize=8,
         va='bottom', ha='left')
ax2.set_ylabel('V', color=MUTED, fontsize=9)
ax2.set_title('Battery voltage', loc='left', color=INK, fontsize=11, pad=5,
              fontweight='medium')

stop  = pd.Timestamp('2025-12-16 17:00')
start = pd.Timestamp('2026-08-05 11:00')
for a in (ax, ax2):
    a.grid(True, axis='y', color=GRID, lw=0.6, alpha=0.7); a.set_axisbelow(True)
    for sp in ('top', 'right'): a.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        a.spines[sp].set_color(GRID); a.spines[sp].set_linewidth(0.8)
    a.tick_params(colors=MUTED, labelsize=8, length=3, width=0.7)
    a.axvline(stop,  lw=0.9, color=CRITICAL, alpha=0.8)
    a.axvline(start, lw=0.9, color=CRITICAL, alpha=0.8)

ax2.annotate('battery exhausted\n2025-12-16', xy=(stop, 10.2),
             xytext=(-6, 0), textcoords='offset points', ha='right', va='center',
             fontsize=8, color=CRITICAL, linespacing=1.3)
ax2.annotate('restarted\n2026-08-05', xy=(start, 10.2),
             xytext=(6, 0), textcoords='offset points', ha='left', va='center',
             fontsize=8, color=CRITICAL, linespacing=1.3)
mid = stop + (start - stop) / 2
ax.text(mid, 4.5, '232 days lost', ha='center', va='center', fontsize=10,
        color=CRITICAL, fontweight='medium')

ax2.xaxis.set_major_locator(mdates.MonthLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax2.set_xlim(grid[0], grid[-1])
plt.setp(ax.get_xticklabels(), visible=False)

n = int(g[chans].notna().any(axis=1).sum())
fig.suptitle('Nissai glacier thermistor station — CR350', x=0.075, y=0.975,
             ha='left', fontsize=14, color=INK, fontweight='semibold')
fig.text(0.075, 0.935,
         f'Installed 2025-09-05 · hourly · {n:,} of {len(grid):,} hours recorded '
         f'({100*n/len(grid):.1f}%) · channel depths not recorded',
         ha='left', fontsize=8.5, color=MUTED)
fig.savefig(out, dpi=170, facecolor=SURFACE, bbox_inches='tight')
print('wrote', out)
