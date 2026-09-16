"""Fig. 7: six-configuration task-adjusted footprint vertical bar plot with confidence intervals.

The historical filename is retained for compatibility. This is no longer a
Pro–Luna scatter. Analysis and bootstrap settings: fig7_adjusted_analysis.py.
Use preview_results.py --only footprint to avoid changing manuscript assets.
"""
from pathlib import Path
import numpy as np
from figure_common import finish, run_single, BLUE, INK
from matplotlib import pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
import redraw_data
from fig7_adjusted_analysis import analyze, write_outputs

RRES_LIM = (0, 2.0)
COPY_LIM = (-40, 40)


def build_figure():
    """Build both panels from task-bootstrap estimates, without writing files."""
    data, _ = analyze()
    rows = data['analyses']['task_bootstrap']['rows']
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.65), sharex=True)
    fig.subplots_adjust(left=.095, right=.98, bottom=.16, top=.87, wspace=.32)
    positions = np.arange(6)
    panels = (
        (axes[0], 'rres_ratio', '(a) Implementation size', 1, RRES_LIM,
         [0, .5, 1, 1.5, 2], ['0', '0.5×', '1×', '1.5×', '2×'], 'Task-adjusted RRES ratio'),
        (axes[1], 'copy_pp', '(b) Source overlap', 0, COPY_LIM,
         [-40, -20, 0, 20, 40], ['−40', '−20', '0', '+20', '+40'], 'Task-adjusted Copy (pp)'),
    )
    for ax, metric, title, center, limits, ticks, labels, ylabel in panels:
        estimates = np.array([r[metric] for r in rows])
        bounds = np.array([r[metric + '_ci'] for r in rows])
        assert bounds.min() > limits[0] and bounds.max() < limits[1]
        ax.axhline(center, color='#87939D', lw=.9, ls=(0, (3, 3)), zorder=4)
        ax.bar(positions, estimates, width=.56, bottom=0, color=BLUE,
               edgecolor='none', zorder=2)
        ax.vlines(positions, bounds[:, 0], bounds[:, 1], color=INK, lw=1, zorder=5)
        for end in (0, 1):
            ax.plot(positions, bounds[:, end], linestyle='none', marker='_',
                    markersize=6, markeredgewidth=1, color=INK, zorder=5)
        ax.set_ylim(limits)
        ax.set_xlim(-.55, 5.55)
        ax.yaxis.set_major_locator(FixedLocator(ticks))
        ax.yaxis.set_major_formatter(FixedFormatter(labels))
        ax.yaxis.set_minor_locator(NullLocator())
        ax.set_xticks(positions, [r['short'] for r in rows])
        ax.set_title(title, loc='left', fontsize=9, fontweight='bold', pad=12)
        ax.set_ylabel(ylabel, fontsize=8, labelpad=7)
        ax.tick_params(axis='y', labelsize=8, length=3, color='#89959D')
        ax.tick_params(axis='x', labelsize=8, length=0, pad=8)
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#EEF0F2', linewidth=.5)
        for spine in ('top', 'right'):
            ax.spines[spine].set_visible(False)
        ax.spines['bottom'].set_color('#89959D')
        ax.spines['bottom'].set_linewidth(.7)
        ax.spines['left'].set_color('#89959D')
        ax.spines['left'].set_linewidth(.7)
    payload = dict(data, geometry='task_adjusted_vertical_bars',
                   caption_note=('Task-adjusted successful-artifact footprints: (a) RRES ratios; '
                                 '(b) Copy differences in percentage points.'),
                   figure_analysis='task_bootstrap', rres_limits=list(RRES_LIM), copy_limits=list(COPY_LIM))
    return fig, payload, [redraw_data.ROOT / s['path'] for s in data['sources']] + [Path(__file__).resolve()]


def draw_matched():
    fig, payload, sources = build_figure()
    redraw_data.export('fig7_matched_footprint', payload, sources)
    data, draws = analyze()
    write_outputs(redraw_data.FIGURES_DIR / 'data', data, draws)
    (redraw_data.FIGURES_DIR / 'data/fig7_caption.md').write_text(payload['caption_note'] + '\n')
    finish(fig, 'fig7_matched_footprint')


if __name__ == '__main__':
    run_single(draw_matched, __doc__)
