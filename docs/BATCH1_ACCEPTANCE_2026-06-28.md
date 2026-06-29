# Batch-1 Acceptance Review - 2026-06-28

## Verdict

Batch-1 is **accepted with documented metric exceptions**.

Use this status:

```text
batch-1 structural/oracle status: pass
batch-1 evidence packet status: pass
batch-1 acceptance status: accepted_with_metric_exceptions
```

All 50 new tasks are runnable, oracle-verified, evidence-complete, and have `decision=promote`. Three metric threshold deviations are accepted as explicit exceptions because the supporting evidence still demonstrates useful, bounded, discriminative feature extraction.

## What Passed

| Check | Result |
| --- | ---: |
| Batch-1 tasks | 50 |
| Batch-1 unique sources | 49 |
| Repeated batch-1 sources | 1 (`python-dateutil` x2) |
| `validate_task()` | 50 / 50 pass |
| `audit_output_imports` gaps | 0 |
| Design notes | 50 / 50 present |
| Module probe design coverage | 50 / 50 have >=3 probes |
| Source pin/license/network metadata policy | 50 / 50 pass |
| Evidence packets | 50 / 50 complete |
| Oracle verification | 50 / 50 pass |
| Gate reports present | 50 / 50 |
| Gate report decisions | 50 `promote`, 0 blocking gates |

Evidence packet completeness:

| Evidence file | Present |
| --- | ---: |
| `gate_report.json` | 50 / 50 |
| `decision.md` | 50 / 50 |
| `validate-task.log` | 50 / 50 |
| `audit-output-imports.log` | 50 / 50 |
| `module-probes.log` | 50 / 50 |
| `oracle/result.json` | 50 / 50 |
| `naive/result.json` | 50 / 50 |
| `copy_all/result.json` | 50 / 50 |
| `flash/run.json` | 50 / 50 |

## Documented Metric Exceptions

| Task | Exception | Metric | Observed | Why accepted |
| --- | --- | --- | ---: | --- |
| `bidict__bidirectional_map_core__001` | `copy_all_metric_exception` | copy_all extraction should be `>=0.85` | `0.787448` | copy_all passes and remains separated from oracle by `0.304626`; the LOC denominator makes full-package copy_all fall below the generic threshold while still preserving the compact-vs-copy signal. |
| `sortedcontainers__sorted_list_core__001` | `low_oracle_extraction_A_tier_exception` | oracle extraction should be `>=0.20` | `0.146183` | Flash fails hidden, naive fails hidden, copy_all is `0.981184`, and the useful `SortedList` closure is naturally compact. |
| `websockets__handshake_parse_core__001` | `low_oracle_extraction_A_tier_exception` | oracle extraction should be `>=0.20` | `0.099550` | Flash fails hidden, naive fails hidden, copy_all is `0.960340`, and HTTP upgrade handshake parsing is a real but small slice of the larger websockets package. |

These exceptions are recorded in both `gate_report.json` and `decision.md`. They are not hidden gate failures.

## Flash Calibration

Flash tier is a calibration label, not a hard rejection budget.

| Flash tier | Count |
| --- | ---: |
| A | 10 |
| B | 40 |

Interpretation:

- A-tier tasks provide stronger functional discrimination against Flash.
- B-tier tasks remain useful benchmark tasks when oracle/naive/copy_all/probe evidence is strong, but they must be reported as B-tier in paper tables.
- Do not claim that batch-1 mostly defeats Flash; claim that batch-1 contains A/B calibrated tasks and that scoring reports both functional pass and extraction quality.

## Quality Summary

| Metric | Value |
| --- | ---: |
| Oracle extraction min / median / max | 0.099550 / 0.378919 / 0.594243 |
| Naive extraction min / median / max | 0.000783 / 0.015929 / 0.092537 |
| Copy-all extraction min / median / max | 0.787448 / 0.992358 / 1.009498 |
| Copy-all minus oracle min / median / max | 0.304626 / 0.585139 / 0.860790 |

The baseline separation is generally strong: naive stays low and fails hidden, copy_all usually passes with high extraction, and oracle is usually in the target band.

## Acceptance Decision

**Status: PASS with documented metric exceptions.**

Accurate statement:

> Batch-1 has 50 runnable oracle-verified tasks with complete evidence packets. It is accepted with 3 documented metric exceptions and Flash calibration distribution A=10 / B=40.

Do not write:

> Batch-1 mostly defeats Flash.

## Commands Run

```bash
PYTHONPATH=harness python3 harness/scripts/verify_all_oracles.py \
  --task-id <all batch-1 task ids> \
  --json /tmp/flb_oracle_verify_batch1.json

PYTHONPATH=harness python3 harness/scripts/verify_module_probes.py \
  --min-probes 3 <all batch-1 task dirs>
```

Additional checks were recomputed directly from `metadata.json`, `gate_report.json`, and review result files.
