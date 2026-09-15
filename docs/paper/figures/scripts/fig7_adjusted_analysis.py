"""Success-conditional task fixed effects for Fig. 7; no evaluations or TeX.

Run this file to export all three analyses, bootstrap draws and Table 5 data.
The within transformation removes task means from BOTH outcomes and model
indicators. Repeated bootstrap clusters enter with multiplicity, which is
equivalent to assigning fresh task fixed effects to identical sampled copies.
"""
import argparse
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import lstsq

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from paper_inputs import (ROOT, RESULTS, MODELS, SHORT, MODEL_RECORDS,
                          MANIFEST_PATH, input_path, paper_task_ids, paper_tasks, read_csv)

REPLICATES = 10_000
SEED = 20260915
METRICS = ('rres_ratio', 'copy_pp')


def connected(information):
    """All six nodes must be linked by co-success, including after resampling."""
    adjacency = information < -1e-10
    seen, pending = {0}, [0]
    while pending:
        for node in np.flatnonzero(adjacency[pending.pop()]):
            if int(node) not in seen:
                seen.add(int(node))
                pending.append(int(node))
    return len(seen) == len(MODELS)


def solve(information, rhs):
    if not connected(information):
        raise ValueError('Disconnected configuration comparison graph')
    # The added rank-one term imposes sum(beta)=0 on the Laplacian system.
    beta = np.linalg.solve(information + np.ones((6, 6)) / 6, rhs)
    beta -= beta.mean(axis=0)
    assert np.isfinite(beta).all()
    assert np.allclose(information @ beta, rhs, atol=1e-9)
    return beta


def load_sample():
    rows = read_csv(RESULTS)
    ids, release = paper_task_ids(), paper_tasks()
    assert len(rows) == len({(r['task_id'], r['model']) for r in rows}) == 900
    assert {(r['task_id'], r['model']) for r in rows} == {(t, m) for t in ids for m in MODELS}
    assert all(r['functional_pass'] in ('True', 'False') for r in rows)
    success = defaultdict(list)
    for row in rows:
        if row['functional_pass'] == 'True':
            success[row['task_id']].append(row)
    included = {t: rs for t, rs in sorted(success.items()) if len(rs) >= 2}
    overlap = np.zeros((6, 6), dtype=int)
    blocks, observations = [], []
    for task, rs in included.items():
        rs = sorted(rs, key=lambda r: MODELS.index(r['model']))
        ix = [MODELS.index(r['model']) for r in rs]
        overlap[np.ix_(ix, ix)] += 1
        raw = np.array([[float(r['rres']), float(r['copied_fraction'])] for r in rs])
        assert np.isfinite(raw).all() and (raw[:, 0] > 0).all()
        assert ((raw[:, 1] >= 0) & (raw[:, 1] <= 1)).all()
        X = np.eye(6)[ix]
        Y = np.column_stack((np.log2(raw[:, 0]), raw[:, 1]))
        xc, yc = X - X.mean(axis=0), Y - Y.mean(axis=0)
        blocks.append({'task_id': task, 'repository': release[task]['source_repo_id'],
                       'k': len(rs), 'X': X, 'Y': Y, 'A': xc.T @ xc, 'B': xc.T @ yc})
        for row, (rres, copy) in zip(rs, raw):
            observations.append({'task_id': task, 'repository': release[task]['source_repo_id'],
                                 'model': row['model'], 'lift_type': row['lift_type'],
                                 'rres': float(rres), 'copied_fraction': float(copy),
                                 'successful_configurations_on_task': len(rs)})
    sample = {'tasks': len(included), 'artifacts': len(observations),
              'repositories': len({b['repository'] for b in blocks}),
              'all_successes': sum(map(len, success.values())),
              'singleton_successes_excluded': sum(len(rs) == 1 for rs in success.values()),
              'singleton_task_ids': sorted(t for t, rs in success.items() if len(rs) == 1),
              'tasks_by_success_count': dict(sorted(Counter(len(success[t]) for t in ids).items())),
              'included_per_model': overlap.diagonal().tolist(),
              'pairwise_overlap': overlap.tolist(),
              'lift_types': dict(Counter(rs[0]['lift_type'] for rs in included.values()))}
    assert (sample['tasks'], sample['artifacts'], sample['repositories']) == (115, 485, 97)
    assert sample['included_per_model'] == [113, 107, 99, 68, 63, 35]
    assert sample['all_successes'] == 492 and sample['singleton_successes_excluded'] == 7
    return blocks, sample, observations


