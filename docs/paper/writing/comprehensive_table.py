"""Render the FSE main-table layout with values computed from saved outcomes."""
from pathlib import Path
from statistics import mean, median
import json


def quantile(v, q):
    v=sorted(v); i=(len(v)-1)*q; lo=int(i); hi=min(lo+1,len(v)-1)
    return v[lo]+(v[hi]-v[lo])*(i-lo)


def comprehensive_table(groups, models, short, full):
    from paper_inputs import input_path
    # Keep author-confirmed aggregate corrections separate from raw run metrics.
    confirmed=json.loads(input_path('author_result_clarifications').read_text())['token_totals']
    lines=[]
    highest=max(sum(r['functional_pass'].lower()=='true' for r in groups[m]) for m in models)
    for m in models:
        rows=groups[m]; passed=[r for r in rows if r['functional_pass'].lower()=='true']
        assert len(rows)==150 and passed
        steps=[float(r['process_assistant_steps']) for r in rows if r['process_assistant_steps']!='']
        assert len(steps)==150
        tokenfield='process_incremental_tokens' if m in models[:2] else 'process_total_tokens'
        tokens=[float(r[tokenfield]) for r in rows if r[tokenfield]!='' and r['process_usage_unverified'].lower()=='false']
        if short[m] in ('Luna','GLM'): assert not tokens
        else: assert len(tokens)==150
        mark=r'$^{\dagger}$' if m in models[:2] else r'$^{\ddagger}$'
        score=f'{len(passed)} ({100*len(passed)/len(rows):.1f})'
        if len(passed)==highest: score=r'\textbf{'+score+'}'
        values=[full[m]+mark,score]
        for field in ('rres','copied_fraction'):
            v=[float(r[field]) for r in passed]
            values.extend([f'{mean(v):.3f}',f'{median(v):.3f}',f'[{quantile(v,.25):.3f}, {quantile(v,.75):.3f}]'])
        if m in confirmed:
            assert confirmed[m]['assigned']==len(rows)
            token_cells=[f"{confirmed[m]['median_k']:.1f}",f"{confirmed[m]['p90_k']:.1f}"]
        else:
            token_cells=[f'{median(tokens)/1000:.1f}',f'{quantile(tokens,.9)/1000:.1f}']
        values.extend([f'{median(steps):.1f}',f'{quantile(steps,.9):.1f}',*token_cells])
        lines.append('    '+' & '.join(values)+r' \\')
    template=(Path(__file__).parent/'templates/main_table.tex').read_text().rstrip()
    assert template.count('@@ROWS@@')==1
    return template.replace('@@ROWS@@','\n'.join(lines))
