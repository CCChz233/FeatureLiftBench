"""Portable, sanitized behavioral-obligation evidence for Fig. 6 and Table 5.

Refresh from the completed analysis ledger with --refresh. Rendering only reads
this export and checks its run-level counts; original classifications are unchanged.
"""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
from paper_inputs import ROOT, input_path

# Definitions follow the frozen reviewer-v0.2 codebook, including its C1-C9 rules.
PROPERTIES = (
    ('value_representation', 'Value / representation',
     'Returned values, result structure, canonical forms, or preserved text differ.'),
    ('call_compatibility', 'Call compatibility',
     'An existing API handles a declared argument form, callback binding, or dispatch path incompatibly.'),
    ('validation_exceptions', 'Validation / exceptions',
     'Input acceptance, rejection, or required exception behavior differs.'),
    ('evaluation_control', 'Evaluation control',
     'Whether or when an operand, callback, or branch executes differs.'),
    ('ordering_identity', 'Ordering / identity',
     'Observable order, identity, or identity-based lookup differs.'),
    ('state_lifecycle', 'State / lifecycle',
     'Observable state evolution, object lifetime, reset, or cleanup differs.'),
    ('defaults_precedence', 'Defaults / precedence',
     'Default selection, fallback, or precedence among supplied values differs.'),
    ('interaction_protocol', 'Interaction protocol',
     'Available operations violate an explicit sequencing or interaction invariant.'),
)
LEDGER = ROOT / 'reports/paper_analysis/se_obligations_ledger_20260918'


def refresh():
    source = LEDGER / 'analyzable_ledger.jsonl'
    rows = [json.loads(line) for line in source.read_text().splitlines()]
    summary = json.loads((LEDGER / 'summary.json').read_text())
    fields = ('review_id', 'task_id', 'model', 'suite_id', 'public_obligation_status',
              'failure_kind', 'behavior_primary', 'in_confirmed_property_distribution')
    data = {
        'schema_version': 1,
        'scope': 'The 201 original behavior-drift candidates within 228 retained source-exposed failures; not all failures.',
        'unit': 'run',
        'interpretation': 'Composition of confirmed behavioral violations, not property-specific failure rates.',
        'source_ledger': str(source.relative_to(ROOT)),
        'source_ledger_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'codebook_version': summary['codebook_version_for_labeled_rows'],
        'review_coverage': summary['review_coverage'],
        'selection': dict(source_exposed=241, prior_excluded=13, prior_retained=228,
                          original_behavior_candidates=201, other_coarse_categories=27),
        'properties': [dict(key=k, label=l, definition=d) for k,l,d in PROPERTIES],
        'records': [{k:r[k] for k in fields} for r in rows],
    }
    path = input_path('behavioral_obligations')
    path.write_text(json.dumps(data, indent=2) + '\n')
    return load_analysis()


def load_analysis():
    data = json.loads(input_path('behavioral_obligations').read_text())
    rows = data['records']
    assert len(rows) == len({r['review_id'] for r in rows}) == 201
    assert len({(r['model'], r['task_id']) for r in rows}) == 201
    assert data['properties'] == [dict(key=k, label=l, definition=d) for k,l,d in PROPERTIES]
    source = ROOT / data['source_ledger']
    if source.is_file():
        assert hashlib.sha256(source.read_bytes()).hexdigest() == data['source_ledger_sha256'], 'Refresh stale obligation export'
    included = [r for r in rows if r['in_confirmed_property_distribution']]
    assert all(r['public_obligation_status']=='confirmed_violation' and r['failure_kind']=='behavior_drift' for r in included)
    kinds = Counter(r['failure_kind'] for r in rows if r['public_obligation_status']=='confirmed_violation')
    assert kinds == dict(behavior_drift=176, contract_api_completion=22, artifact_constraint=1)
    assert sum(r['public_obligation_status']=='insufficient_evidence' for r in rows)==2
    assert not any(r['public_obligation_status']=='contract_question' for r in rows)
    counts = Counter(r['behavior_primary'] for r in included)
    assert len(included)==176 and len({r['task_id'] for r in included})==68
    assert sum(counts.values())==sum(counts[k] for k,_,_ in PROPERTIES)
    return {**{k:v for k,v in data.items() if k!='records'},
            'candidate_n':len(rows), 'candidate_tasks':len({r['task_id'] for r in rows}),
            'confirmed_kind_counts':dict(kinds), 'unresolved_n':2,
            'n':len(included), 'distinct_tasks':len({r['task_id'] for r in included}),
            'properties':[dict(key=k,label=l,definition=d,n=counts[k],
                 percent=100*counts[k]/len(included),
                 distinct_tasks=len({r['task_id'] for r in included if r['behavior_primary']==k}))
                 for k,l,d in PROPERTIES]}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true')
    args=parser.parse_args()
    print(json.dumps(refresh() if args.refresh else load_analysis(), indent=2))
