"""Fig. 4: descriptive pass rates by lift type and entanglement mechanism.

Configurations, rather than task categories, occupy the horizontal axis.
Mechanism groups overlap; neither panel defines a calibrated difficulty scale.
"""
from pathlib import Path
import sys
import numpy as np
from figure_common import finish, run_single, INK
from matplotlib import pyplot as plt
import redraw_data

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'writing'))
from results_visuals import evidence

# Lift-type colors match the benchmark composition figure. Mechanisms have a
# separate palette and hatches so the two categorical encodings stay distinct.
PANELS = (
    ('(a) Pass rate by lift type', slice(0, 3),
     ['Direct', 'Adapted', 'Composite'], ['#0072B2', '#E69F00', '#009E73'], ['', '', '']),
    ('(b) Pass rate by entanglement mechanism', slice(3, 7),
     ['Code deps.', 'Data/state', 'Framework', 'Env./resources'],
     ['#5B5F97', '#9396BE', '#497D87', '#A5C7C6'], ['', '//', '', '//']),
)


def build_figure():
    data = evidence()
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.15), sharey=True)
    fig.subplots_adjust(left=.075, right=.985, bottom=.14, top=.73, wspace=.15)
    positions = np.arange(len(data['models']))
    designs = []
    for ax, (title, subset, labels, colors, hatches) in zip(axes, PANELS):
        groups = data['structure'][subset]
        step = .78 / len(groups)
        offsets = (np.arange(len(groups)) - (len(groups) - 1) / 2) * step
        width = step * .86
        for group, label, color, hatch, offset in zip(groups, labels, colors, hatches, offsets):
            ax.bar(positions + offset, group['rates'], width=width, bottom=0,
                   color=color, edgecolor='white', linewidth=.35, hatch=hatch,
                   label=label, zorder=3)
        ax.set(xticks=positions, xticklabels=[m['short'] for m in data['models']],
               ylim=(0, 100), yticks=np.arange(0, 101, 20), xlim=(-.55, 5.55))
        ax.set_title(title, loc='left', fontsize=8.3, fontweight='bold', y=1.30, pad=0)
        ax.legend(loc='lower left', bbox_to_anchor=(0, 1.015), ncol=2,
                  fontsize=7.3, columnspacing=1.2, handlelength=1.3,
                  handletextpad=.5, borderaxespad=0, frameon=False)
        ax.tick_params(axis='x', length=0, pad=7, labelsize=8, labelcolor=INK)
        ax.tick_params(axis='y', length=3, pad=4, labelsize=8, colors='#89959D', labelcolor=INK)
        ax.grid(axis='y', color='#E7EBEF', linewidth=.55)
        ax.set_axisbelow(True)
        for side in ('top', 'right'):
            ax.spines[side].set_visible(False)
        for side in ('left', 'bottom'):
            ax.spines[side].set_color('#89959D')
            ax.spines[side].set_linewidth(.7)
        designs.append(dict(groups=groups, offsets=offsets.tolist(), bar_width=width))
    axes[0].set_ylabel('Functional pass rate (%)', fontsize=8.5, labelpad=6)
    payload = dict(models=data['models'], groups=data['structure'],
                   interpretation='Descriptive category outcomes; mechanisms overlap; no independent difficulty effects',
                   design=dict(geometry='two_panel_grouped_bar', panels=designs, baseline=0, stacked=False))
    sources = [redraw_data.ROOT / source['path'] for source in data['sources']]
    return fig, payload, sources


def draw_structure():
    fig, payload, sources = build_figure()
    redraw_data.export('fig4_structure', payload, sources)
    finish(fig, 'fig4_structure')


if __name__ == '__main__':
    run_single(draw_structure, __doc__)
