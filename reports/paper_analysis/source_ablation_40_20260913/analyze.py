"""Read retained source-ablation records; never execute archive code or agents."""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ARMS = ('full_repository', 'contract_only')
MODELS = ('gpt-5.6-luna', 'deepseek-v4-pro', 'qwen3.6-35b-a3b-fp8')
GATES = ('build_pass', 'public_tests_pass', 'hidden_tests_pass', 'isolation_pass')
STAGES = ('Build', 'Public', 'Hidden', 'Isolation')
SERVICE = {'LLMTimeoutError', 'LLMServiceUnavailableError', 'LLMRateLimitError', 'LLMBadRequestError'}


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def table(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def paired(rows):
    n = len(rows)
    a = sum(r['full_pass'] and r['contract_pass'] for r in rows)
    b = sum(r['full_pass'] and not r['contract_pass'] for r in rows)
    c = sum(not r['full_pass'] and r['contract_pass'] for r in rows)
    d = n-a-b-c
    p = min(1., 2*sum(math.comb(b+c, i) for i in range(min(b, c)+1))/2**(b+c)) if b+c else 1.
    return {'n': n, 'full_pass': a+b, 'contract_pass': a+c, 'both': a,
            'full_only': b, 'contract_only': c, 'neither': d,
            'delta_pp': 100*(b-c)/n if n else None, 'mcnemar_exact_p': p}


def main(base):
    sample = read(base / 'source_ablation_40.json')
    tasks = sample['tasks']
    ids = {t['task_id'] for t in tasks}
    assert len(ids) == 40 and len({t['source_repo_id'] for t in tasks}) == 38
    local = read(ROOT / 'docs/paper/experiments/source_ablation_40.json')
    assert tasks == local['tasks']
    paper = read(ROOT / 'docs/paper/paper_sources.json')
    with (ROOT / paper['inputs']['main_results']).open(encoding='utf-8-sig', newline='') as f:
        main_rows = list(csv.DictReader(f))
    assert ids <= {r['task_id'] for r in main_rows}
    rows, pairs, checks, retried, mismatches = [], [], [], [], []
    digest = hashlib.sha256()
    for model in MODELS:
        folder = base / model / 'source-ablation-40-r1'
        cells = {}
        for arm in ARMS:
            for p in (folder / arm).iterdir():
                if p.is_dir() and '.infra_' in p.name:
                    retried.append({'model': model, 'arm': arm, 'archive': p.name})
            for task in tasks:
                tid = task['task_id']
                cell = folder / arm / tid
                run = read(cell / 'run.json')
                ep = cell / 'eval/result.json'
                result = read(ep) if ep.exists() else {}
                digest.update((cell / 'run.json').read_bytes())
                if result: digest.update(ep.read_bytes())
                inventory = read(cell / 'agent/agent_visible_inventory.json')
                runtime_iterations = sorted({read(p).get('max_iterations') for p in (cell/'agent').rglob('base_state.json')})
                assert runtime_iterations == [500]
                cond, config = run['experiment_conditions'], run['agent_config']
                assert run['task_id'] == tid
                assert run['ablation']['source_context'] == arm
                assert inventory['agent_source_available'] == (arm == ARMS[0])
                assert inventory['repo_present'] == (arm == ARMS[0])
                assert cond['benchmark_tests_visible_to_agent'] is False
                assert cond['source_hints_visible_to_agent'] is False
                assert cond['agent_harness_mount'] == 'package'
                delivered = run['submission']['exists'] is True
                assert bool(result) == delivered
                passed = delivered and all(result.get(k) is True for k in GATES)
                first = 'Pass' if passed else 'Missing' if not delivered else next(s for k,s in zip(GATES,STAGES) if result.get(k) is not True)
                codes, last_error, actions = [], '', 0
                events = cell / 'agent/openhands_events.jsonl'
                for line in events.read_text(encoding='utf-8').splitlines():
                    if not line.strip(): continue
                    event = json.loads(line)
                    if event.get('source') == 'agent' and event.get('kind') == 'ActionEvent': actions += 1
                    if event.get('kind') == 'ConversationErrorEvent':
                        codes.append(event.get('code', 'unknown'))
                        last_error = event.get('code', 'unknown')
                command = run['agent'].get('command', [])
                network = command[command.index('--network')+1] if '--network' in command else ''
                row = {'model': model, 'arm': arm, 'task_id': tid,
                       'repository': task['source_repo_id'], 'cohort': task['cohort'], 'lift_type': task['lift_type'],
                       'functional_pass': int(passed), 'delivered': int(delivered), 'first_outcome': first,
                       'run_status': run['status'], 'last_conversation_error': last_error,
                       'service_error_recorded': int(bool(set(codes) & SERVICE)),
                       'conversation_error_codes': '|'.join(sorted(set(codes))),
                       'api_error_without_submission': int(not delivered and bool(set(codes) & SERVICE)),
                       'max_steps': cond['agent_max_steps'], 'timeout_seconds': cond['agent_timeout_seconds'],
                       'persisted_max_iterations': 500,
                       'context_window_tokens': config['context_window_tokens'],
                       'reserved_output_tokens': config['reserved_output_tokens'],
                       'agent_network': network, 'eval_network': cond['evaluator_runtime'].get('network'),
                       'eval_capsule': result.get('evaluation_capsule_digest', ''),
                       'agent_exit_status': run['agent'].get('usage', {}).get('exit_status', ''),
                       'record_path': str((cell/'run.json').relative_to(base)).replace('\\','/')}
                if passed and run['status'] != 'passed': mismatches.append({'model':model,'arm':arm,'task_id':tid,'run_status':run['status'],'functional_pass':True})
                rows.append(row)
                cells[arm, tid] = (row, run, (cell/'workspace/TASK.md').read_text(encoding='utf-8'))
        for task in tasks:
            tid = task['task_id']
            full, fr, ft = cells[ARMS[0], tid]
            contract, cr, ct = cells[ARMS[1], tid]
            # Differences are allowed only in source-availability instructions.
            def obligations(text):
                return '\n'.join(line for line in text.splitlines() if not line.startswith(('Treat the requested feature as a complete task-scoped module', 'Benchmark-authored evaluator tests are not included')))
            assert obligations(ft) == obligations(ct), tid
            for k in ('max_steps', 'timeout_seconds', 'context_window_tokens','reserved_output_tokens','agent_network','eval_network'):
                assert full[k] == contract[k], (model, tid, k)
            diffkeys = [k for k in fr['agent_config'] if fr['agent_config'][k] != cr['agent_config'].get(k)]
            capsule_equal = full['eval_capsule'] == contract['eval_capsule'] if full['delivered'] and contract['delivered'] else None
            assert capsule_equal is not False, (model, tid)
            checks.append({'model':model,'task_id':tid,'contract_obligations_equal':True,'paired_config_differences':diffkeys,'capsule_equal_when_both_evaluated':capsule_equal})
            pairs.append({'model':model,'task_id':tid,'repository':task['source_repo_id'],'cohort':task['cohort'],'lift_type':task['lift_type'],
                          'full_pass':full['functional_pass'],'contract_pass':contract['functional_pass'],
                          'delta':full['functional_pass']-contract['functional_pass'],
                          'full_outcome':full['first_outcome'],'contract_outcome':contract['first_outcome'],
                          'both_delivered':int(full['delivered'] and contract['delivered']),
                          'any_service_error':int(full['service_error_recorded'] or contract['service_error_recorded']),
                          'any_api_empty':int(full['api_error_without_submission'] or contract['api_error_without_submission'])})
    assert len(rows)==240 and len(pairs)==120
    headline = read(base/'summary.json')['models']
    for r in rows:
        archived = next(x for x in headline[r['model']]['cells'][r['arm']]['cells'] if x['task_id']==r['task_id'])
        assert bool(r['functional_pass']) == archived['functional_pass']
    rng = np.random.default_rng(20260913)
    results=[]
    for model in MODELS:
        pr=[p for p in pairs if p['model']==model]
        s=paired(pr)
        x=np.array([p['delta'] for p in pr])
        s['paired_bootstrap_95ci_pp']=(100*np.quantile(x[rng.integers(0,40,size=(100000,40))].mean(axis=1),[.025,.975])).tolist()
        repos=sorted({p['repository'] for p in pr})
        sums=np.array([sum(p['delta'] for p in pr if p['repository']==repo) for repo in repos])
        sizes=np.array([sum(p['repository']==repo for p in pr) for repo in repos])
        ix=rng.integers(0,len(repos),size=(100000,len(repos)))
        s['repository_cluster_bootstrap_95ci_pp']=(100*np.quantile(sums[ix].sum(axis=1)/sizes[ix].sum(axis=1),[.025,.975])).tolist()
        s['model']=model
        s['sensitivity_both_delivered']=paired([p for p in pr if p['both_delivered']])
        s['sensitivity_no_recorded_service_error']=paired([p for p in pr if not p['any_service_error']])
        s['sensitivity_exclude_api_empty_pairs']=paired([p for p in pr if not p['any_api_empty']])
        uncertain_full=sum(r['api_error_without_submission'] for r in rows if r['model']==model and r['arm']==ARMS[0])
        uncertain_contract=sum(r['api_error_without_submission'] for r in rows if r['model']==model and r['arm']==ARMS[1])
        s['api_empty_outcome_bounds_delta_pp']=[s['delta_pp']-100*uncertain_contract/40,s['delta_pp']+100*uncertain_full/40]
        s['outcomes']={arm:dict(Counter(r['first_outcome'] for r in rows if r['model']==model and r['arm']==arm)) for arm in ARMS}
        s['full_only_contract_failure_stages']=dict(Counter(p['contract_outcome'] for p in pr if p['delta']==1))
        s['full_only_tasks']=[p['task_id'] for p in pr if p['delta']==1]
        s['contract_only_tasks']=[p['task_id'] for p in pr if p['delta']==-1]
        s['both_fail_tasks']=[p['task_id'] for p in pr if not p['full_pass'] and not p['contract_pass']]
        results.append(s)
    ordered=sorted(results,key=lambda s:s['mcnemar_exact_p'])
    last=0
    for i,s in enumerate(ordered):
        last=max(last,min(1.,(len(ordered)-i)*s['mcnemar_exact_p']))
        s['holm_adjusted_p_three_models']=last
    table('task_outcomes.csv',rows)
    table('paired_outcomes.csv',pairs)
    table('api_empty_review_queue.csv',[r for r in rows if r['api_error_without_submission']])
    save('statistics.json',{'seed':20260913,'bootstrap_resamples':100000,'results':results})
    save('verification.json',{'retained_cells':len(rows),'paired_tasks_per_model':40,'repositories':38,
                            'source_records_sha256':digest.hexdigest(),'headline_counts_agree':True,
                            'sample_equals_prespecified_local_sample':True,'sample_within_current_paper':True,
                            'checks':checks,'archived_retry_directories':retried,'passing_artifact_run_status_mismatches':mismatches})
    names={'gpt-5.6-luna':'GPT-5.6 Luna','deepseek-v4-pro':r'DeepSeek V4 Pro$^{\dagger}$','qwen3.6-35b-a3b-fp8':'Qwen3.6-35B-A3B-FP8'}
    lines=[r'\begin{table}[tbp]',r' \caption{Source-evidence ablation on 40 paired tasks per configuration (240 retained outcomes).}',
           r' \label{tab:source-ablation}',r' \centering\footnotesize',r' \setlength{\tabcolsep}{3pt}',
           r' \begin{tabularx}{\linewidth}{@{}Xrrrccr@{}}',r' \toprule',
           r' Configuration & Full & Contract only & $\Delta$ (pp) & 95\% CI & $b/c$ & $p_{\mathrm{Holm}}$ \\',r' \midrule']
    for s in results:
        lo,hi=s['paired_bootstrap_95ci_pp']
        ptext=f"{s['holm_adjusted_p_three_models']:.5f}"
        lines.append(f" {names[s['model']]} & {s['full_pass']}/40 & {s['contract_pass']}/40 & +{s['delta_pp']:.1f} & [{lo:.1f}, {hi:.1f}] & {s['full_only']}/{s['contract_only']} & {ptext} " + r'\\')
    lines.extend([r' \bottomrule',r' \end{tabularx}',r' \par\smallskip\begin{minipage}{\linewidth}\footnotesize',
                  r' Full provides the complete source repository and contract; Contract only omits repository evidence. Missing submissions count as failures. $\Delta$ is Full minus Contract only; intervals are paired task-bootstrap percentile intervals in percentage points (100,000 resamples). $b/c$ counts Full-only/Contract-only successes. Exact two-sided McNemar tests use Holm adjustment across the three exploratory comparisons.',
                  r' $\dagger$: all 18 missing Pro Contract-only submissions have recorded LLM timeouts; its full-sample difference includes service interruptions. On the 22 pairs without these errors, Pro passes 11 versus six tasks (unadjusted $p=0.125$).',
                  r' \end{minipage}',r'\end{table}'])
    (OUT/'source_ablation_table.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(results,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--records',type=Path,default=ROOT/'experiments/source_ablation_review_20260913/source-ablation-40-r1-full')
    main(parser.parse_args().records)