def bootstrap(A, B, replicates, seed):
    """Whole-cluster pairs bootstrap, conditional on a connected graph."""
    rng = np.random.default_rng(seed)
    draws, rejected, attempts = [], 0, 0
    while len(draws) < replicates:
        attempts += 1
        if attempts > replicates * 20:
            raise RuntimeError('Too many disconnected draws; inspect overlap before inference')
        multiplicity = np.bincount(rng.integers(len(A), size=len(A)), minlength=len(A))
        info = np.einsum('t,tij->ij', multiplicity, A)
        rhs = np.einsum('t,tij->ij', multiplicity, B)
        if not connected(info):
            rejected += 1
            continue
        draws.append(solve(info, rhs))
    return np.asarray(draws), {'accepted': replicates, 'attempts': attempts,
                              'disconnected_rejected': rejected, 'seed': seed,
                              'clusters': len(A)}


def dense_verification(blocks, beta, task_equal):
    """Independent explicit-dummy weighted least squares, with six sum contrasts."""
    X, Y, weights = [], [], []
    contrast = np.vstack((np.eye(5), -np.ones(5)))
    for task_index, block in enumerate(blocks):
        task_dummy = np.zeros((block['k'], len(blocks)))
        task_dummy[:, task_index] = 1
        X.append(np.column_stack((task_dummy, block['X'] @ contrast)))
        Y.append(block['Y'])
        weights.extend([1 / block['k'] if task_equal else 1] * block['k'])
    root_w = np.sqrt(weights)[:, None]
    estimate, _, rank, _ = lstsq(np.vstack(X) * root_w, np.vstack(Y) * root_w)
    assert rank == len(blocks) + 5
    recovered = contrast @ estimate[-5:]
    error = float(np.max(np.abs(recovered - beta)))
    assert error < 1e-10, (error, 'Within estimates differ from explicit fixed effects')
    return error


