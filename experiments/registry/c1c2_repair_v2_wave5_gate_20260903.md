# Freeze v2 wave 5 gate — 2026-09-03

> Repair evidence only. **No new freeze_id / suite_id / task_set_sha256.**
> Old Flash 132/200 stays on the v1 freeze.

## Gate

`reports/benchmark_gate/python200_hard_20260903_v2_repair2/`

| Check | pass | fail | undetermined |
| --- | ---: | ---: | ---: |
| L1_PACKAGE | 200 | 0 | 0 |
| L2_C1_SURFACE | 200 | 0 | 0 |
| L2_C2_ENTRYPOINT | 200 | 0 | 0 |
| L3_G2PRIME_UPSTREAM | 200 | 0 | 0 |
| L3_ORACLE_N3 | 200 | 0 | 0 |
| L4_ISOLATION_N3 | 200 | 0 | 0 |
| L5_C4_TEST_OVERLAP | 200 | 0 | 0 |
| L5_TASK_LEAKAGE | 200 | 0 | 0 |
| SOURCE_IDENTITY | 200 | 0 | 0 |

Labels: **200 `meets_standard` / 0 `violates` / 0 `undetermined`**.

Oracle image: `featureliftbench-eval:python200-prime-769f2486`.
Merged N=3: `experiments/validation/c1c2_repair_v2/oracle_n3_merged/summary.json`
(32 C1/C2 + 6 C4 replaced; other 162 rows from the 2026-09-01 200-task ledger).
Merged G2′: `experiments/validation/c1c2_repair_v2/g2prime_merged/summary.json`.

## L1 false start

`python200_hard_20260903_v2_repair` was 185/15 because 15 C1 tasks updated
`TASK.md` without `evaluation/behavior_contract.json` `spec_sha256`.
`scripts/repair_c1_surface.py` and `scripts/repair_c2_entrypoints.py` now call
`_sync_behavior_contract`.

## Not done

HEAD-based freeze cut. Do not reuse
`materialize_python200_hard_frozen_input.py` `BASE_REF=f822ff28`.
