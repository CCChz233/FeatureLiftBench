"""Preview Fig.5/Table 4 and Fig.6/Table 5 at acmsmall print dimensions.

Exports figure-only vector/raster assets, editable LaTeX fragments and an HTML
layout mockup with real text tables. Never compiles TeX or edits main.tex.
"""
import argparse
import csv
import hashlib
import html
import json
from pathlib import Path

from figure_common import render
from matplotlib import pyplot as plt
from matplotlib.text import Text
from fig05_failure_stages import build_compact as build_stages
from fig06_failure_taxonomy import build_figure as build_taxonomy

from paper_inputs import ROOT, PAPER, input_path
import paper_style

# Local acmart.cls: paperwidth=6.75in; inner=outer=46 TeX points.
TEXT_WIDTH = 6.75 - 92 / 72.27
RATIOS = {'stages': (.52, .45), 'taxonomy': (.40, .57)}
CAPTIONS = {
    'stages': 'Functional outcomes and first failed evaluator gates by configuration.',
    'taxonomy': 'Primary behavioral properties in 176 confirmed source-exposed semantic violations.',
}


def exposure_rows():
    source = ROOT / 'reports/paper_analysis/source_exposure/diagnosis/summary_by_model_outcome.csv'
    with source.open() as stream:
        rows = [r for r in csv.DictReader(stream) if r['model'] == 'ALL']
    assert len(rows) == 4 and sum(int(r['all_runs']) for r in rows) == 900
    return [dict(label=r['outcome_group'].removesuffix(' failure'),
                 n=int(r['confirmed_explicit_read_runs']), total=int(r['all_runs']),
                 percent=100*int(r['confirmed_explicit_read_runs'])/int(r['all_runs']),
                 step=r['median_first_explicit_read_action_step']) for r in rows], source


def export_plot(fig, stem, out):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    for item in fig.findobj(Text):
        if not item.get_visible() or not item.get_text():
            continue
        box = item.get_window_extent(renderer)
        assert box.x0 >= bounds.x0-2 and box.y0 >= bounds.y0-2 and box.x1 <= bounds.x1+2 and box.y1 <= bounds.y1+2, (stem, item.get_text(), 'outside canvas')
    for suffix in ('svg', 'pdf', 'png'):
        fig.savefig(out / f'{stem}.{suffix}', dpi=220)
    sizes = [t.get_fontsize() for t in fig.findobj(Text) if t.get_visible() and t.get_text()]
    dimensions = list(fig.get_size_inches())
    plt.close(fig)
    return dict(width_in=dimensions[0], height_in=dimensions[1], min_font_pt=min(sizes), text_within_canvas=True)


def table4_html(rows):
    body = ''
    for r in rows:
        label = r['label'].replace('Behavioral-first', 'Behavioral-<br>first').replace('Isolation-first', 'Isolation-<br>first')
        value = f'{r["n"]}/{r["total"]}<br>({r["percent"]:.1f})'
        if r['label'] == 'Behavioral-first': value = f'<b>{value}</b>'
        body += f'<tr><td>{label}</td><td>{value}</td><td>{r["step"]}</td></tr>'
    return '<div class="tcaption">Table 4. Source exposure by final outcome.</div><table class="exposure"><colgroup><col style="width:34%"><col style="width:39%"><col style="width:27%"></colgroup><thead><tr><th>Outcome</th><th>Confirmed<br>read<br>n/N (%)</th><th>Median<br>first read<br>step</th></tr></thead><tbody>'+body+'</tbody></table><p class="note">Read-step medians are conditional on confirmed source reads.</p>'


def table5_html(data):
    rows=''.join(f"<tr><td>{r['label']}</td><td>{html.escape(r['definition'])}</td><td>{r['n']} ({r['percent']:.1f})</td><td>{r['distinct_tasks']}</td></tr>" for r in data['properties'])
    return '<div class="tcaption">Table 5. Behavioral-property definitions and counts.</div><table class="taxonomy"><thead><tr><th>Property</th><th>Operational definition</th><th>n (%)</th><th>Tasks</th></tr></thead><tbody>'+rows+'</tbody></table><p class="note">N = 176 runs across 68 tasks; task counts overlap across properties.</p>'


