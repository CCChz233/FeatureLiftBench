"""Shared, read-only evidence for the Results structure and matched-artifact visuals."""
from pathlib import Path
import sys
import hashlib
import json
import csv
import numpy as np
from scipy.stats import wilcoxon, rankdata

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_inputs import RESULTS, STATS_PATH, MODELS, SHORT, MODEL_RECORDS, input_path, paper_task_ids


def evidence():
    with RESULTS.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    ids = paper_task_ids()
    cells = {(r['model'], r['task_id']): r for r in rows}
    assert len(rows) == len(cells) == 900
    assert set(cells) == {(m, t) for m in MODELS for t in ids}
    assert all(r['functional_pass'] in ('True', 'False') for r in rows)
    taxonomy = json.loads(input_path('coverage_data').read_text())
    tasks = {t['task_id']: t for t in taxonomy['tasks']}
    assert set(tasks) == ids
    assert all(r["lift_type"] == tasks[r["task_id"]]["lift_type"] for r in rows)
    structure = []
    for kind, names in [('lift_type', taxonomy['lift_types']), ('mechanism', taxonomy['mechanism_order'])]:
        for name in names:
            selected = sorted(t for t in ids if (tasks[t]['lift_type'] == name if kind == 'lift_type' else name in tasks[t]['mechanisms']))
            passes = [sum(cells[m, t]['functional_pass'] == 'True' for t in selected) for m in MODELS]
            structure.append({'kind':kind, 'name':name, 'n':len(selected), 'task_ids':selected,
                              'passes':passes, 'rates':[100*n/len(selected) for n in passes]})
    assert [r['n'] for r in structure] == [56,76,18,139,127,71,49]
    assert [sum(r['passes'][i] for r in structure[:3]) for i in range(6)] == [115,108,102,68,63,36]
    pro, luna = 'deepseek-v4-pro', 'gpt-5.6-luna'
    common = sorted(t for t in ids if all(cells[m,t]['functional_pass']=='True' for m in (pro,luna)))
    assert len(common)==97
    points=[]
    for t in common:
        point={'task_id':t}
        for metric, field in [('rres','rres'),('copy','copied_fraction')]:
            a,b=float(cells[pro,t][field]),float(cells[luna,t][field])
            assert np.isfinite(a) and np.isfinite(b)
            assert min(a,b)>0 if metric=='rres' else 0<=min(a,b)<=max(a,b)<=1
            point.update({f'pro_{metric}':a,f'luna_{metric}':b,f'delta_{metric}':b-a})
        points.append(point)
    summary={}
    for metric in ['rres','copy']:
        d=np.array([r[f'delta_{metric}'] for r in points])
        nonzero=d[d!=0]; ranks=rankdata(np.abs(nonzero))
        # Same two-sided Wilcoxon convention as the retained paper statistics.
        test=wilcoxon(d,zero_method='wilcox',correction=False,alternative='two-sided',method='auto')
        summary[metric]={'n':97,'median_pro':float(np.median([r[f'pro_{metric}'] for r in points])),
                         'median_luna':float(np.median([r[f'luna_{metric}'] for r in points])),
                         'median_delta':float(np.median(d)), 'q1':float(np.quantile(d,.25)),
                         'q3':float(np.quantile(d,.75)), 'min':float(d.min()),'max':float(d.max()),
                         'negative':int(sum(d<0)),'ties':int(sum(d==0)),'positive':int(sum(d>0)),
                         'wilcoxon_p':float(test.pvalue),'wilcoxon_stat':float(test.statistic),
                         'rank_biserial':float(np.sum(np.sign(nonzero)*ranks)/ranks.sum())}
    assert [(summary[m]['negative'],summary[m]['ties'],summary[m]['positive']) for m in summary]==[(85,2,10),(76,3,18)]
    prior=json.loads(STATS_PATH.read_text())['paired_pro_luna']
    assert np.isclose(summary['copy']['wilcoxon_p'],prior['wilcoxon_p'],rtol=1e-8,atol=0)
    assert np.isclose(summary['copy']['rank_biserial'],-prior['rank_biserial'])
    # Holm family: the two paired Wilcoxon tests for RRES and Copy. Keep raw p.
    order=sorted(summary,key=lambda k:summary[k]['wilcoxon_p']);running=0
    for i,k in enumerate(order):
        running=max(running,min(1,(len(order)-i)*summary[k]['wilcoxon_p']))
        summary[k]['holm_p_two_metrics']=running
    assert summary['rres']['wilcoxon_p'] < summary['copy']['wilcoxon_p']
    assert np.isclose(summary['rres']['holm_p_two_metrics'], 2*summary['rres']['wilcoxon_p'])
    assert np.isclose(summary['copy']['holm_p_two_metrics'], summary['copy']['wilcoxon_p'])
    paths=[RESULTS,STATS_PATH,input_path('coverage_data'),input_path('task_selection')]
    return {'models':[{'id':m,'short':SHORT[m],'display':MODEL_RECORDS[m]['display']} for m in MODELS],
            'structure':structure,'matched':{'n':97,'delta_definition':'Luna minus Pro within each task',
             'task_order':'task_id ascending, identical in both panels','copy_definition':'retained copied_fraction',
             'points':points,'summary':summary},
            'sources':[{'path':str(p.relative_to(Path(__file__).resolve().parents[3])),
                        'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]}
