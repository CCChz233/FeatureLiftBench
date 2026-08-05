# Python-200 Contract V2 P0 Closure

**Status:** current, P0 remediation closed  
**Verified:** 2026-08-04  
**Scope:** the 15 tasks classified as `contradictory` by the Python-200 v1 audit

This directory is the review evidence for the versioned contract-v2 overlay. It
does not rewrite the frozen Python-150 tasks or the original Python-200 v1 audit.

## Result

| Gate | Result |
| --- | ---: |
| Repaired P0 tasks | 15 / 15 |
| Strict validation | 15 / 15 |
| Test-to-behavior mappings | 15 / 15 |
| Behavior-contract metadata | 15 / 15 |
| Completed closure reviews | 15 / 15 |
| Final verdict | 15 `closed`, 0 remaining P0 contradictions |
| Reference tests | 159 / 159 passed |
| Local evaluator | 14 / 15 passed; 1 target-platform-only dependency case |
| Linux CPython 3.11 wheel coverage | 200 / 200 |

The repairs close missing or contradictory API signatures and result protocols,
publish evaluator-observed behavior, correct test mappings, strengthen weak
boundary tests, and repair two adapter references whose old behavior contradicted
the adjudicated contract. Every accepted change is declared in
`benchmark/contract_v2/repairs.json`; generated API candidates are not applied to
other tasks automatically.

## Evidence

- `task_ids.txt`: fixed P0 scope.
- `machine_audit.json` and `summary.csv`: extracted validation and mapping state.
- `dossiers/`: readable API, behavior, test, dependency, and oracle evidence.
- `decisions.jsonl`: reviewer adjudications.
- `reviews/`: test-level materialized closure ledgers.

## Reproduce

```bash
python -B scripts/generate_contract_api_patches.py --check
python -B scripts/materialize_python200_contract_v2.py --check
python -B benchmark/selection/scripts/audit_python200_wheels.py \
  --suite benchmark/contract_v2/suite.json --python-version 311
PYTHONPATH=harness python -B scripts/materialize_contract_closure_reviews.py \
  --audit reports/contract_closure_v2_p0/machine_audit.json \
  --decisions reports/contract_closure_v2_p0/decisions.jsonl \
  --output reports/contract_closure_v2_p0/reviews --check
PYTHONPATH=harness python -B scripts/audit_python200_contract_closure.py \
  --suite benchmark/contract_v2/suite.json \
  --output reports/contract_closure_v2_p0 \
  --task-list reports/contract_closure_v2_p0/task_ids.txt --check
```

The full 200-task closure check remains fail-closed because the 168 v1
`underspecified` tasks are the next remediation tier and are not silently promoted
by this P0 repair.

The local evaluator exception is
`dateparser__parse_settings_pipeline_core__001`: its required `regex==2024.11.6`
wheel is pinned for the experiment target (Linux x86_64, CPython 3.11), not this
macOS arm64 CPython 3.12 workstation. Its 9 reference tests pass locally, and the
target wheel is covered by the suite-level wheel audit. The other 14 repaired
tasks pass build, public tests, hidden tests, runtime import-origin checks, and all
isolation gates in fresh evaluator environments.