def latex_table4(rows):
    body = []
    for r in rows:
        label = r['label'].replace('Behavioral-first', r'\shortstack[l]{Behavioral-\\first}').replace('Isolation-first', r'\shortstack[l]{Isolation-\\first}')
        value = rf'\shortstack{{{r["n"]}/{r["total"]}\\({r["percent"]:.1f})}}'
        if r['label'] == 'Behavioral-first': value = r'\textbf{'+value+'}'
        body.append(f'{label} & {value} & {r["step"]} '+r'\\')
    return '\n'.join([
        r'\captionof{table}{Source exposure by final outcome.}', r'\label{tab:source-exposure}',
        r'\footnotesize', r'\begin{tabularx}{\linewidth}{@{}Xrr@{}}', r'\toprule',
        r'Outcome & \shortstack{Confirmed\\read\\$n/N$ (\%)} & \shortstack{Median\\first read\\step} \\',
        r'\midrule', *body, r'\bottomrule', r'\end{tabularx}',
        r'\par\smallskip {\scriptsize Read-step medians are conditional on confirmed source reads.}'])


def latex_table5(data):
    # Keep the preview identical to the editable table in the current manuscript.
    import re
    text=(PAPER/'main.tex').read_text()
    return re.search(r'% BEGIN RESULTS EVIDENCE: failure-analysis\n(.*?)% END RESULTS EVIDENCE: failure-analysis',text,re.S)[1]


