"""Read-only inventory for the proposed source-exposed behavioral-failure study.
Does not assign or validate semantic labels, execute tasks, or change the paper.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'docs/paper'))
from paper_inputs import RESULTS,MODELS,SHORT,paper_task_ids
OUT=Path(__file__).resolve().parent
BASE=ROOT/'reports/paper_analysis'
def read(p):
 with p.open(newline='',encoding='utf-8-sig') as h:return list(csv.DictReader(h))
def nonempty(p):return p.is_file() and p.stat().st_size>0
exposure_file=BASE/'source_exposure/diagnosis/run_exposure.csv'
index_file=BASE/'source_exposure/preflight/run_index.csv'
exposure={(r['model'],r['task_id']):r for r in read(exposure_file)}
index={(r['model'],r['task_id']):r for r in read(index_file)}
results={(r['model'],r['task_id']):r for r in read(RESULTS)}
assert len(exposure)==len(index)==len(results)==900
assert set(exposure)==set(index)==set(results)
assert {t for m,t in results}==paper_task_ids()
old_files=[BASE/'python150_prime_v2_analysis_20260905'/n for n in ['failure_root_cause_annotations.csv','postsample_annotations.csv']]
old={(r['model'],r['task_id']):r for f in old_files for r in read(f)}
selected=[k for k,r in results.items() if r['first_failure_stage'] in ['public_failure','hidden_failure'] and exposure[k]['entrypoint_explicit_read']=='1']
assert len(selected)==241
rows=[]
for model,task in sorted(selected):
 key=model,task;r=results[key];run=ROOT/index[key]['run_directory'];taskdir=ROOT/'benchmark/tasks'/task
 gate='public' if r['first_failure_stage']=='public_failure' else 'hidden'
 logpaths=[run/'eval/logs'/f'{gate}.{ext}' for ext in ['stdout','stderr']]
 submissions=[p for p in (run/'submission').rglob('*.py') if nonempty(p)]
 packages=[nonempty(taskdir/'TASK.md'),nonempty(taskdir/'metadata.json'),nonempty(taskdir/'evaluation/behavior_contract.json')]
 flags={'run_json':nonempty(run/'run.json'),'eval_result':nonempty(run/'eval/result.json'),
        'first_failure_log':any(nonempty(p) for p in logpaths),'submission_python':bool(submissions),
        'public_contract_files':all(packages),'events':nonempty(ROOT/index[key]['events_path']),
        'public_test_files':any(nonempty(p) for p in (taskdir/'public_tests').rglob('*.py')),
        'hidden_test_files':any(nonempty(p) for p in (taskdir/'hidden_tests').rglob('*.py'))}
 if flags['eval_result']:json.loads((run/'eval/result.json').read_text())
 if flags['run_json']:json.loads((run/'run.json').read_text())
 annotation=old.get(key,{})
 rows.append({'model':model,'task_id':task,'first_failure_stage':r['first_failure_stage'],
              **flags,'all_core_materials_present':all(flags.values()),'submission_python_files':len(submissions),
              'previous_annotation':bool(annotation),'previous_tier':annotation.get('close_read_tier',''),
              'previous_human_review':annotation.get('independent_human_review',''),
              'previous_defect_candidate':annotation.get('validity_override')=='benchmark_invalid_candidate' or annotation.get('evidence_eligibility')=='benchmark_invalid_candidate',
              'run_directory':str(run.relative_to(ROOT)), 'events_path':index[key]['events_path']})
summary={'scope':'Behavioral-first failures with confirmed explicit entrypoint source read',
 'candidate_runs':len(rows),'unique_tasks':len({r['task_id'] for r in rows}),
 'all_core_materials_present':sum(r['all_core_materials_present'] for r in rows),
 'materials':{f:sum(r[f] for r in rows) for f in flags},
 'previous_annotations_total':len(old),'previous_annotations_in_scope':sum(r['previous_annotation'] for r in rows),
 'previous_flagged_runs_in_scope':sum(r['previous_defect_candidate'] for r in rows),
 'previous_flagged_tasks_in_scope':len({r['task_id'] for r in rows if r['previous_defect_candidate']}),
 'independent_human_review_in_scope':sum(r['previous_human_review'].lower()=='true' for r in rows),
 'by_model':[{ 'model':SHORT[m],'candidates':sum(r['model']==m for r in rows),
               'core_present':sum(r['model']==m and r['all_core_materials_present'] for r in rows),
               'previous_annotations':sum(r['model']==m and r['previous_annotation'] for r in rows),
               'previous_flagged_runs':sum(r['model']==m and r['previous_defect_candidate'] for r in rows)} for m in MODELS],
 'limits':['File existence and non-emptiness are not semantic sufficiency or validity adjudication.',
           'Existing labels are prior L1 assistant work, not independent human review.',
           '241 is the candidate denominator; defect/evidence adjudication precedes valid-agent proportions.',
           'No new labels, experiments, paper edits, or compilation.'],
 'sources':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [RESULTS,exposure_file,index_file,*old_files]]}
with (OUT/'material_inventory.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'feasibility.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
