"""Render the additional Results evidence tables; never run experiments or LaTeX."""
import csv
import json
import re
import math
from pathlib import Path
import sys
from scipy.stats import binomtest
from results_visuals import evidence
from paper_inputs import input_path
from failure_analysis import counts as failure_counts, CATEGORIES


def compact(label,caption,columns,headers,rows,note,colsep='3pt'):
    lines=[r'\begin{table}[tbp]',r'  \centering',r'  \footnotesize',
           rf'  \caption{{{caption}}}',rf'  \label{{tab:{label}}}',
           rf'  \begin{{tabularx}}{{\linewidth}}{{@{{}}{columns}@{{}}}}',r'    \toprule',
           '    '+' & '.join(headers)+r' \\',r'    \midrule']
    for r in rows:
        lines.append(r'    \midrule' if r is None else '    '+' & '.join(r)+r' \\')
    lines += [r'    \bottomrule',r'  \end{tabularx}',r'  \par\smallskip\begin{minipage}{\linewidth}\scriptsize',
              '  '+note,r'  \end{minipage}',r'\end{table}']
    return '\n'.join(lines)


def sci(value):
    exponent=math.floor(math.log10(value))
    return rf'${value/10**exponent:.2f}\times10^{{{exponent}}}$'


def build():
    data=evidence();outputs={}
    failures=failure_counts()
    data['failure_analysis']=failures
    cause_rows=[]
    for key,label,definition in CATEGORIES:
        n=failures['pooled'][key]
        value=f'{n} ({100*n/failures["valid"]:.1f})'
        if key=='behavior_drift':
            label=r'\textbf{'+label+'}'
            value=r'\textbf{'+value+'}'
        cause_rows.append([label,definition,value])
    outputs['failure-analysis']=compact('failure-analysis',
        'Failure taxonomy and pooled counts after confirmed source reading.',
        r'p{0.23\linewidth}Xr',['Category','Observed gap',r'$n$ (\%)'],cause_rows,
        r'$N=228$ reviewed failures; one primary category per failure.',
        colsep='4pt')
    rows=[]
    for i,g in enumerate(data['structure']):
        if i==3:rows.append(None)
        rows.append([g['name'],str(g['n']),*[f'{v:.1f}' for v in g['rates']]])
    outputs['structure']=compact('structure',r'Observed functional pass rates (\%) by task structure.',
        'Xrrrrrrr',['Category','$n$',*[m['short'] for m in data['models']]],rows,
        r'$n$ is the row denominator. Lift types partition the tasks; mechanism groups overlap.')
    stats=json.loads(input_path('source_ablation_statistics').read_text())
    folder=input_path('source_ablation_results').parent
    def read(name):
        with (folder/name).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
    pairs=read('paired_outcomes.csv');outcomes=read('task_outcomes.csv')
    cells={(r['model'],r['task_id'],r['arm']):r for r in outcomes}
    assert len(cells)==len(outcomes)==240
    assert len(pairs)==len({(r['model'],r['task_id']) for r in pairs})==120
    rows=[];ps={}
    for s in stats['results']:
        rs=[r for r in pairs if r['model']==s['model']]
        assert len(rs)==len({r['task_id'] for r in rs})==s['n']==40
        for r in rs:
            for field,arm in [('full_pass','full_repository'),('contract_pass','contract_only')]:
                assert int(r[field])==int(cells[r['model'],r['task_id'],arm]['functional_pass'])
        full=sum(int(r['full_pass']) for r in rs);contract=sum(int(r['contract_pass']) for r in rs)
        fo=sum(int(r['full_pass'])==1 and int(r['contract_pass'])==0 for r in rs)
        co=sum(int(r['contract_pass'])==1 and int(r['full_pass'])==0 for r in rs)
        assert [full,contract,fo,co]==[s[k] for k in ['full_pass','contract_pass','full_only','contract_only']]
        ps[s['model']]=float(binomtest(fo,fo+co,.5).pvalue)
        assert math.isclose(ps[s['model']],s['mcnemar_exact_p'],rel_tol=1e-10)
    adjusted={};running=0
    for i,m in enumerate(sorted(ps,key=ps.get)):
        running=max(running,min(1,(len(ps)-i)*ps[m]));adjusted[m]=running
    names={r['id']:r['display'] for r in data['models']}
    for s in stats['results']:
        m=s['model'];assert math.isclose(adjusted[m],s['holm_adjusted_p_three_models'],rel_tol=1e-10)
        label=names[m]
        lo,hi=s['paired_bootstrap_95ci_pp']
        rows.append([label,f"{s['full_pass']}/40",f"{s['contract_pass']}/40",str(s['full_only']),str(s['contract_only']),
                     f"{s['delta_pp']:.1f}",f'[{lo:.1f}, {hi:.1f}]',sci(adjusted[m])])
    pro_missing=[r for r in outcomes if r['model']=='deepseek-v4-pro' and r['arm']=='contract_only' and r['first_outcome']=='Missing']
    assert len(pro_missing)==12 and all(r['last_conversation_error']=='LLMTimeoutError' for r in pro_missing)
    outputs['paired-ablation']=compact('paired-ablation','Exact paired source-evidence ablation results on 40 tasks per configuration.',
        'Xrrrrrrr',['Configuration',r'\shortstack{Full\\pass}',r'\shortstack{Contract\\pass}',r'\shortstack{Full-\\only}',r'\shortstack{Contract-\\only}',r'\shortstack{$\Delta$\\(pp)}',r'\shortstack{95\%\\CI}',r'$p_{\mathrm{Holm}}$'],rows,
        r'Full-only and Contract-only count discordant pairs. $\Delta$: Full minus Contract (pp); CI: paired task-bootstrap interval; $p_{\mathrm{Holm}}$: Holm-adjusted exact McNemar test.',
        colsep='2.2pt')
    # Use the same task-adjusted estimand and bootstrap as the approved Fig. 7.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'figures/scripts'))
    from fig7_adjusted_analysis import analyze
    adjusted_data, _ = analyze()
    data.pop('matched', None)
    data['adjusted_footprint'] = adjusted_data
    rows=[]
    for r in adjusted_data['analyses']['task_bootstrap']['rows']:
        lo, hi = r['rres_ratio_ci']
        clo, chi = r['copy_pp_ci']
        rows.append([r['short'], str(r['included_success_n']),
                     f"{r['rres_ratio']:.3f} [{lo:.3f}, {hi:.3f}]",
                     f"${r['copy_pp']:+.2f}$ [${clo:+.2f}$, ${chi:+.2f}$]"])
    outputs['matched-footprint']=compact('matched-footprint',
        'Task-adjusted implementation footprints among successful artifacts.',
        'Xrrr', ['Configuration', r'\shortstack{Included\\success $n$}',
                 r'\shortstack{Adjusted RRES ratio\\{[95\% CI]}}',
                 r'\shortstack{Adjusted Copy, pp\\{[95\% CI]}}'], rows,
        r'Estimates follow Equation~\ref{eq:adjusted-footprint}; brackets show pointwise 95\% task-bootstrap intervals. Copy differences are in percentage points (pp).',
        colsep='4pt')
    return outputs,data


def update(tex):
    blocks,data=build()
    for key,body in blocks.items():
        pattern=r'(% BEGIN RESULTS EVIDENCE: '+re.escape(key)+r'\n).*?(% END RESULTS EVIDENCE: '+re.escape(key)+')'
        tex,n=re.subn(pattern,lambda m:m[1]+body+'\n'+m[2],tex,flags=re.S)
        assert n==1, (key,n)
    return tex,data
