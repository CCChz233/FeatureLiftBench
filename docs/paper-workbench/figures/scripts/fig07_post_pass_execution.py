"""Fig. 7: post-checkpoint token and model-response distributions.

Produces two independent panels without in-image titles:

    fig07a_post_pass_tokens.pdf/png
    fig07b_post_pass_responses.pdf/png

Panel titles belong in the LaTeX caption.
"""
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


def _draw_panel(data, *, metric, scale, ylabel, points_key, count_key, name,
                ylim=None, yticks=None, integer_yaxis=False):
    fig, ax = plt.subplots(figsize=(3.50, 2.55))
    fig.subplots_adjust(left=.18, right=.98, bottom=.22, top=.97)
    rng = np.random.default_rng(20260917)
    for i, summary in enumerate(data['summaries']):
        values = np.array([r[metric] * scale for r in data[points_key]
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
        ax.scatter(i + rng.uniform(-.17, .17, len(values)), values,
                   s=12 if len(values) < 10 else 7, color=BLUE,
                   alpha=.85 if len(values) < 10 else .37, linewidths=0, zorder=3)
        if len(values) < 10:
            ax.hlines(np.median(values), i - .23, i + .23, color=INK, linewidth=1.4, zorder=4)
    ax.set_xticks(range(6), [f"{r['short']}\n$n$={r[count_key]}" for r in data['summaries']])
    ax.tick_params(axis='x', length=0, pad=6, labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.set_xlim(-.6, 5.6)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.grid(axis='y', color='#E9EDF0', linewidth=.5)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#8C969F')
    if ylim is not None:
        ax.set_ylim(*ylim)
    if yticks is not None:
        ax.set_yticks(yticks)
    if integer_yaxis:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=5, integer=True))
    finish(fig, name)


def draw_execution_effort():
    data = load_analysis()
    output = Path(paper_style.OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)
    fields = ('run_id', 'configuration', 'task_id', 'include_checkpoint',
              'include_response', 'post_fraction', 'post_responses')
    with (output / 'fig07_post_pass_points.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore',
                                lineterminator='\n')
        writer.writeheader()
        writer.writerows(data['response_point_data'])
    _draw_panel(
        data,
        metric='post_fraction',
        scale=100,
        ylabel='Post-pass tokens (%)',
        points_key='point_data',
        count_key='checkpoint_n',
        name='fig07a_post_pass_tokens',
        ylim=(0, 100),
        yticks=[0, 25, 50, 75, 100],
    )
    response_max = max(r['post_responses'] for r in data['response_point_data'])
    _draw_panel(
        data,
        metric='post_responses',
        scale=1,
        ylabel='Subsequent responses',
        points_key='response_point_data',
        count_key='response_n',
        name='fig07b_post_pass_responses',
        ylim=(0, response_max * 1.08),
        integer_yaxis=True,
    )


if __name__ == '__main__':
    run_single(draw_execution_effort, __doc__)
