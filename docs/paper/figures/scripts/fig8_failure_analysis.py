"""Source-exposed failure classifications; figure numbering follows LaTeX order."""
import csv
from pathlib import Path
import sys

from matplotlib import pyplot as plt
from matplotlib.patches import Patch

from figure_common import finish, run_single
import paper_style

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from failure_analysis import counts

ORDER = ('contract_api_completion', 'dependency_closure', 'behavior_drift',
         'packaging_modularization', 'localization', 'unknown')
LABELS = ('API completion', 'Dependency closure', 'Behavior drift',
          'Packaging', 'Localization', 'Unknown')
COLORS = ('#0072B2', '#E69F00', '#D55E00', '#009E73', '#CC79A7', '#BDBDBD')


def draw_failure_analysis():
    data = counts()
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    fig.subplots_adjust(left=.18, right=.985, bottom=.31, top=.98)
    plot_rows = []
    for i, row in enumerate(data['by_model']):
        left = 0
        for key, color in zip(ORDER, COLORS):
            n = row['counts'][key]
            percent = 100 * n / row['n']
            if n:
                ax.barh(i, percent, left=left, height=.60, color=color)
            left += percent
            plot_rows.append({'model': row['model'], 'category': key, 'n': n,
                              'denominator': row['n'], 'percent': percent})
    ax.set_yticks(range(6), [f"{r['short']} ($n$={r['n']})" for r in data['by_model']])
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel('Share of classified failures (%)')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(handles=[Patch(facecolor=color, label=label)
                       for key, label, color in zip(ORDER, LABELS, COLORS)
                       if data['pooled'][key]],
              loc='upper center', bbox_to_anchor=(.5, -.25), ncol=3,
              frameon=False, fontsize=8, columnspacing=1.5)
    output = Path(paper_style.OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'fig8_plot_data.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(plot_rows[0]))
        writer.writeheader()
        writer.writerows(plot_rows)
    finish(fig, 'fig8_failure_analysis')


if __name__ == '__main__':
    run_single(draw_failure_analysis, __doc__)
