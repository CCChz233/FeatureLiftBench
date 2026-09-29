"""Render the evidence-qualified subtype preview; never sync to the manuscript."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

import paper_style
from figure_common import render

DATA = Path(__file__).resolve().parents[2] / 'data/failure_subtypes_20260918'
SUBTYPES = [
    ('call', 'Call\nmismatch'),
    ('result', 'Incorrect\nresult'),
    ('parse', 'Parsing /\nformatting'),
    ('validation', 'Validation\n& errors'),
    ('state', 'State /\ncontrol flow'),
]
OTHER = [
    ('contract_api_completion', 'Missing\nAPI'),
    ('dependency_closure', 'Missing\ndependency'),
    ('packaging_modularization', 'Packaging'),
]


def draw():
    data = json.loads((DATA / 'summary.json').read_text())
    source = DATA / 'failure_root_cause_annotations.csv'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == data['annotations_sha256']
    frozen = DATA.parent / 'failure_analysis_20260916/classifications.csv'
    assert hashlib.sha256(frozen.read_bytes()).hexdigest() == data['frozen_classifications_sha256']
    ledger = list(csv.DictReader(source.open()))
    assert len(ledger) == len({(r['model'], r['task_id']) for r in ledger}) == 201
    models = data['by_model']
    cells, values = [], []
    for model in models:
        reviewed = [r for r in ledger if r['model'] == model['model']]
        row = []
        for key, label in SUBTYPES + OTHER:
            if key in model['subtype_counts']:
                count = sum(r['plot_eligible'] == '1' and r['behavior_subtype'] == key for r in reviewed)
                assert count == model['subtype_counts'][key]
                tier = 'L1_assistant_subtype'
            else:
                count = model['counts'][key]
                tier = 'original_classification_carried_forward'
            percent = 100 * count / model['n']
            row.append(percent)
            cells.append({'model': model['model'], 'category': key, 'count': count,
                          'denominator': model['n'], 'percent': percent, 'evidence': tier})
        assert sum(c['count'] for c in cells if c['model'] == model['model']) + model['subtype_pending'] + model['counts']['unknown'] == model['n']
        values.append(row)
    values = np.asarray(values)
    assert values.max() <= 25
    ink, muted = '#243746', '#687783'
    fig = plt.figure(figsize=(7.4, 3.55))
    ax = fig.add_axes((.155, .285, .680, .475))
    cmap = LinearSegmentedColormap.from_list('profile', ['#F3F6F8', '#CFDFEA', '#88B3CE', '#367CAB', '#164F77'])
    im = ax.imshow(values, cmap=cmap, vmin=0, vmax=25, aspect='auto', interpolation='nearest')
    ax.spines[:].set_visible(False)
    ax.set_xticks([])
    for j, (_, label) in enumerate(SUBTYPES + OTHER):
        fig.text(.155 + .680 * (j + .5) / 8, .810, label,
                 ha='center', va='center', fontsize=7.8, color=ink)
    ax.set_yticks([])
    ax.set_xticks(np.arange(-.5, 8), minor=True)
    ax.set_yticks(np.arange(-.5, 6), minor=True)
    ax.grid(which='minor', linewidth=2.6, color='white')
    ax.tick_params(which='minor', length=0, bottom=False, top=False, left=False)
    ax.axvline(4.5, color='white', linewidth=9)
    for i, model in enumerate(models):
        ax.text(-.20, i, model['short'], transform=ax.get_yaxis_transform(),
                ha='left', va='center', color=ink, fontsize=9)
        ax.text(-.025, i, model['n'], transform=ax.get_yaxis_transform(),
                ha='right', va='center', color=muted, fontsize=8)
        ax.text(1.105, i, model['subtype_pending'], transform=ax.get_yaxis_transform(),
                ha='center', va='center', color=muted, fontsize=8.5)
        for j in range(8):
            value = values[i, j]
            ax.text(j, i, f'{value:.1f}' if value else '0', ha='center', va='center',
                    fontsize=9, color='white' if value >= 16 else muted if value == 0 else ink)
    fig.text(.019, .95, 'Failure profiles', fontsize=12, weight='bold', color=ink)
    fig.text(.955, .953, 'REVIEW PREVIEW · L1', ha='right', color=muted, fontsize=8)
    for left, right, label in [(.155, .58, 'Behavior drift: assigned subtypes'),
                                (.58, .835, 'Original categories')]:
        fig.text((left + right) / 2, .895, label, ha='center', color=ink, fontsize=8.5)
        fig.add_artist(plt.Line2D([left + .005, right - .005], [.873, .873],
                                 transform=fig.transFigure, color='#BAC6CE', linewidth=.7))
    fig.text(.137, .798, '$n$', ha='right', fontsize=8, color=muted)
    fig.text(.906, .79, 'To review\n(count)', ha='center', fontsize=8, color=muted)
    fig.text(.155, .205, 'Cells: % of the original within-model failure total ($n$)',
             fontsize=8, color=ink)
    cax = fig.add_axes((.64, .145, .195, .022))
    colorbar = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[0, 10, 20, 25])
    colorbar.outline.set_visible(False)
    colorbar.ax.tick_params(length=0, pad=3, labelsize=7, colors=muted)
    fig.text(.856, .155, '%', fontsize=8, color=muted, va='center')
    fig.text(.155, .143, '74 / 201 behavior cases assigned; 127 pending.', fontsize=8, color=muted)
    fig.text(.019, .055, 'Pending cases and 1 original unclassified case are not plotted; denominators are unchanged.',
             fontsize=7.5, color=muted)
    fig.text(.019, .017, 'Zeros mean no currently assigned cases. Subtypes are a first pass, not independent human review.',
             fontsize=7.5, color=muted)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    for text in fig.findobj(plt.Text):
        if not text.get_visible() or not text.get_text():
            continue
        box = text.get_window_extent(renderer)
        assert box.x0 >= bounds.x0 - 1 and box.x1 <= bounds.x1 + 1, text.get_text()
        assert box.y0 >= bounds.y0 - 1 and box.y1 <= bounds.y1 + 1, text.get_text()
    output = Path(paper_style.OUTPUT_DIR)
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'fig6_subtype_plot_data.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=cells[0])
        writer.writeheader()
        writer.writerows(cells)
    for path in paper_style.save_figure(fig, 'fig6_failure_profile_heatmap', formats=('pdf', 'svg', 'png')):
        print(path)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path,
                        default=paper_style.FIGURES_DIR / 'output/fig6_subtypes')
    args = parser.parse_args()
    render([draw], args.output_dir)
