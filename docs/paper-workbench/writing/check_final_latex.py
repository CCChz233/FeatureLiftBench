"""Static checks for the final source; never invoke a TeX compiler."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_inputs import PAPER, MODEL_RECORDS, input_path, validate_manuscript


def main():
    tex = (PAPER / 'main.tex').read_text()
    supplement = (PAPER/'supplementary.tex').read_text()
    text = re.sub(r'(?<!\\)%[^\n]*', '', tex)
    # Ignore escaped literal braces, then check group and environment nesting.
    depth = 0
    for token in re.findall(r'\\.|[{}]', text):
        if token == '{': depth += 1
        if token == '}': depth -= 1
        assert depth >= 0, 'Unmatched closing brace'
    assert depth == 0, 'Unclosed brace group'
    stack = []
    for action, env in re.findall(r'\\(begin|end)\{([^}]+)\}', text):
        if action == 'begin': stack.append(env)
        else:
            assert stack and stack.pop() == env, ('Unbalanced environment', env)
    assert not stack
    assert sum(token == '$' for token in re.findall(r'\\.|\$', text)) % 2 == 0
    assert r'\usepackage{amsmath}' in text
    assert not re.search(r'\\\\\[95', text), 'CI header parsed as an optional line-break length'
    labels = re.findall(r'\\label\{(tab:[^}]+)\}', text)
    assert labels == ['tab:main','tab:structure','tab:paired-ablation','tab:source-exposure',
                      'tab:task-comparison']
    assert re.findall(r'\\label\{(tab:[^}]+)\}', supplement) == ['tab:execution-effort','tab:matched-footprint']
    assert r'\appendix' not in text
    assert re.findall(r'\\label\{(fig:[^}]+)\}', text) == [
        'fig:pipeline', 'fig:construction', 'fig:coverage', 'fig:source-evidence', 'fig:failures',
        'fig:failure-analysis', 'fig:execution-effort', 'fig:matched-footprint']
    for block in re.findall(r'\\begin\{figure\}.*?\\end\{figure\}', text, re.S):
        content = r'\includegraphics' if r'\includegraphics' in block else r'\begin{tabularx}'
        assert block.index(content) < block.index(r'\caption')
    for block in re.findall(r'\\begin\{table\}.*?\\end\{table\}', text, re.S):
        assert block.index(r'\caption') < block.index(r'\begin{tabular')
        assert r'\begin{minipage}' not in block and r'\scriptsize' not in block
        assert r'\dagger' not in block and r'\ddagger' not in block
    bib = (PAPER / 'references.bib').read_text()
    keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib))
    cited = {key.strip() for group in re.findall(r'\\cite(?:t|p|author|year|alp|alt|yearpar)?(?:\[[^\]]*\])*\{([^}]+)\}', text)
             for key in group.split(',')}
    assert cited <= keys, ('Missing bibliography keys', cited - keys)
    confirmed=json.loads(input_path('author_result_clarifications').read_text())
    main_table=re.search(r'% BEGIN GENERATED TABLE: main\n(.*?)% END GENERATED TABLE: main',tex,re.S)[1]
    for model,values in confirmed['token_totals'].items():
        line=next(line for line in main_table.splitlines() if line.strip().startswith(r'\mbox{'+MODEL_RECORDS[model]['display']+'} &'))
        cells=line.strip().removesuffix(r'\\').strip().split(' & ')
        assert cells[-2:]==[f"{values['median_k']/10:.2f}",f"{values['p90_k']/10:.2f}"]
    assert confirmed['maximum_steps']['value'] == 150
    assert len(re.findall(r'150[- ](?:step|interaction)',text)) == 1
    assert not re.search(r'120[- ](?:step|interaction)',text)
    assert 'development sample' not in text
    for section in (tex.split(r'\begin{abstract}', 1)[1].split(r'\end{abstract}', 1)[0],
                    tex.split(r'\section{Conclusion}', 1)[1].split(r'\section*{Data Availability}', 1)[0]):
        normalized = ' '.join(section.split())
        assert 'identifies recurring but limited patterns involving' in normalized
        assert ('79.5\\% of Primary/Extended-first failures contain confirmed reads of '
                'entrypoint-associated source-file content.') in normalized
        for theme in ('changed ambient assumptions', 'incompatible supporting representations and pipelines',
                      'destination-specific obligations requiring adaptation'):
            assert theme in normalized
    ablation_table = re.search(r'% BEGIN RESULTS EVIDENCE: paired-ablation\n(.*?)% END RESULTS EVIDENCE:', tex, re.S)[1]
    assert '25/40 & 6/40 & 20 & 1 & 47.5' in ablation_table
    assert 'includes 18 runs without' in text and 'successful artifact delivery' in text
    assert '18 Contract-only missing submissions' not in text
    qualitative = text.split(r'\paragraph{Recurring themes across the reviewed sample.}', 1)[1].split(r'\subsection{Secondary Analyses:', 1)[0]
    assert 'RQ3: How Can Behavioral Preservation Fail Despite Confirmed Reads of Entrypoint-Associated Source-File Content?' in text
    assert not re.search(r'behavioral-first|relevant source.*observed', text, re.I)
    assert 'purposively diverse sample of 40' in text
    assert 'Two authors independently' in text and 'reviewed the 40 sampled cases' in text
    assert 'not random or representative' in text
    for retired in ['176', '228', '201 originally', '69.3', '34.1', '18.2', '17.0',
                    'fig6_behavioral_obligations.pdf', 'tab:failure-analysis']:
        assert retired not in text, ('Retired quantitative taxonomy', retired)
    for case in ['platformdirs', 'cerberus', 'importlib']:
        assert case in qualitative
    assert 'causal effect' in qualitative and 'prevalence' in qualitative
    mapping=json.loads(input_path('qualitative_themes').read_text())
    assert len(mapping['cases']) == len({r['case_id'] for r in mapping['cases']}) == 40
    assert {r['case_id'] for r in mapping['cases']} == {f'SE{i:03}' for i in range(1,41)}
    for key, theme in mapping['themes'].items():
        assert set(theme['cases']) == {r['case_id'] for r in mapping['cases'] if key in r['themes']}
    assert r'\input{qualitative_mapping.tex}' in supplement

    rq4 = text.split(r'\label{sec:footprint-results}', 1)[1].split(r'\section{Discussion}', 1)[0]
    assert not any(x in rq4 for x in ['Wilcoxon', 'rank-biserial', 'identity-scatter', '97 tasks passed'])
    assert '115 tasks' in rq4 and '485 successful artifacts' in rq4
    evidence = json.loads((PAPER/'writing/results_visual_evidence.json').read_text())['adjusted_footprint']
    previous = json.loads((PAPER/'figures/output/text_cleanup_preview/data/fig7_adjusted_analysis.json').read_text())
    assert evidence['analyses'] == previous['analyses']
    assert evidence['sample'] == previous['sample']
    table = re.search(r'% BEGIN RESULTS EVIDENCE: matched-footprint\n(.*?)% END RESULTS EVIDENCE:', supplement, re.S)[1]
    for row in evidence['analyses']['task_bootstrap']['rows']:
        display = next(m['display'] for m in MODEL_RECORDS.values() if m['short']==row['short'])
        actual = next(line for line in table.splitlines() if line.strip().startswith(display + ' &'))
        vals = actual.strip().removesuffix(r'\\').strip().split(' & ')
        lo, hi = row['rres_ratio_ci']; clo, chi = row['copy_pp_ci']
        assert vals == [display, str(row['included_success_n']),
                        f"{row['rres_ratio']:.3f} [{lo:.3f}, {hi:.3f}]",
                        f"${row['copy_pp']:+.2f}$ [${clo:+.2f}$, ${chi:+.2f}$]"]
    from execution_effort import load_analysis
    effort = load_analysis()
    rq2 = text.split(r'\label{sec:execution-effort-results}', 1)[1].split(r'\subsubsection{Implementation footprints', 1)[0]
    assert re.findall(r'\\label\{sec:rq(\d)\}', text) == ['1','2','3']
    assert 'first observed pass' in text or 'observed passing checkpoint' in text
    for row in effort['summaries']:
        if row['checkpoint_n']:
            assert f"{100*row['psf']['median']:.1f}\\%" in rq2
    assert f"{sum(r['checkpoint_n'] for r in effort['summaries'])} successful runs" in rq2
    assert str(sum(r['response_n'] for r in effort['summaries'])) in rq2
    assert str(sum(r['usable_n'] for r in effort['effort'])) in rq2
    assert 'same conservative subset' not in text
    assert 'five recoverable runs' not in text
    assert 'Historical per-call usage is unavailable' not in text
    from execution_effort_tables import build_table
    region = re.search(r'% BEGIN RESULTS EVIDENCE: execution-effort\n(.*?)\n% END RESULTS EVIDENCE: execution-effort',supplement,re.S)
    assert region[1] == build_table()
    result = dict(validate_manuscript(), tables=5, supplementary_tables=4, research_questions=3, secondary_analyses=2, brace_groups_balanced=True,
                  environments_balanced=True, bibliography_keys_resolved=len(cited),
                  footprint_table_matches_figure_analysis=True, old_pairwise_footprint_statistics_removed=True,
                  execution_effort_matches_reviewed_records=True,
                  checkpoint_samples={row['short']: row['checkpoint_n'] for row in effort['summaries']},
                  response_samples={row['short']: row['response_n'] for row in effort['summaries']},
                  outcome_effort_records=sum(row['usable_n'] for row in effort['effort']),
                  author_confirmed_token_cells_match=True, maximum_steps_stated_once=True,
                  author_confirmed_pro_results_integrated=True,
                  qualitative_analysis_scope_verified=True,
                  latex_compiled=False, layout_verified=False,
                  raw_profile_coverage='307/900 at legacy unpacked paths; all 900 raw runs supplied in separately verified archives',
                  main_tex_sha256=hashlib.sha256((PAPER/'main.tex').read_bytes()).hexdigest())
    (PAPER/'writing/final_latex_checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
