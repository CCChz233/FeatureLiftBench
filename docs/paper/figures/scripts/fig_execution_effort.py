"""RQ2: post-checkpoint token and model-call distributions (current Fig. 4)."""
import csv
from pathlib import Path
import sys

import numpy as np
from figure_common import BLUE, INK, finish, run_single
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from execution_effort import load_analysis
import paper_style


def draw_execution_effort():
    data = load_analysis()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
    fig.subplots_adjust(left=.085, right=.985, bottom=.21, top=.87, wspace=.30)
    rng = np.random.default_rng(20260917)
    for ax, metric, scale, title, ylabel in (
        (axes[0], 'post_fraction', 100, '(a) Token fraction', 'Post-pass tokens (%)'),
        (axes[1], 'post_calls', 1, '(b) Model calls', 'Subsequent calls'),
    ):
        for i, summary in enumerate(data['summaries']):
            values = np.array([r[metric]*scale for r in data['point_data']
                               if r['configuration'] == summary['configuration']])
            if not len(values):
                ax.text(i, .48, '—', transform=ax.get_xaxis_transform(), ha='center',
                        va='center', fontsize=12, color='#A5ADB3')
                continue
            if len(values) >= 10:
                ax.boxplot([values], positions=[i], widths=.48, patch_artist=True,
                           showfliers=False,
                           boxprops=dict(facecolor='#DCEBF4', edgecolor=BLUE, linewidth=.8),
                           medianprops=dict(color=INK, linewidth=1.5),
                           whiskerprops=dict(color=BLUE, linewidth=.8),
                           capprops=dict(color=BLUE, linewidth=.8))
            ax.scatter(i+rng.uniform(-.17, .17, len(values)), values,
                       s=12 if len(values) < 10 else 7, color=BLUE,
                       alpha=.85 if len(values) < 10 else .37, linewidths=0, zorder=3)
            if len(values) < 10:
                ax.hlines(np.median(values), i-.23, i+.23, color=INK, linewidth=1.4, zorder=4)
        ax.set_xticks(range(6), [f"{r['short']}\n$n$={r['checkpoint_n']}" for r in data['summaries']])
        ax.tick_params(axis='x', length=0, pad=6, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        ax.set_xlim(-.6, 5.6)
        ax.set_title(title, loc='left', fontweight='bold', fontsize=9, pad=10)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.grid(axis='y', color='#E9EDF0', linewidth=.5)
        ax.spines[['top', 'right']].set_visible(False)
        ax.spines[['left', 'bottom']].set_color('#8C969F')
    axes[0].set_ylim(0, 100)
    axes[0].set_yticks([0, 25, 50, 75, 100])
    axes[1].set_ylim(0, max(r['post_calls'] for r in data['point_data'])*1.08)
    axes[1].yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    output = Path(paper_style.OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)
    fields = ('run_id', 'configuration', 'task_id', 'post_fraction', 'post_calls')
    with (output/'fig_execution_effort_points.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(data['point_data'])
    finish(fig, 'fig_execution_effort')


if __name__ == '__main__':
    run_single(draw_execution_effort, __doc__)
