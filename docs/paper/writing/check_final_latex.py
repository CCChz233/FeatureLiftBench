"""Static checks for the final source; never invoke a TeX compiler."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_inputs import PAPER, validate_manuscript


def main():
    tex = (PAPER / 'main.tex').read_text()
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
    assert len(re.findall(r'(?<!\\)\$', text)) % 2 == 0
    assert r'\usepackage{amsmath}' in text
    assert not re.search(r'\\\\\[95', text), 'CI header parsed as an optional line-break length'
    labels = re.findall(r'\\label\{(tab:[^}]+)\}', text)
    assert labels == ['tab:main','tab:structure','tab:source-exposure','tab:paired-ablation',
                      'tab:matched-footprint','tab:task-comparison']
    bib = (PAPER / 'references.bib').read_text()
    keys = set(re.findall(r'@\w+\s*\{\s*([^,\s]+)', bib))
    cited = {key.strip() for group in re.findall(r'\\cite(?:t|p|author|year|alp|alt|yearpar)?(?:\[[^\]]*\])*\{([^}]+)\}', text)
             for key in group.split(',')}
    assert cited <= keys, ('Missing bibliography keys', cited - keys)
    rq4 = text.split(r'\label{sec:rq4}', 1)[1].split(r'\section{Discussion}', 1)[0]
    assert not any(x in rq4 for x in ['Wilcoxon', 'rank-biserial', 'identity-scatter', '97 tasks passed'])
    assert '115 tasks' in rq4 and '485 successful artifacts' in rq4
    evidence = json.loads((PAPER/'writing/results_visual_evidence.json').read_text())['adjusted_footprint']
    previous = json.loads((PAPER/'figures/output/text_cleanup_preview/data/fig7_adjusted_analysis.json').read_text())
    assert evidence['analyses'] == previous['analyses']
    assert evidence['sample'] == previous['sample']
    table = re.search(r'% BEGIN RESULTS EVIDENCE: matched-footprint\n(.*?)% END RESULTS EVIDENCE:', tex, re.S)[1]
    for row in evidence['analyses']['task_bootstrap']['rows']:
        actual = next(line for line in table.splitlines() if line.strip().startswith(row['short'] + ' &'))
        vals = actual.strip().removesuffix(r'\\').strip().split(' & ')
        lo, hi = row['rres_ratio_ci']; clo, chi = row['copy_pp_ci']
        assert vals == [row['short'], str(row['included_success_n']),
                        f"{row['rres_ratio']:.3f} [{lo:.3f}, {hi:.3f}]",
                        f"${row['copy_pp']:+.2f}$ [${clo:+.2f}$, ${chi:+.2f}$]"]
    result = dict(validate_manuscript(), tables=6, brace_groups_balanced=True,
                  environments_balanced=True, bibliography_keys_resolved=len(cited),
                  table5_matches_figure_analysis=True, old_rq4_statistics_removed=True,
                  latex_compiled=False, layout_verified=False,
                  raw_profile_coverage='307/900; 593 unavailable (existing limitation)',
                  main_tex_sha256=hashlib.sha256((PAPER/'main.tex').read_bytes()).hexdigest())
    (PAPER/'writing/final_latex_checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
