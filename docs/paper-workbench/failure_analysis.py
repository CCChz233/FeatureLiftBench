"""Shared, source-checked counts for the manuscript failure figure and table."""
from collections import Counter
from functools import lru_cache
import hashlib

from paper_inputs import ROOT, RESULTS, MODELS, SHORT, input_path, read_csv, read_json

CATEGORIES = (
    ('behavior_drift', 'Behavior drift',
     'Required API exists, but observable behavior differs from the contract.'),
    ('contract_api_completion', 'API completion',
     'Required export, member, or API path is missing.'),
    ('dependency_closure', 'Dependency closure',
     'A required helper, resource, registry, or dependency is absent.'),
    ('packaging_modularization', 'Packaging',
     'Implementation is present but not exposed through the standalone package.'),
    ('localization', 'Localization',
     'Trajectory and submission indicate the wrong implementation region.'),
    ('unknown', 'Unknown',
     'Available evidence does not distinguish a primary category.'),
)


@lru_cache(maxsize=1)
def counts():
    path = input_path('failure_classifications')
    provenance = read_json(input_path('failure_classification_provenance'))
    assert hashlib.sha256(path.read_bytes()).hexdigest() == provenance['classification_sha256']
    rows = read_csv(path)
    keys = {(r['model'], r['task_id']) for r in rows}
    assert len(rows) == len(keys) == 241
    assert len({r['task_id'] for r in rows}) == 89
    exposure_rows = read_csv(ROOT / 'reports/paper_analysis/source_exposure/diagnosis/run_exposure.csv')
    exposure = {(r['model'], r['task_id']): r for r in exposure_rows}
    assert len(exposure) == len(exposure_rows) == 900
    selected = {(r['model'], r['task_id']) for r in read_csv(RESULTS)
                if r['first_failure_stage'] in ('public_failure', 'hidden_failure')
                and exposure[r['model'], r['task_id']]['entrypoint_explicit_read'] == '1'}
    assert keys == selected
    valid = [r for r in rows if r['evidence_eligibility'] == 'valid_agent_evidence']
    excluded = [r for r in rows if r['evidence_eligibility'] != 'valid_agent_evidence']
    assert len(valid) == 228 and len(excluded) == 13
    assert all(r['evidence_eligibility'] == 'benchmark_invalid_candidate' for r in excluded)
    assert len({r['task_id'] for r in excluded}) == 3
    pooled = Counter(r['root_cause_primary'] for r in valid)
    assert dict(pooled) == dict(behavior_drift=201, contract_api_completion=16,
                              dependency_closure=8, packaging_modularization=2, unknown=1)
    assert set(pooled) <= {c[0] for c in CATEGORIES}
    by_model = []
    for model, expected in zip(MODELS, (26, 31, 30, 35, 42, 64)):
        subset = Counter(r['root_cause_primary'] for r in valid if r['model'] == model)
        assert sum(subset.values()) == expected
        by_model.append({'model': model, 'short': SHORT[model], 'n': expected,
                         'counts': {k: subset[k] for k, _, _ in CATEGORIES}})
    return {'candidates': len(rows), 'tasks': 89, 'excluded': len(excluded),
            'excluded_tasks': 3, 'valid': len(valid), 'by_model': by_model,
            'pooled': {k: pooled[k] for k, _, _ in CATEGORIES}}