def latex_pair(kind, table):
    left, right = RATIOS[kind]
    number, label = ('5','failures') if kind == 'stages' else ('6','failure-analysis')
    return '\n'.join([
        '% Candidate replacement for the existing figure AND table, not an additional float.',
        '% acmart already loads caption. Keep native caption formatting and float spacing.',
        '% Asset path assumes this fragment remains in figures/output/evidence_pairs_preview/.',
        r'\begin{figure}[tbp]', r'  \centering',
        rf'  \begin{{minipage}}[t]{{{left:.2f}\linewidth}}',
        r'    \vspace{0pt}',
        rf'    \includegraphics[width=\linewidth]{{figures/output/evidence_pairs_preview/fig{number}_compact.pdf}}',
        rf'    \caption{{{CAPTIONS[kind]}}}', rf'    \label{{fig:{label}}}',
        rf'    \Description{{{CAPTIONS[kind]}}}', r'  \end{minipage}\hfill',
        rf'  \begin{{minipage}}[t]{{{right:.2f}\linewidth}}', r'    \vspace{0pt}',
        table, r'  \end{minipage}', r'\end{figure}', ''])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1]/'output/evidence_pairs_preview')
    args = parser.parse_args()
    out = args.output_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    protected = [PAPER/'main.tex', *paper_style.FIGURES_DIR.glob('*.pdf'), *paper_style.FIGURES_DIR.glob('*.png')]
    original = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    rows, source = exposure_rows()
    result = {}
    def draw():
        fig, stages = build_stages(TEXT_WIDTH * RATIOS['stages'][0])
        result['fig5'] = export_plot(fig, 'fig5_compact', out)
        fig, taxonomy = build_taxonomy()
        result['fig6'] = export_plot(fig, 'fig6_compact', out)
        # Full-width alternative, reusing the existing formal renderer in isolation.
        from fig06_failure_taxonomy import draw_failure_analysis
        draw_failure_analysis()
        result['data'] = dict(stages=stages['first_outcomes'], taxonomy=taxonomy, exposure=rows)
        (out/'pair_fig5_table4.tex').write_text(latex_pair('stages', latex_table4(rows)))
        (out/'pair_fig6_table5.tex').write_text(latex_table5(taxonomy))
        return taxonomy
    render([draw], out)
    taxonomy = result['data']['taxonomy']
    first = f'<div class="pair stages"><figure><img src="fig5_compact.svg"><figcaption>Fig. 5. {CAPTIONS["stages"]}</figcaption></figure><section>{table4_html(rows)}</section></div>'
    second = f'<div class="pair causes"><figure><img src="fig6_compact.svg"><figcaption>Fig. 6. {CAPTIONS["taxonomy"]}</figcaption></figure><section>{table5_html(taxonomy)}</section></div>'
    third = f'<figure><img src="fig6_behavioral_obligations.png"><figcaption>Fig. 6. {CAPTIONS["taxonomy"]}</figcaption></figure><section class="stack-table">{table5_html(taxonomy)}</section>'
    page = '''<!doctype html><html lang="zh"><meta charset="utf-8"><title>Results 图表并排预览</title><style>
body{background:#eceef0;margin:24px;color:#161616;font:15px/1.6 system-ui} header, .label{max-width:850px;margin:16px auto} h1{font-size:23px} .label{font-weight:600} .paper{width:WIDTHin;padding:.28in;margin:0 auto 30px;background:white;box-shadow:0 2px 12px #0001;font-family:"Times New Roman",serif;box-sizing:content-box;font-size:8pt;line-height:1.18} .pair{display:grid;align-items:start;column-gap:3%}.stages{grid-template-columns:52% 45%}.causes{display:block}.causes section{margin-top:14pt}figure{margin:0;min-width:0}section{min-width:0}img{display:block;width:100%;height:auto}figcaption,.tcaption{font:9pt/1.22 Arial,sans-serif}figcaption{margin-top:6pt}.tcaption{margin-bottom:6pt}table{border-collapse:collapse;width:100%;table-layout:fixed;font-size:8pt;line-height:1.22;border-top:.8pt solid;border-bottom:.8pt solid}th,td{padding:3pt 6pt;vertical-align:top;text-align:left;overflow-wrap:normal}th:first-child,td:first-child{padding-left:0}th:last-child,td:last-child{padding-right:0}thead{border-bottom:.5pt solid}th{font-weight:normal}.exposure td:nth-child(n+2),.exposure th:nth-child(n+2),.taxonomy td:last-child,.taxonomy th:last-child{text-align:right}.taxonomy td:last-child{white-space:nowrap}.note{font-size:7pt;line-height:1.2;margin:5pt 0 0}.stack-table{margin-top:14pt}.stack-table .taxonomy col:first-child{width:24%!important}.stack-table .taxonomy col:nth-child(2){width:60%!important}.stack-table .taxonomy col:last-child{width:16%!important}@media print{body{background:white;margin:0}header,.label{display:none}.paper{box-shadow:none;break-after:page}}
</style><header><h1>Results 图表组合预览</h1><p>按当前 acmsmall 正文宽约 13.9 cm 设计。图为重新绘制的矢量图；表为可选中文字，并非截图。这里展示宽度与内容换行关系，不是 LaTeX 编译结果；实际浮动位置、页数与表格高度需在最终排版时确认。</p></header>'''.replace('WIDTH',f'{TEXT_WIDTH:.6f}')
    page += '<div class="label">A · Fig.5 + Table 4 · 52% / 45%</div><article class="paper" id="pair1">'+first+'</article>'
    page += '<div class="label">B · Fig.6 + Table 5 · 属性构成与定义</div><article class="paper" id="pair2">'+second+'</article>'
    page += '<div class="label">C · Fig.6 + Table 5 · 上下排列对照</div><article class="paper" id="stacked">'+third+'</article></html>'
    (out/'index.html').write_text(page)
    result.update(text_width_in=TEXT_WIDTH, ratios=RATIOS, preview_not_latex_render=True,
                  source_exposure=str(source.relative_to(ROOT)), removed_table4_runs_column='Total remains in n/N denominator')
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in original.items())
    result['formal_manuscript_and_assets_unchanged'] = True
    (out/'preview_data.json').write_text(json.dumps(result,indent=2)+'\n')
    print(out/'index.html')


if __name__ == '__main__':
    main()
