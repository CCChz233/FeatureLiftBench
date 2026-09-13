"""One paper table, two aligned panels; saved outcomes only."""
from statistics import mean, median


def quantile(v, q):
    v=sorted(v); i=(len(v)-1)*q; lo=int(i); hi=min(lo+1,len(v)-1)
    return v[lo]+(v[hi]-v[lo])*(i-lo)


def comprehensive_table(groups, models, short):
    lines=[r'\begin{table}[tbp]',
           r' \caption{Functional correctness, extraction characteristics, and efficiency on the common 150-task comparison.}',
           r' \label{tab:main}', r' \centering\footnotesize', r' \setlength{\tabcolsep}{3pt}',
           r' \renewcommand{\arraystretch}{1.12}',
           r' \textbf{(a) Correctness and extraction characteristics}\par\smallskip',
           r' \begin{tabular}{@{}lr rrr rrr@{}}',r' \toprule',
           r' & & \multicolumn{3}{c}{RRES} & \multicolumn{3}{c}{Copy} \\',
           r' \cmidrule(lr){3-5}\cmidrule(lr){6-8}',
           r' Configuration & Pass@1 (\%) & Mean & Median & IQR & Mean & Median & IQR \\',r' \midrule']
    efficiency=[]
    for m in models:
        rows=groups[m]; passed=[r for r in rows if r['functional_pass'].lower()=='true']
        assert len(rows)==150 and passed
        values=[short[m],f'{100*len(passed)/len(rows):.1f}']
        for field in ('rres','copied_fraction'):
            v=[float(r[field]) for r in passed]
            values.extend([f'{mean(v):.3f}',f'{median(v):.3f}',f'[{quantile(v,.25):.3f}, {quantile(v,.75):.3f}]'])
        lines.append(' '+' & '.join(values)+r' \\')
        steps=[float(r['process_assistant_steps']) for r in rows if r['process_assistant_steps']!='']
        assert len(steps)==150
        tokenfield='process_incremental_tokens' if m in models[:2] else 'process_total_tokens'
        tokens=[float(r[tokenfield]) for r in rows if r[tokenfield]!='' and r['process_usage_unverified'].lower()=='false']
        if short[m] in ('Luna','GLM'):assert not tokens
        else:assert len(tokens)==150
        mark=r'$^{\dagger}$' if m in models[:2] else (r'$^{\ddagger}$' if tokens else '')
        efficiency.append([short[m]+mark,f'{median(steps):.1f}',f'{quantile(steps,.9):.1f}',
                           f'{median(tokens)/1000:.1f}' if tokens else '---',
                           f'{quantile(tokens,.9)/1000:.1f}' if tokens else '---',str(len(tokens))])
    lines += [r' \bottomrule',r' \end{tabular}',r' \par\medskip',
              r' \textbf{(b) Efficiency across all assigned tasks}\par\smallskip',
              r' \begin{tabular}{@{}lrrrrr@{}}',r' \toprule',
              r' & \multicolumn{2}{c}{Steps} & \multicolumn{2}{c}{Tokens ($10^3$)} & \\',
              r' \cmidrule(lr){2-3}\cmidrule(lr){4-5}',
              r' Configuration & Median & P90 & Median & P90 & $n_{\mathrm{tokens}}$ \\',r' \midrule']
    lines += [' '+' & '.join(row)+r' \\' for row in efficiency]
    lines += [r' \bottomrule',r' \end{tabular}',r' \par\smallskip\begin{minipage}{\linewidth}\footnotesize',
              r' Pass@1 uses one retained final outcome per assigned task, including non-delivery, under the recovery policy in Section~\ref{sec:protocol}. RRES and Copy use only passing artifacts; passing counts are 115/108/102/68/63/36 in row order. IQR is shown as [Q1, Q3]. Steps use all 150 tasks per configuration. $\dagger$: uncached prompt plus completion tokens; $\ddagger$: provider total tokens. These token definitions are not comparable across the two groups; missing accounting is shown as a dash. Footprint measures describe extraction characteristics, not a scalar quality ranking.',
              r' \end{minipage}',r'\end{table}']
    return '\n'.join(lines)
