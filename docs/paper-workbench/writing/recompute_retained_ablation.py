"""Compute paired ablation statistics from the selected task-level records."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import shutil

import numpy as np
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'reports/paper_analysis/source_ablation_40_20260913'
DEST = ROOT / 'docs/paper-workbench/data/source_ablation_retained_20260921'
MODELS = ['gpt-5.6-luna', 'deepseek-v4-pro', 'qwen3.6-35b-a3b-fp8']
SEED, RESAMPLES = 20260913, 100000


def main():
    def read(name):
        with (SOURCE / name).open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))

    pairs, outcomes = read('paired_outcomes.csv'), read('task_outcomes.csv')
    cells = {(r['model'], r['task_id'], r['arm']): r for r in outcomes}
    assert len(cells) == len(outcomes) == 240
    assert len(pairs) == len({(r['model'], r['task_id']) for r in pairs}) == 120
    assert len({r['task_id'] for r in pairs}) == 40
    rng = np.random.default_rng(SEED)
    results = []
    for model in MODELS:
        rows = [r for r in pairs if r['model'] == model]
        assert len(rows) == 40
        for r in rows:
            for field, arm in [('full_pass', 'full_repository'), ('contract_pass', 'contract_only')]:
                assert int(r[field]) in (0, 1)
                assert int(r[field]) == int(cells[model, r['task_id'], arm]['functional_pass'])
            assert int(r['delta']) == int(r['full_pass']) - int(r['contract_pass'])
        full = np.array([int(r['full_pass']) for r in rows])
        contract = np.array([int(r['contract_pass']) for r in rows])
        delta = full - contract
        fo, co = int((delta == 1).sum()), int((delta == -1).sum())
        ci = 100 * np.quantile(delta[rng.integers(0, 40, size=(RESAMPLES, 40))].mean(axis=1), [.025, .975])
        repos = sorted({r['repository'] for r in rows})
        sums = np.array([sum(int(r['delta']) for r in rows if r['repository'] == repo) for repo in repos])
        sizes = np.array([sum(r['repository'] == repo for r in rows) for repo in repos])
        ix = rng.integers(0, len(repos), size=(RESAMPLES, len(repos)))
        repo_ci = 100 * np.quantile(sums[ix].sum(axis=1) / sizes[ix].sum(axis=1), [.025, .975])
        results.append(dict(model=model, n=40, full_pass=int(full.sum()), contract_pass=int(contract.sum()),
                            both=int(((full == 1) & (contract == 1)).sum()), full_only=fo, contract_only=co,
                            neither=int(((full == 0) & (contract == 0)).sum()), delta_pp=100*float(delta.mean()),
                            mcnemar_exact_p=float(binomtest(fo, fo+co, .5).pvalue) if fo+co else 1.0,
                            paired_bootstrap_95ci_pp=ci.tolist(), repository_cluster_bootstrap_95ci_pp=repo_ci.tolist(),
                            outcomes={arm:dict(Counter(r['first_outcome'] for r in outcomes if r['model']==model and r['arm']==arm))
                                      for arm in ['full_repository', 'contract_only']}))
    running = 0.0
    for i, row in enumerate(sorted(results, key=lambda r:r['mcnemar_exact_p'])):
        running = max(running, min(1.0, (len(results)-i)*row['mcnemar_exact_p']))
        row['holm_adjusted_p_three_models'] = running
    pro = next(r for r in results if r['model']=='deepseek-v4-pro')
    assert (pro['full_pass'], pro['contract_pass'], pro['outcomes']['contract_only']['Missing']) == (25, 6, 18)
    DEST.mkdir(parents=True, exist_ok=True)
    for name in ['task_outcomes.csv', 'paired_outcomes.csv']:
        shutil.copy2(SOURCE/name, DEST/name)
    (DEST/'statistics.json').write_text(json.dumps(dict(seed=SEED, bootstrap_resamples=RESAMPLES, results=results), indent=2)+'\n')
    verification = dict(retained_cells=240, paired_tasks_per_model=40,
                        source_files={str(SOURCE/name):hashlib.sha256((SOURCE/name).read_bytes()).hexdigest()
                                      for name in ['task_outcomes.csv', 'paired_outcomes.csv']},
                        paired_binary_outcomes_match_cells=True, statistic_source='task-level paired binary outcomes')
    (DEST/'verification.json').write_text(json.dumps(verification, indent=2)+'\n')
    print(json.dumps(pro, indent=2))


if __name__ == '__main__':
    main()
