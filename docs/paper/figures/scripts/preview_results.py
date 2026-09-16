"""Preview only the two NEW Results figures in the locked visual plan.

Run from any directory:
    python preview_results.py --output-dir /tmp/flb-results-preview
    python preview_results.py --only footprint --output-dir /tmp/flb-fig7

Default output: figures/output/results_preview/ (never the manuscript assets).
This entry never invokes TeX, updates tables, or redraws inherited figures.
Each figure's editable layout lives in its own fig*.py file. build_figure()
returns a Matplotlib figure without file writes, for notebook experimentation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from figure_common import render, finish
from matplotlib.collections import PathCollection, LineCollection
from matplotlib.text import Text
import redraw_data
from fig4_structure import build_figure as build_structure
from fig7_footprint_forest_preview import build_figure as build_matched

SCRIPTS = Path(__file__).resolve().parent
FIGURES = SCRIPTS.parent
BUILDERS = {
    'structure': ('fig4_structure', build_structure),
    'footprint': ('fig7_matched_footprint', build_matched),
}


def validate_geometry(name, fig, payload):
    """Check plotted data and transformed geometry, not just declared metadata."""
    fig.canvas.draw()
    checks = {}
    assert len(fig.axes) == 2
    if name == 'footprint':
        assert payload['geometry'] == 'task_adjusted_forest'
        assert payload['sample']['tasks'] == 115 and payload['sample']['artifacts'] == 485
        rows = payload['analyses']['task_bootstrap']['rows']
        for ax, metric, limits, scale, center in zip(
                fig.axes, ['rres_ratio', 'copy_pp'], [payload['rres_limits'], payload['copy_limits']],
                ['log', 'linear'], [1, 0]):
            assert ax.get_xscale() == scale and np.allclose(ax.get_xlim(), limits)
            points = [c for c in ax.collections if isinstance(c, PathCollection)]
            intervals = [c for c in ax.collections if isinstance(c, LineCollection)]
            assert len(points) == len(intervals) == 1 and not ax.patches
            assert np.allclose(points[0].get_offsets(), [[r[metric], i] for i, r in enumerate(rows)])
            expected = [[[r[metric + '_ci'][0], i], [r[metric + '_ci'][1], i]] for i, r in enumerate(rows)]
            assert np.allclose(intervals[0].get_segments(), expected)
            assert len(ax.lines) == 1 and np.allclose(ax.lines[0].get_xdata(), center)
            assert all(limits[0] < r[metric + '_ci'][0] <= r[metric + '_ci'][1] < limits[1] for r in rows)
            checks[metric] = dict(points=6, intervals_match_bootstrap=True, scale=scale, reference=center, no_clipping=True)
        assert [t.get_text() for t in fig.axes[0].get_yticklabels()] == [r['short'] for r in rows]
    else:
        assert payload['design']['geometry'] == 'two_panel_grouped_bar'
        assert [g['n'] for g in payload['groups']] == [56,76,18,139,127,71,49]
        for ax, panel in zip(fig.axes, payload['design']['panels']):
            assert np.allclose(ax.get_ylim(), [0,100])
            assert len(ax.containers) == len(panel['groups'])
            assert len(ax.patches) == 6 * len(panel['groups'])
            assert panel['bar_width'] < min(np.diff(panel['offsets']))
            for bars, group, shift in zip(ax.containers, panel['groups'], panel['offsets']):
                assert all(b.get_y() == 0 for b in bars)
                assert np.allclose([b.get_height() for b in bars], group['rates'])
                assert np.allclose([b.get_x()+b.get_width()/2 for b in bars], np.arange(6)+shift)
            assert [t.get_text() for t in ax.get_xticklabels()] == [m['short'] for m in payload['models']]
        checks = dict(bars=42, panels=2, denominators=[g['n'] for g in payload['groups']],
                      zero_baseline=True, bar_values_match_evidence=True, model_order_matches_main_table=True)
    # Titles, tick labels, axis labels and figure notes must remain on the canvas.
    renderer=fig.canvas.get_renderer();frame=fig.bbox
    for obj in fig.findobj(Text):
        if not obj.get_visible() or not obj.get_text():continue
        b=obj.get_window_extent(renderer)
        if b.width and b.height:
            assert b.x0>=frame.x0-2 and b.y0>=frame.y0-2 and b.x1<=frame.x1+2 and b.y1<=frame.y1+2, (name,obj.get_text(),'outside canvas')
    checks['text_within_canvas']=True
    return checks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',nargs='+',choices=list(BUILDERS),default=list(BUILDERS))
    parser.add_argument('--output-dir',type=Path,default=FIGURES/'output/results_preview')
    args=parser.parse_args()
    destination=args.output_dir.expanduser().resolve()
    # Reject routes that would overwrite a manuscript PDF even via a symlink.
    if destination==FIGURES.resolve():parser.error('Choose a preview directory, not figures/ itself.')
    for key in args.only:
        name,_=BUILDERS[key]
        for suffix in ('pdf','png'):
            if (destination/f'{name}.{suffix}').is_symlink():parser.error('Preview files must not be symlinks.')
    protected=[FIGURES.parent/'main.tex',FIGURES.parent/'RESULTS_VISUAL_PLAN.md',
               FIGURES.parent/'paper_sources.json',*FIGURES.glob('*.pdf'),*FIGURES.glob('*.png')]
    before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.is_file()}
    checks={}
    def draw(key):
        name,builder=BUILDERS[key]
        fig,payload,sources=builder()
        checks[key]=validate_geometry(key,fig,payload)
        redraw_data.export(name,payload,sources)
        if key == 'footprint':
            from fig7_adjusted_analysis import analyze, write_outputs
            data, draws = analyze()
            write_outputs(destination / 'data', data, draws)
            (destination / 'data/fig7_caption.md').write_text(payload['caption_note'] + '\n')
        finish(fig,name)
    render([lambda k=k:draw(k) for k in args.only],destination)
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in before.items()), 'A protected paper file changed'
    checks['paper_files_unchanged']=True
    checks['latex_compiled']=False
    (destination/'preview_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(f'Checked new figures only; paper files unchanged. {destination / "preview_checks.json"}')


if __name__=='__main__':main()