@lru_cache(maxsize=2)
def analyze(replicates=REPLICATES, seed=SEED):
    if replicates < 1000:
        raise ValueError('Use at least 1000 bootstrap replicates')
    blocks, sample, observations = load_sample()
    base_A, base_B = np.array([b['A'] for b in blocks]), np.array([b['B'] for b in blocks])
    assert np.linalg.matrix_rank(base_A.sum(axis=0)) == 5
    # Exercise the disconnected-graph guard with two separate three-node groups.
    disconnected = np.zeros((6, 6))
    disconnected[:3, :3] = disconnected[3:, 3:] = np.eye(3) - np.ones((3, 3)) / 3
    assert not connected(disconnected) and connected(base_A.sum(axis=0))
    summaries, all_draws, checks = {}, {}, {}
    for name in ('task_bootstrap', 'task_equal_weight', 'repository_bootstrap'):
        task_equal = name == 'task_equal_weight'
        w = np.array([1 / b['k'] if task_equal else 1 for b in blocks])
        A, B = base_A * w[:, None, None], base_B * w[:, None, None]
        beta = solve(A.sum(axis=0), B.sum(axis=0))
        if name != 'repository_bootstrap':
            checks[name + '_dense_max_error'] = dense_verification(blocks, beta, task_equal)
        if name == 'repository_bootstrap':
            repositories = sorted({b['repository'] for b in blocks})
            membership = np.array([[b['repository'] == r for b in blocks] for r in repositories])
            A, B = np.einsum('rt,tij->rij', membership, A), np.einsum('rt,tij->rij', membership, B)
        draws, audit = bootstrap(A, B, replicates, seed + (name == 'repository_bootstrap'))
        assert np.allclose(draws.sum(axis=1), 0, atol=1e-12)
        # Quantiles on the coefficient scale, then monotone transformation.
        quantiles = np.quantile(draws, [.025, .975], axis=0, method='linear')
        result_rows = []
        for i, model in enumerate(MODELS):
            result_rows.append({'model': model, 'short': SHORT[model],
                               'included_success_n': sample['included_per_model'][i],
                               'rres_ratio': float(2 ** beta[i, 0]),
                               'rres_ratio_ci': (2 ** quantiles[:, i, 0]).tolist(),
                               'copy_pp': float(100 * beta[i, 1]),
                               'copy_pp_ci': (100 * quantiles[:, i, 1]).tolist()})
        summaries[name] = {'weighting': '1/k_t per artifact' if task_equal else 'equal artifact weight',
                           'cluster': 'repository' if name == 'repository_bootstrap' else 'task',
                           'bootstrap': audit, 'coefficients': beta.tolist(), 'rows': result_rows}
        all_draws[name] = draws
    main = np.array(summaries['task_bootstrap']['coefficients'])
    equal = np.array(summaries['task_equal_weight']['coefficients'])
    checks.update({'comparison_graph_connected': True, 'disconnected_guard_checked': True,
                   'within_design_rank': 5,
                   'sum_centered_all_replicates': True,
                   'task_equal_same_sign': (np.sign(main) == np.sign(equal)).tolist(),
                   'task_equal_rank_order_same': [bool(np.array_equal(np.argsort(main[:, j]),
                                                                   np.argsort(equal[:, j]))) for j in range(2)],
                   'task_equal_max_ratio_relative_change': float(np.max(np.abs(2 ** (equal[:, 0] - main[:, 0]) - 1))),
                   'task_equal_max_copy_pp_change': float(np.max(np.abs(equal[:, 1] - main[:, 1])) * 100)})
    sources = [RESULTS, MANIFEST_PATH, input_path('task_selection'), input_path('release_manifest'), Path(__file__)]
    payload = {'schema_version': 1, 'sample': sample,
               'models': [{'id': m, 'short': SHORT[m], 'display': MODEL_RECORDS[m]['display']} for m in MODELS],
               'estimand': {'rres': 'log2(RRES) = task FE + configuration FE; sum(configuration FE)=0; report 2^beta',
                            'copy': 'copied_fraction = task FE + configuration FE; sum(configuration FE)=0; report 100*beta pp',
                            'center': 'sum-to-zero center of configuration effects',
                            'interval': 'pointwise 95% cluster-bootstrap percentile CI; not simultaneous',
                            'scope': 'Successful artifacts only; no extrapolation to failed configurations on a task',
                            'bootstrap_variation': 'Across sampled task/repository clusters, not repeated agent runs'},
               'analyses': summaries, 'checks': checks, 'observations': observations,
               'software': {'numpy': np.__version__, 'python': sys.version.split()[0]},
               'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]}
    return payload, all_draws


def write_outputs(destination, payload, draws):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'fig7_adjusted_analysis.json').write_text(json.dumps(payload, indent=2) + '\n')
    np.savez_compressed(destination / 'fig7_bootstrap_coefficients.npz', **draws)
    columns = ['configuration', 'included_success_n', 'rres_ratio', 'rres_ci_low', 'rres_ci_high',
               'copy_pp', 'copy_ci_low', 'copy_ci_high']
    for name, analysis in payload['analyses'].items():
        filename = 'table5_adjusted.csv' if name == 'task_bootstrap' else f'fig7_{name}.csv'
        with (destination / filename).open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for row in analysis['rows']:
                writer.writerow([row['short'], row['included_success_n'], row['rres_ratio'],
                                 *row['rres_ratio_ci'], row['copy_pp'], *row['copy_pp_ci']])
    lines = ['# RQ4 adjusted footprint analysis', '',
             '115 tasks; 485 successful artifacts; 97 repositories. Six configurations in Table 1 order.',
             'Reference lines are the sum-to-zero center of configuration effects. Intervals are pointwise 95% percentile CIs.',
             'Success-conditional descriptive analysis; no causal or failed-task extrapolation.', '']
    for name, analysis in payload['analyses'].items():
        audit = analysis['bootstrap']
        lines += [f'## {name}', '',
                  f"{audit['accepted']:,} accepted draws; {audit['disconnected_rejected']} disconnected draws rejected; seed {audit['seed']}.", '',
                  '| Configuration | Included n | RRES ratio [95% CI] | Copy pp [95% CI] |',
                  '| --- | ---: | ---: | ---: |']
        for r in analysis['rows']:
            lines.append(f"| {r['short']} | {r['included_success_n']} | {r['rres_ratio']:.3f} [{r['rres_ratio_ci'][0]:.3f}, {r['rres_ratio_ci'][1]:.3f}] | {r['copy_pp']:+.2f} [{r['copy_pp_ci'][0]:+.2f}, {r['copy_pp_ci'][1]:+.2f}] |")
        lines.append('')
    lines += ['## Verification', '', '```json', json.dumps(payload['checks'], indent=2), '```', '',
              'Changing centering or including additional configurations changes the reference center.',
              'CI overlap is not a pairwise comparison test. Point-estimate ranks do not establish population ordering.',
              'The additive model summarizes configuration-by-task heterogeneity; fixed effects do not remove success selection.', '']
    (destination / 'fig7_adjusted_results.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'output/results_preview/data')
    parser.add_argument('--replicates', type=int, default=REPLICATES)
    parser.add_argument('--seed', type=int, default=SEED)
    args = parser.parse_args()
    evidence, draws = analyze(args.replicates, args.seed)
    write_outputs(args.output_dir, evidence, draws)
    print(args.output_dir / 'fig7_adjusted_results.md')
