#!/usr/bin/env python3
"""Overview figure for the Sangvor AWS year. Small multiples: one measure per
panel, shared time axis, no dual axes."""
import sys, warnings
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
warnings.filterwarnings('ignore')

S1, S2 = '#2a78d6', '#eb6834'          # validated categorical slots 1,2
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#d8d7d2'

def qc(s, lo, hi):
    s = pd.to_numeric(s, errors='coerce')
    return s.where((s >= lo) & (s <= hi))

df = pd.read_parquet(sys.argv[1])
df = df.set_index('TIMESTAMP').sort_index()

# Drop partial-write records recovered at run boundaries: a station at this
# altitude never reads near-zero absolute pressure, so it flags a torn record.
p = pd.to_numeric(df.PressureBarometricAbsolute, errors='coerce')
torn = ~p.between(500, 800)
if torn.any(): print(f'dropping {int(torn.sum())} torn record(s)')
df = df[~torn]

# Break every series across sampling gaps so no line is drawn through them.
gaps = df.index.to_series().diff() > pd.Timedelta('30min')
if gaps.any():
    blanks = pd.DataFrame(np.nan, index=df.index[gaps] - pd.Timedelta('1s'),
                          columns=df.columns)
    df = pd.concat([df, blanks]).sort_index()
    print(f'inserted {len(blanks)} line break(s)')

panels = [
    ('Air temperature', '°C',
     [('CS215', qc(df.TemperatureAir_CS215, -60, 60), S1),
      ('HygroVUE10', qc(df.TemperatureAir_HygroVUE10, -60, 60), S2)]),
    ('Snow height', 'm',
     [('Laser', qc(df.SnowHeight_Laser, -200, 5000) / 1000.0, S1)]),
    ('Wind speed', 'm s⁻¹',
     [('Propeller, scalar mean', qc(df.WindSpeedScalMean_Prop, 0, 80), S1),
      ('ClimaVUE, gust max', qc(df.WindSpeedMax_ClimaVUE, 0, 80), S2)]),
    ('Blowing-snow particle flux', 'g m⁻² s⁻¹',
     [('FlowCapt FC4, mean', qc(df.SnowPartFluxAvg_FC4, 0, 500), S1)]),
    ('Shortwave radiation', 'W m⁻²',
     [('Incoming', qc(df.ISWR, -50, 1600), S1),
      ('Reflected', qc(df.RSWR, -50, 1600), S2)]),
    ('Longwave radiation', 'W m⁻²',
     [('Incoming', qc(df.ILWR, 0, 600), S1),
      ('Outgoing', qc(df.OLWR, 0, 600), S2)]),
    ('Relative humidity', '%',
     [('CS215', qc(df.RelativeHumidity_CS215, 0, 100), S1)]),
    ('Barometric pressure', 'hPa',
     [('Absolute', qc(df.PressureBarometricAbsolute, 500, 800), S1)]),
]

fig, axes = plt.subplots(len(panels), 1, figsize=(13, 2.05*len(panels)),
                         sharex=True, facecolor='#fcfcfb')
fig.subplots_adjust(hspace=0.30, left=0.075, right=0.825, top=0.955, bottom=0.05)

# the outage, from the coverage analysis
gap = (pd.Timestamp('2025-09-03 23:50'), pd.Timestamp('2025-09-29 12:10'))

for ax, (title, unit, series) in zip(axes, panels):
    ax.set_facecolor('#fcfcfb')
    ax.axvspan(*gap, color='#000000', alpha=0.055, lw=0, zorder=0)
    for name, s, col in series:
        ax.plot(s.index, s.values, lw=0.45, color=col, label=name,
                solid_capstyle='round', zorder=3)
    ax.set_ylabel(unit, color=MUTED, fontsize=8.5)
    ax.set_title(title, loc='left', color=INK, fontsize=10.5, pad=4, fontweight='medium')
    ax.grid(True, axis='y', color=GRID, lw=0.6, alpha=0.8, zorder=1)
    ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        ax.spines[sp].set_color(GRID); ax.spines[sp].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=8, length=3, width=0.7)
    # direct labels to the right, replacing a legend box
    for i, (name, s, col) in enumerate(series):
        ax.text(1.008, 0.90 - 0.20*i, name, transform=ax.transAxes,
                color=col, fontsize=8.2, va='top', ha='left')
    n = int(sum(s.notna().sum() for _, s, _ in series))
    ax.text(1.008, 0.06, f'n={n:,}', transform=ax.transAxes, color=MUTED,
            fontsize=7, ha='left', va='bottom')

axes[0].text(gap[0] + (gap[1]-gap[0])/2, axes[0].get_ylim()[1],
             'station outage\n25.5 d', ha='center', va='top',
             fontsize=7.5, color=MUTED, linespacing=1.25)

ax = axes[-1]
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax.set_xlim(df.index.min(), df.index.max())

fig.suptitle('Sangvor automatic weather station — Tajikistan, 2025–26',
             x=0.075, y=0.992, ha='left', fontsize=14, color=INK, fontweight='semibold')
fig.text(0.075, 0.974,
         f'CR1000X · Meteodata_Entire · 10-minute · {df.index.min():%Y-%m-%d} to '
         f'{df.index.max():%Y-%m-%d} · {len(df):,} records · 93.1% complete · '
         'shaded = no data · sensor error codes masked',
         ha='left', fontsize=8.5, color=MUTED)
fig.savefig(sys.argv[2], dpi=170, facecolor='#fcfcfb', bbox_inches='tight')
print('wrote', sys.argv[2])
