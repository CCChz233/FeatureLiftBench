"""Fig. 4: grouped vertical bars for functional pass rates by lift type.

Each configuration has three independent bars with a common zero baseline.
Colors identify Direct / Adapted / Composite; task denominators are explicit
in the legend. The plot describes observed categories, not causal difficulty.
Use preview_results.py --only structure to render without changing paper files.
"""
from pathlib import Path
import sys
import numpy as np
from figure_common import finish, run_single, INK
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
import redraw_data

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'writing'))
from results_visuals import evidence

FIGURE_SIZE = (7.2, 3.35)
BAR_WIDTH = .19
TYPE_STYLES = (
    ('Direct', '#0072B2', -.23),
    ('Adapted', '#E69F00', 0),
    ('Composite', '#009E73', .23),
)
GRID_COLOR = '#E7EBEF'
AXIS_COLOR = '#89959D'


def build_figure():
    """Build the grouped bar chart without writing images or derived data."""
    data = evidence()
    groups = data['structure'][:3]
    assert [g['name'] for g in groups] == [s[0] for s in TYPE_STYLES]
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    fig.subplots_adjust(left=.095, right=.98, bottom=.13, top=.875)
    positions = np.arange(len(data['models']))

    for group, (_, color, offset) in zip(groups, TYPE_STYLES):
        ax.bar(positions + offset, group['rates'], width=BAR_WIDTH,
                bottom=0, color=color, edgecolor='white', linewidth=.35, zorder=3)

    labels = [model['short'] for model in data['models']]
    ax.set(xticks=positions, xticklabels=labels,
           ylim=(0, 100), yticks=[0, 20, 40, 60, 80, 100],
           xlim=(-.55, len(positions) - .45), ylabel='Functional pass rate (%)')
    ax.tick_params(axis='x', length=0, pad=8, labelsize=9, labelcolor=INK)
    ax.tick_params(axis='y', length=3, pad=4, labelsize=8,
                   colors=AXIS_COLOR, labelcolor=INK)
    ax.yaxis.label.set_color(INK)
    ax.yaxis.label.set_size(8.5)
    ax.yaxis.labelpad = 6
    ax.set_axisbelow(True)
    ax.grid(axis='y', color=GRID_COLOR, linewidth=.55)
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(AXIS_COLOR)
        ax.spines[spine].set_linewidth(.7)

    handles = [Patch(facecolor=color, edgecolor='none',
                     label=group['name'])
               for group, (_, color, _) in zip(groups, TYPE_STYLES)]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.535, .995),
               ncol=3, fontsize=8, columnspacing=1.8, handlelength=1.1,
               handleheight=.8, handletextpad=.6, frameon=False, labelcolor=INK)

    payload = {
        'models': data['models'], 'groups': groups,
        'interpretation': 'Descriptive outcomes, not independent difficulty effects',
        'design': {'geometry': 'grouped_bar', 'bar_width': BAR_WIDTH,
                   'type_offsets': [style[2] for style in TYPE_STYLES],
                   'baseline': 0, 'stacked': False, 'short_model_labels': True,
                   'exact_value_labels': False},
    }
    sources = [redraw_data.ROOT / source['path'] for source in data['sources']]
    return fig, payload, sources


def draw_structure():
    fig, payload, sources = build_figure()
    redraw_data.export('fig4_structure', payload, sources)
    finish(fig, 'fig4_structure')


if __name__ == '__main__':
    run_single(draw_structure, __doc__)
