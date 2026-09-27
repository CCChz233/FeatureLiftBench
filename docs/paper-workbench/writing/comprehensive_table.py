"""Render the FSE main-table layout with values computed from saved outcomes."""
from pathlib import Path
from statistics import median
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
        # Count all input tokens, including cached input, plus output tokens.
        verified=[r for r in rows if r['process_total_tokens']!='' and r['process_usage_unverified'].lower()=='false']
        tokens=[]
        for r in verified:
            total=float(r['process_prompt_tokens'])+float(r['process_completion_tokens'])
            assert total==float(r['process_total_tokens']), (m, r['task_id'])
            tokens.append(total)
        if short[m] in ('Luna','GLM'): assert not tokens
        else: assert len(tokens)==150
        mark=''
        score=f'{len(passed)} ({100*len(passed)/len(rows):.1f})'
        if len(passed)==highest: score=r'\textbf{'+score+'}'
        values=[r'\mbox{'+full[m]+'}'+mark,score]
        if m in confirmed:
            assert confirmed[m]['assigned']==len(rows)
            token_cells=[f"{confirmed[m]['median_k']/10:.2f}",f"{confirmed[m]['p90_k']/10:.2f}"]
        else:
            token_cells=[f'{median(tokens)/10000:.2f}',f'{quantile(tokens,.9)/10000:.2f}']
        values.extend([f'{median(steps):.1f}',f'{quantile(steps,.9):.1f}',*token_cells])
        lines.append('    '+' & '.join(values)+r' \\')
    template=(Path(__file__).parent/'templates/main_table.tex').read_text().rstrip()
    assert template.count('@@ROWS@@')==1
    return template.replace('@@ROWS@@','\n'.join(lines))
