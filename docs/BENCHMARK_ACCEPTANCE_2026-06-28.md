# Benchmark Acceptance Review - 2026-06-28

## Verdict

The 100-task suite is **accepted**.

Use this status:

```text
status: accepted
mechanical oracle suite: pass
batch-0 policy: grandfathered
batch-1 quality status: accepted_with_metric_exceptions
```

Batch-0 remains a frozen legacy set: oracle + design note + deterministic tests are sufficient. Batch-1 has complete evidence packets and is accepted with 3 documented metric exceptions.

## What Passed

| Check | Result |
| --- | ---: |
| Formal tasks under `benchmark/tasks/` | 100 |
| Batch-0 / legacy tasks | 50 |
| Batch-1 tasks | 50 |
| `validate_task()` structural validation | 100 / 100 pass |
| Oracle directories present | 100 / 100 |
| `verify_all_oracles.py` | 100 / 100 pass |
| Design notes present | 100 / 100 |
| Module probe design coverage | 100 / 100 have >=3 probes |
| Public + hidden test files present | 100 / 100 |
| Source pin/license/network metadata policy | 100 / 100 pass |
| `audit_output_imports --fail-on-gap` | 100 / 100 pass |
| Full-board unique sources | 75 |
| Batch-1 unique sources | 49 |

Repo concentration is acceptable:

- batch-1 has only one repeated repo: `python-dateutil` with 2 tasks;
- full-board real OSS concentration is within the 5-task limit for `coveragepy` and `jinja2`;
- `vibe_app` has 7 curated tasks and should continue to be reported separately.

## Batch-1 Acceptance

| Check | Result |
| --- | ---: |
| `gate_report.json` | 50 / 50 |
| `decision.md` | 50 / 50 |
| `flash/run.json` | 50 / 50 |
| oracle / naive / copy_all result files | 50 / 50 |
| validate / audit / module-probes logs | 50 / 50 |
| gate report decisions | 50 `promote` |
| blocking gates | 0 |

Flash calibration distribution:

| Flash tier | Count |
| --- | ---: |
| A | 10 |
| B | 40 |

B-tier is reported as a calibration label, not a rejection budget. The paper must disclose this distribution and must not claim that batch-1 mostly defeats Flash.

## Documented Metric Exceptions

| Task | Exception | Observed |
| --- | --- | ---: |
| `bidict__bidirectional_map_core__001` | `copy_all_metric_exception` for copy_all extraction `<0.85` | `0.787448` |
| `sortedcontainers__sorted_list_core__001` | `low_oracle_extraction_A_tier_exception` for oracle extraction `<0.20` | `0.146183` |
| `websockets__handshake_parse_core__001` | `low_oracle_extraction_A_tier_exception` for oracle extraction `<0.20` | `0.099550` |

These exceptions are machine-readable in `gate_report.json` and explained in `decision.md`. They are accepted because oracle/naive/copy_all/Flash evidence still demonstrates useful, bounded, discriminative feature extraction.

## Remediation Completed

| Item | Before | After |
| --- | --- | --- |
| `audit_output_imports --fail-on-gap` | 13 gaps | 100 / 100 pass |
| batch-1 review packet | incomplete | 50 / 50 complete |
| batch-1 `gate_report.json` | partial | 50 / 50 |
| batch-1 `decision.md` | partial | 50 / 50 |
| batch-1 `flash/run.json` | missing / partial | 50 / 50 |
| `h2` G1 oracle extraction | 0.199846 | 0.200039 |
| `passlib` G3 copy_all | 0.613 | ~1.0 |
| batch-0 naive/copy_all | policy undecided | grandfathered |

## Paper Wording

Acceptable:

> The 100-task suite is structurally complete and oracle-passing. Batch-1 has complete quality evidence and is accepted with three documented metric exceptions. Flash calibration is reported as A=10 / B=40.

Avoid:

> Batch-1 mostly defeats Flash.

## Commands Run

```bash
PYTHONPATH=harness python3 - <<'PY'
from pathlib import Path
from featureliftbench.validate import validate_task
roots=sorted(p for p in Path('benchmark/tasks').iterdir() if (p/'metadata.json').is_file())
invalid=[(p.name, validate_task(p).errors) for p in roots if not validate_task(p).valid]
print(f'total={len(roots)} invalid={len(invalid)}')
PY

PYTHONPATH=harness python3 harness/scripts/audit_output_imports.py --fail-on-gap
PYTHONPATH=harness python3 harness/scripts/verify_all_oracles.py --json /tmp/flb_oracle_verify_100.json
PYTHONPATH=harness python3 harness/scripts/verify_module_probes.py --min-probes 3
```
