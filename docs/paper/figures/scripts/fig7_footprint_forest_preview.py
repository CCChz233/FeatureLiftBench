"""Current Fig. 8: task-adjusted footprint estimates as two forest panels.

Historical filename retained. Statistics live in fig7_adjusted_analysis.py.
"""
from pathlib import Path
import numpy as np
from figure_common import finish, run_single, BLUE, INK
from matplotlib import pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
import redraw_data
from fig7_adjusted_analysis import analyze, write_outputs

RRES_LIM = (.4, 2.1)
COPY_LIM = (-40, 40)


def build_figure():
    data, _ = analyze()
    rows = data['analyses']['task_bootstrap']['rows']
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    fig.subplots_adjust(left=.09, right=.975, bottom=.21, top=.86, wspace=.23)
    positions = np.arange(len(rows))
    panels = (
        (axes[0], 'rres_ratio', '(a) Implementation size', 1, RRES_LIM,
         [.5, 1, 2], ['0.5×', '1×', '2×'], 'Task-adjusted RRES ratio'),
        (axes[1], 'copy_pp', '(b) Source overlap', 0, COPY_LIM,
         [-40, -20, 0, 20, 40], ['−40', '−20', '0', '+20', '+40'], 'Task-adjusted Copy (pp)'),
    )
    axes[0].set_xscale('log', base=2)
    for ax, metric, title, center, limits, ticks, labels, xlabel in panels:
        estimates = np.array([r[metric] for r in rows])
        bounds = np.array([r[metric + '_ci'] for r in rows])
        assert bounds.min() > limits[0] and bounds.max() < limits[1]
        ax.axvline(center, color='#87939D', lw=.9, ls=(0, (3, 3)), zorder=2)
        ax.hlines(positions, bounds[:, 0], bounds[:, 1], color=BLUE, lw=1.8, zorder=3)
        ax.scatter(estimates, positions, s=30, color=BLUE, edgecolors='white', linewidths=.65, zorder=4)
        ax.set_xlim(limits)
        ax.set_ylim(5.6, -.6)
        ax.xaxis.set_major_locator(FixedLocator(ticks))
        ax.xaxis.set_major_formatter(FixedFormatter(labels))
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_yticks(positions, [r['short'] for r in rows])
        ax.set_title(title, loc='left', fontsize=9, fontweight='bold', pad=12)
        ax.set_xlabel(xlabel, fontsize=8, labelpad=7)
        ax.tick_params(axis='x', labelsize=8, length=3, color='#89959D')
        ax.tick_params(axis='y', labelsize=8.5, length=0, pad=8, labelcolor=INK)
        ax.grid(axis='y', color='#EEF0F2', linewidth=.6)
        ax.set_axisbelow(True)
        for spine in ('top', 'right', 'left'):
            ax.spines[spine].set_visible(False)
        ax.spines['bottom'].set_color('#89959D')
        ax.spines['bottom'].set_linewidth(.7)
    payload = dict(data, geometry='task_adjusted_forest',
                   caption_note=(
                       'Task-adjusted implementation footprints of 485 successful artifacts from 115 tasks '
                       'with at least two successful configurations. (a) Configuration effects from a '
                       'task fixed-effects model of log2(RRES), displayed as multiplicative size effects '
                       'on a logarithmic ratio axis. (b) Configuration effects for detected source overlap (Copy), '
                       'in percentage points. Points show estimates; horizontal intervals show pointwise 95% '
                       'task-cluster bootstrap percentile intervals from 10,000 accepted resamples. '
                       'Dashed lines mark the sum-to-zero configuration-effect centers (1× and 0 pp), '
                       'not an oracle-relative size reference. The analysis characterizes successful artifacts only.'),
                   figure_analysis='task_bootstrap', rres_limits=list(RRES_LIM), copy_limits=list(COPY_LIM))
    sources = [redraw_data.ROOT / s['path'] for s in data['sources']] + [Path(__file__).resolve()]
    return fig, payload, sources


def draw_matched():
    fig, payload, sources = build_figure()
    redraw_data.export('fig7_matched_footprint', payload, sources)
    data, draws = analyze()
    write_outputs(redraw_data.FIGURES_DIR / 'data', data, draws)
    (redraw_data.FIGURES_DIR / 'data/fig7_caption.md').write_text(payload['caption_note'] + '\n')
    finish(fig, 'fig7_matched_footprint')


if __name__ == '__main__':
    run_single(draw_matched, __doc__)
