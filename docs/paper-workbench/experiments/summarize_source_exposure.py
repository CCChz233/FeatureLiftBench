"""Recompute offline exposure summaries and generate the paper table from CSVs."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'reports/paper_analysis/source_exposure/diagnosis'


def rows(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def write_csv(name,data):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)


def main():
    runs=rows('run_exposure.csv');events=rows('exposure_events.csv');mapping=rows('entrypoint_mapping.csv')
    assert len(runs)==900 and len({(r['model'],r['task_id']) for r in runs})==900
    tasks={r['task_id']:r for r in runs};assert len(tasks)==150
    groups={'functional_pass':'Pass','public_failure':'Behavioral-first failure',
            'hidden_failure':'Behavioral-first failure','missing_submission':'Delivery/build failure',
            'build_failure':'Delivery/build failure','isolation_failure':'Isolation-first failure'}
    for r in runs:
        evidence=[e for e in events if e['model']==r['model'] and e['task_id']==r['task_id'] and
                  e['entrypoint_file']=='True' and e['evidence_kind']=='explicit_read']
        assert bool(evidence)==bool(int(r['entrypoint_explicit_read']))
        if evidence:assert min(int(e['action_step']) for e in evidence)==int(r['first_explicit_read_action_step'])
    summary=rows('summary_by_model_outcome.csv')
    for s in summary:
        rr=[r for r in runs if (s['model']=='ALL' or s['model']==r['model']) and groups[r['outcome']]==s['outcome_group']]
        hit=[r for r in rr if int(r['entrypoint_explicit_read'])]
        assert int(s['all_runs'])==len(rr)
        assert int(s['confirmed_explicit_read_runs'])==len(hit)
    overall=[s for s in summary if s['model']=='ALL']
    table=[r'\begin{table}[tbp]',
        r' \caption{Observed entrypoint-associated file reads in the 900 main-comparison traces.}',
        r' \label{tab:source-exposure}',r' \centering',r' \small',
        r' \begin{tabularx}{\linewidth}{@{}Xrrr@{}}',r' \toprule',
        r' Final outcome & Runs & Confirmed read, $n$ (\%) & First-read step \\',r' \midrule']
    for s in overall:
        step=float(s['median_first_explicit_read_action_step']);step=f'{step:g}'
        table.append(f" {s['outcome_group']} & {s['all_runs']} & {s['confirmed_explicit_read_runs']} ({float(s['confirmed_explicit_read_percent']):.1f}) & {step} "+r'\\')
    table += [r' \bottomrule',r' \end{tabularx}',r' \par\smallskip',
        r' {\footnotesize Reads require a successful tool observation with content matching a statically mapped source file. Percentages use all runs in each outcome group; non-matches mean unconfirmed exposure. First-read step is the median one-based tool-action index among confirmed reads. Of 101 delivery/build failures, 23 have no paired tool observations. Search snippets are excluded here.}',r'\end{table}']
    (OUT/'source_exposure_table.tex').write_text('\n'.join(table)+'\n',encoding='utf-8')
    subsets=[]
    for prefix,select in [('support',lambda r:int(r['support_raw_entries'])>0),('closure',lambda r:int(r['has_closure_annotation'])>0)]:
        for category in ['ALL',*dict.fromkeys(groups.values())]:
            rr=[r for r in runs if select(r) and (category=='ALL' or groups[r['outcome']]==category)]
            valid=[r for r in rr if int(r[prefix+'_mapped_files'])>0]
            coverage=[int(r[prefix+'_exposed_files'])/int(r[prefix+'_mapped_files']) for r in valid]
            subsets.append({'annotation':prefix,'outcome':category,'tasks':len({r['task_id'] for r in rr}),
                'runs':len(rr),'nonempty_mapped_file_runs':len(valid),
                'any_annotated_file_exposed':sum(int(r[prefix+'_exposed_files'])>0 for r in valid),
                'all_mapped_files_exposed':sum(int(r[prefix+'_exposed_files'])==int(r[prefix+'_mapped_files']) for r in valid),
                'median_mapped_file_fraction':median(coverage) if coverage else '',
                'scope':'annotated files only; explicit reads or search snippets; not complete closure'})
    write_csv('subset_results.csv',subsets)
    # Fixed, outcome-stratified evidence sample for review, never performance filtering.
    sample=[]
    for model in sorted({r['model'] for r in runs}):
        for category in ['Pass','Behavioral-first failure']:
            candidates=[r for r in runs if r['model']==model and groups[r['outcome']]==category and int(r['entrypoint_explicit_read'])]
            candidates.sort(key=lambda r:hashlib.sha256(r['task_id'].encode()).hexdigest())
            for r in candidates[:2]:
                es=[e for e in events if e['model']==model and e['task_id']==r['task_id'] and e['entrypoint_file']=='True' and e['evidence_kind']=='explicit_read']
                e=min(es,key=lambda e:(int(e['action_step']),e['file']))
                sample.append(dict(outcome=r['outcome'],**e))
    write_csv('review_sample.csv',sample)
    stat={'runs':900,'tasks':150,'models':6,'mapped_declarations':sum(r['status']=='statically_mapped' for r in mapping),
          'unresolved_declarations':sum(r['status']=='unresolved' for r in mapping),
          'tasks_with_any_mapped_entrypoint':sum(int(r['mapped_entrypoint_files'])>0 for r in tasks.values()),
          'tasks_with_all_declarations_mapped':sum(int(r['unresolved_entrypoint_symbols'])==0 for r in tasks.values()),
          'nonempty_support_tasks':sum(int(r['support_raw_entries'])>0 for r in tasks.values()),
          'support_tasks_with_unresolved_entries':sum(int(r['support_unresolved_entries'])>0 for r in tasks.values()),
          'closure_annotation_tasks':sum(int(r['has_closure_annotation']) for r in tasks.values()),
          'runs_without_paired_observations':sum(int(r['paired_observations'])==0 for r in runs),
          'malformed_lines':sum(int(r['malformed_lines']) for r in runs),
          'orphan_observations':sum(int(r['orphan_observations']) for r in runs),
          'overall':overall,'subsets':subsets,
          'files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in
                   [OUT/n for n in ['run_exposure.csv','entrypoint_mapping.csv','exposure_events.csv','summary_by_model_outcome.csv','method.json']]]}
    (OUT/'statistics.json').write_text(json.dumps(stat,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in stat.items() if k not in ('files','overall','subsets')},indent=2))


if __name__=='__main__':main()
