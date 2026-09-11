"""Summarize existing 150-task outcomes by task structure; never run experiments."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_inputs import PAPER, ROOT, RESULTS as MATRIX, MODELS, input_path

TAXONOMY = input_path('coverage_data')


def build():
    with MATRIX.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    taxonomy = json.loads(TAXONOMY.read_text(encoding='utf-8'))
    tasks = {t['task_id']: t for t in taxonomy['tasks']}
    assert len(tasks) == 150 and len(rows) == 900
    cells = {(r['model'], r['task_id']): r for r in rows}
    assert len(cells) == 900 and set(cells) == {(m, t) for m in MODELS for t in tasks}
    assert all(r['functional_pass'] in ('True', 'False') for r in rows)
    assert all(r['lift_type'] == tasks[r['task_id']]['lift_type'] for r in rows)
    groups = []
    for kind, names in [('Lift type', taxonomy['lift_types']), ('Mechanism', taxonomy['mechanism_order'])]:
        for name in names:
            ids = sorted(t for t, a in tasks.items() if
                         (a['lift_type'] == name if kind == 'Lift type' else name in a['mechanisms']))
            counts = [sum(cells[m, t]['functional_pass'] == 'True' for t in ids) for m in MODELS]
            groups.append(dict(kind=kind, name=name, n=len(ids), task_ids=ids,
                               passes=counts, rates=[100*n/len(ids) for n in counts]))
    assert sum(g['n'] for g in groups[:3]) == 150
    assert [sum(g['passes'][i] for g in groups[:3]) for i in range(6)] == [115,108,102,68,63,36]
    lines = [r'\begin{table}[tbp]', r' \caption{Functional pass rates (\%) by task structure on the common 150-task comparison.}',
             r' \label{tab:structure}', r' \centering\small', r' \setlength{\tabcolsep}{3pt}',
             r' \begin{tabular}{@{}lrrrrrrr@{}}', r' \toprule',
             r' Category & $n$ & Pro & Flash & Luna & GLM & Qwen & OSS \\', r' \midrule']
    for i,g in enumerate(groups):
        if i == 3: lines.append(r' \midrule')
        lines.append(' ' + ' & '.join([g['name'], str(g['n']), *[f'{v:.1f}' for v in g['rates']]]) + r' \\')
    lines += [r' \bottomrule', r' \end{tabular}', r' \par\smallskip\begin{minipage}{\linewidth}\footnotesize',
              r' $n$ is the task denominator for every configuration in that row. Lift types partition the tasks; mechanism categories overlap. Model abbreviations follow Section~\ref{sec:protocol}. These unadjusted comparisons describe composition; Section~\ref{sec:rq3} reports the construction-adjusted analysis.',
              r' \end{minipage}', r'\end{table}']
    evidence = dict(scope='Six configurations on the common 150 tasks', models=MODELS, groups=groups,
                    method='Within-category passing tasks / assigned tasks; overlapping mechanisms, no causal or significance claim',
                    inputs=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (MATRIX,TAXONOMY)],
                    new_experiments=False)
    return '\n'.join(lines), evidence


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args=parser.parse_args()
    table,evidence=build()
    file=PAPER/'main.tex'; raw=file.read_bytes(); text=raw.decode('utf-8').replace('\r\n','\n')
    pattern=r'(% BEGIN STRUCTURE RESULTS\n).*?(% END STRUCTURE RESULTS)'
    updated,n=re.subn(pattern,lambda m:m[1]+table+'\n'+m[2],text,flags=re.S); assert n==1
    if args.check:
        assert updated==text, 'Structure table differs from saved results'
    else:
        file.write_bytes(updated.replace('\n','\r\n').encode('utf-8'))
        (PAPER/'writing/structure_results.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print('Checked 900 model-task cells, 150 task labels and seven category denominators; no new experiments.')
