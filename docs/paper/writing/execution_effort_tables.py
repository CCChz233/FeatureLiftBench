"""Generate/check the outcome-effort table without compiling the manuscript."""
import argparse
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from execution_effort import load_analysis
from paper_inputs import PAPER, MODELS, SHORT

BEGIN = '% BEGIN RESULTS EVIDENCE: execution-effort'
END = '% END RESULTS EVIDENCE: execution-effort'


def build_table():
    data = load_analysis()
    lookup = {(r['configuration'], r['outcome']): r for r in data['effort']}
    lines = [r'\begin{table}[tbp]', r'  \centering', r'  \footnotesize',
             r'  \caption{Token expenditure by final outcome.}', r'  \label{tab:execution-effort}',
             r'  \begin{tabularx}{\linewidth}{@{}Xrlrl@{}}', r'    \toprule',
             r'    & \multicolumn{2}{c}{Successful runs} & \multicolumn{2}{c}{Failed runs} \\',
             r'    \cmidrule(lr){2-3}\cmidrule(lr){4-5}',
             r'    Configuration & $n/N$ & Median [IQR] & $n/N$ & Median [IQR] \\', r'    \midrule']
    for model in MODELS:
        cells = [SHORT[model]]
        for outcome in ('pass', 'fail'):
            row = lookup[model, outcome]
            d = row['tokens']
            cells.extend([f"{row['usable_n']}/{row['assigned_n']}",
                          '--' if not d['n'] else f"{d['median']/1e6:.2f} [{d['q1']/1e6:.2f}, {d['q3']/1e6:.2f}]"])
        lines.append('    '+' & '.join(cells)+r' \\')
    lines.extend([r'    \bottomrule', r'  \end{tabularx}',
                  r'  \par\smallskip\begin{minipage}{\linewidth}\scriptsize',
                  r'  Tokens are input plus output, including cached input, in millions. $n/N$ denotes usable records over assigned runs with that outcome.',
                  r'  \end{minipage}', r'\end{table}'])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    table = build_table()
    tex = (PAPER/'main.tex').read_text()
    pattern = re.compile(re.escape(BEGIN)+r'\n(.*?)\n'+re.escape(END), re.S)
    match = pattern.search(tex)
    assert match, 'Insert the RQ2 table region first'
    snippet = PAPER/'writing/final_tables/table3_execution_effort.tex'
    if args.check:
        assert match[1] == table, 'Stale execution-effort manuscript table'
        assert snippet.read_text() == table+'\n'
    else:
        (PAPER/'main.tex').write_text(pattern.sub(lambda _: BEGIN+'\n'+table+'\n'+END, tex))
        snippet.write_text(table+'\n')
    print('Execution-effort table agrees with reviewed records; no LaTeX compilation.')


if __name__ == '__main__':
    main()
