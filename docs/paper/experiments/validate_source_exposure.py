"""Verify sampled trace evidence and record the exact offline inputs; no agent calls."""
import csv
import hashlib
import json
from pathlib import Path
from diagnose_source_exposure import normalized, read_kind

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'reports/paper_analysis/source_exposure'


def csv_rows(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()


def main():
    index=csv_rows(BASE/'preflight/run_index.csv')
    byrun={(r['model'],r['task_id']):r for r in index}
    sample=csv_rows(BASE/'diagnosis/review_sample.csv');checked=[]
    for row in sample:
        path=ROOT/byrun[row['model'],row['task_id']]['events_path']
        needed={row['action_id'],row['observation_id']};ev={}
        with path.open(encoding='utf-8') as f:
            for line in f:
                e=json.loads(line)
                if e.get('id') in needed:ev[e['id']]=e
        action=ev[row['action_id']]['action'];event=ev[row['observation_id']]
        assert event['action_id']==row['action_id']
        observation=event['observation']
        assert not observation.get('is_error') and observation.get('exit_code',0) in (0,None)
        text='\n'.join(x.get('text','') for x in observation.get('content',[]) if isinstance(x,dict))
        assert hashlib.sha256(text.encode()).hexdigest()==row['observation_sha256']
        pair=json.loads(row['matched_source_pair'])
        source=ROOT/'benchmark/tasks'/row['task_id']/'repo'/row['file']
        for content in (text,source.read_text(encoding='utf-8-sig')):
            lines=[normalized(x) for x in content.splitlines()]
            assert any([a,b]==pair for a,b in zip(lines,lines[1:]))
        assert read_kind(action,observation,row['file'])=='explicit_read'
        checked.append({'model':row['model'],'task_id':row['task_id'],'file':row['file'],
                        'paired_observation_and_source_content_agree':True})
    paths={ROOT/r['events_path'] for r in index}
    for r in csv_rows(BASE/'diagnosis/exposure_events.csv'):
        paths.add(ROOT/'benchmark/tasks'/r['task_id']/'repo'/r['file'])
    paths.update(BASE/'preflight'/name for name in ('preflight.json','run_index.csv','targets.private.json'))
    hashes=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in sorted(paths)]
    (BASE/'diagnosis/input_hashes.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    result={'sample_runs':len(checked),'sample_unique_tasks':len({r['task_id'] for r in checked}),
            'sample_selection':'First two confirmed reads per model and Pass/behavioral-first group, ordered by SHA256(task_id)',
            'checks':checked,'hashed_input_files':len(hashes),
            'scope':'Programmatic evidence consistency plus assistant inspection; not independent human audit or detector precision/recall estimate'}
    (BASE/'diagnosis/verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'Checked {len(checked)} sampled runs; hashed {len(hashes)} inputs. No model or evaluator execution.')


if __name__=='__main__':main()
