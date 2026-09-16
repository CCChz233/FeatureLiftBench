"""Candidate Fig. 4: all 150 task outcomes across the six configurations.

Preview only: the default destination is output/task_success_matrix_preview/.
No manuscript, table, package, or existing figure asset is changed.
Tasks are ordered by descending success count, then ascending task ID.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from figure_common import render, finish, BLUE, INK
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.text import Text
import redraw_data

PAPER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAPER))
from paper_inputs import RESULTS, MODELS, SHORT, MODEL_RECORDS, read_csv, paper_task_ids, input_path

FAIL_COLOR = '#E7EBEF'
NAME = 'fig4_task_success_matrix'


def load_matrix():
    rows = read_csv(RESULTS)
    task_ids = paper_task_ids()
    assert len(rows) == 900
    cells = {(r['model'], r['task_id']): r['functional_pass'] for r in rows}
    assert len(cells) == 900
    assert set(cells) == {(m, t) for m in MODELS for t in task_ids}
    assert set(cells.values()) <= {'True', 'False'}
    success_count = {t: sum(cells[m, t] == 'True' for m in MODELS) for t in task_ids}
    order = sorted(task_ids, key=lambda t: (-success_count[t], t))
    matrix = np.array([[int(cells[m, t] == 'True') for t in order] for m in MODELS])
    groups = []
    offset = 0
    for k in range(6, -1, -1):
        n = sum(success_count[t] == k for t in order)
        groups.append(dict(passing_configurations=k, n=n, start=offset, end=offset+n))
        offset += n
    assert matrix.shape == (6, 150) and offset == 150
    assert matrix.sum(axis=1).tolist() == [115, 108, 102, 68, 63, 36]
    assert matrix.sum() == 492
    assert np.array_equal(matrix.sum(axis=0), [success_count[t] for t in order])
    assert [g['n'] for g in groups] == [17, 31, 36, 22, 9, 7, 28]
    payload = dict(
        task_order=order, outcome_matrix=matrix.tolist(), groups=groups,
        models=[dict(id=m, short=SHORT[m], display=MODEL_RECORDS[m]['display'],
                     passes=int(matrix[i].sum())) for i, m in enumerate(MODELS)],
        ordering='Descending number of successful configurations; ascending task ID within each group',
        encoding={'0': 'Fail', '1': 'Pass'},
        all_pass_tasks=groups[0]['n'], mixed_outcome_tasks=sum(g['n'] for g in groups[1:-1]),
        all_fail_tasks=groups[-1]['n'],
        caption=('Task-level functional success across six configurations on the same 150 tasks. '
                 'Each column denotes one task and each row one configuration. Blue cells denote '
                 'functional success; gray cells denote failure. Tasks are grouped by the number of '
                 'configurations that pass (6 to 0), with task IDs in ascending order within each group. '
                 'Group labels give the number passing out of six and the number of tasks. '
                 'These are observed outcomes, not predefined difficulty levels.'),
    )
    return matrix, payload


def build_figure():
    matrix, payload = load_matrix()
    fig, ax = plt.subplots(figsize=(7.2, 2.65))
    fig.subplots_adjust(left=.09, right=.985, bottom=.155, top=.70)
    mesh = ax.pcolormesh(np.arange(151), np.arange(7), matrix,
                        cmap=ListedColormap([FAIL_COLOR, BLUE]),
                        norm=BoundaryNorm([-.5, .5, 1.5], 2),
                        shading='flat', edgecolors='white', linewidth=.22,
                        antialiased=False, rasterized=False)
    ax.set(xlim=(0, 150), ylim=(6, 0), yticks=np.arange(6)+.5,
           yticklabels=[m['short'] for m in payload['models']], xticks=[], xlabel='Tasks')
    ax.tick_params(axis='y', length=0, pad=8, labelsize=9, labelcolor=INK)
    ax.xaxis.label.set_size(8.5)
    ax.xaxis.labelpad = 9
    for spine in ax.spines.values():
        spine.set_visible(False)
    for y in range(1, 6):
        ax.axhline(y, color='white', lw=1.4)
    for group in payload['groups']:
        if not group['n']:
            continue
        left, right = group['start'], group['end']
        if left:
            ax.axvline(left, color='white', lw=1.6)
        ax.plot([left+.35, right-.35], [1.02, 1.02], transform=ax.get_xaxis_transform(),
                color='#8B98A2', linewidth=.55, clip_on=False)
        ax.text((left+right)/2, 1.055,
                f"{group['passing_configurations']}/6\n$n$={group['n']}",
                transform=ax.get_xaxis_transform(), ha='center', va='bottom',
                fontsize=7.8, color=INK, linespacing=1.25)
    fig.text(.09, .945, 'Task-level functional success', fontsize=9, fontweight='bold', color=INK)
    fig.legend(handles=[Patch(facecolor=BLUE, label='Pass'), Patch(facecolor=FAIL_COLOR, label='Fail')],
               loc='upper right', bbox_to_anchor=(.99, .995), ncol=2, fontsize=8,
               handlelength=1.25, handletextpad=.5, columnspacing=1.25, frameon=False)
    fig.canvas.draw()
    # Verify the actual plotted matrix, row order and annotation bounds.
    assert np.array_equal(np.asarray(mesh.get_array()).reshape(6, 150), matrix)
    assert [t.get_text() for t in ax.get_yticklabels()] == [SHORT[m] for m in MODELS]
    renderer = fig.canvas.get_renderer()
    for obj in fig.findobj(Text):
        if not obj.get_visible() or not obj.get_text():
            continue
        box = obj.get_window_extent(renderer)
        if box.width and box.height:
            assert box.x0 >= -2 and box.y0 >= -2 and box.x1 <= fig.bbox.x1+2 and box.y1 <= fig.bbox.y1+2, obj.get_text()
    payload['checks'] = dict(plotted_cells_match_records=900, text_within_canvas=True,
                             row_totals_match_main_results=True, latex_compiled=False)
    return fig, payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=PAPER/'figures/output/task_success_matrix_preview')
    args = parser.parse_args()
    destination = args.output_dir.expanduser().resolve()
    if destination == (PAPER/'figures').resolve():
        parser.error('Choose a preview directory, not the manuscript figure directory.')
    protected = [PAPER/'main.tex', PAPER/'paper_sources.json', PAPER/'RESULTS_VISUAL_PLAN.md',
                 *PAPER.glob('*.zip'), *(PAPER/'figures').glob('*.pdf'),
                 *(PAPER/'writing/final_tables').glob('*.tex')]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    def draw():
        fig, payload = build_figure()
        redraw_data.export(NAME, payload, [RESULTS, input_path('task_selection'), Path(__file__).resolve()])
        (destination/'data'/f'{NAME}_caption.txt').write_text(payload['caption']+'\n')
        finish(fig, NAME)
        print(json.dumps({k: payload[k] for k in ['all_pass_tasks', 'mixed_outcome_tasks', 'all_fail_tasks']}))
    render([draw], destination)
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in before.items())
    print('Manuscript, tables, packages and published PDFs unchanged; preview only.')


if __name__ == '__main__':
    main()
