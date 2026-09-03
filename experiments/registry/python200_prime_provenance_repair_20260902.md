# Python-200′ provenance repair — 2026-09-02

> **Status: complete · Scope: provenance records and the materialized run input
> only. No frozen task package, `metadata.json`, Hidden test, or published
> result was modified.**

## Problem

Four identity records disagreed, and the disagreement blocked every attempt to
produce a verifiable run input for Python-200′:

| Record | Was | Reality |
| --- | --- | --- |
| `python200_hard_suite.json.baseline_freeze_id` | `846b8147…` | `0b106842…` |
| `check_python200_baseline_freeze.py::EXPECTED_FREEZE_ID` | `846b8147…` | `0b106842…` |
| `materialize_python200_hard_release.py::FREEZE_ID` | `846b8147…` | `0b106842…` |
| `STATUS.md` Hard-50 release tree | `6b1cac75…` | `61c61ee5…` |
| `materialize_python200_hard_frozen_input.py::BASE_REF` | `8438e3a3` (pre-hardening) | `f822ff28` |

`materialize_python200_hard_frozen_input.py --check` failed with
`Python-200′ selection and active freeze IDs disagree` and could not run at all.

## Root cause

On 2026-09-01 a contract-hardening pass rewrote 48 of the 150 baseline task
packages, adding the members that Hidden already exercised into `required_api`
plus the matching `assert callable(...)` lines in
`hidden_tests/test_required_api_surface.py`. This is the R-SURFACE fix pattern.

The hardening was committed (`f429806f`, then `f822ff28`) and captured in two
freeze artifacts:

- `474862c2…` — Python-200′ active freeze (2026-09-01T00:12:16Z)
- `0b106842…` — Python-150 stratum projection (2026-09-01T00:45:10Z),
  `compatibility_source.projection_only = true`

The surrounding provenance records were never updated, so they kept naming the
pre-hardening ancestor `846b8147…` (2026-07-28).

## Evidence

Measured on 2026-09-02, all against the on-disk assets:

| Claim | Measurement |
| --- | --- |
| `benchmark/tasks` vs `0b106842…` | **150/150 clean**, 0 field failures |
| `benchmark/tasks` vs `846b8147…` | 102/150 clean, 136 field failures |
| `benchmark/python200_hard_tasks` `spec_hash` vs `474862c2…` | **200/200 match** |
| `tree_digest(benchmark/hard50)` | `61c61ee5…` (= suite JSON, ≠ `STATUS.md`) |
| `git archive f822ff28 benchmark/tasks` vs `0b106842…` `task_tree` | **150/150 match** |
| `git archive f429806f …` | 63/150 mismatch (hardening not yet complete) |
| `freeze846-input` `spec_hash` vs `474862c2…` | 156 match / **44 mismatch** |

The 44-task drift explains the observed
`active benchmark freeze spec hash mismatch` failures: `distlib`, `fs` and
`fsspec` in the 2026-09-02 run, and the 17 baseline tasks blocked before launch
in the 2026-08-29 received package.

## Changes

Records only:

- `benchmark/selection/python200_hard_suite.json` — `baseline_freeze_id`
- `benchmark/selection/scripts/check_python200_baseline_freeze.py` — `EXPECTED_FREEZE_ID`
- `benchmark/selection/scripts/materialize_python200_hard_release.py` — `FREEZE_ID`
- `harness/scripts/materialize_python200_hard_frozen_input.py` — `BASE_REF`,
  `DEFAULT_OUTPUT`
- `docs/STATUS.md`, `benchmark/README.md` — freeze identities, ancestor recorded
- `experiments/validation/preflight/python200-hard-freeze846-input/SUPERSEDED.md`

Deliberately left alone as historical records of a different suite or of runs
already executed: `benchmark/contract_v2/suite.json` (old 150+E50 suite),
`benchmark/selection/python200_suite.json`, `reports/paper_analysis/**`,
`experiments/registry/*_20260829*.md`, `experiments/registry/*_20260830.md`,
`artifacts/research_analysis/v3/freezes/846b8147….json`,
`scripts/archive/`, `docs/archive/`.

## Verification after repair

```
check_python200_baseline_freeze.py        -> Python-150 baseline freeze: 150/150 unchanged
materialize_python200_hard_release.py --check -> 150 frozen + 50 hard; digest=61c61ee521c3
materialize_python200_hard_frozen_input.py    -> 200 tasks, freeze 0b106842…, task_set a28c301e…
```

New verifiable run input:
`experiments/validation/preflight/python200-hard-hardened-input/`

| Tree | `spec_hash` vs `474862c2…` |
| --- | --- |
| `python200-hard-hardened-input` | **200 / 0** |
| `python200-hard-freeze846-input` | 156 / 44 (superseded) |
| `benchmark/python200_hard_tasks` | 200 / 0 |

`materialized_tree` sha256 `a8f441c6df7b94c1b1cc025ab408f9198a6f540314ca292c3f938c359789968d`,
13075 files.

## Consequence for existing results

Every Flash run to date used the pre-hardening tree. The 2026-08-29 received
package, the 20260830 38/84 and the 20260902 32/84 all evaluate a weaker
contract on 44 of the 200 tasks and must be reported against ancestor
`846b8147…`. They are not comparable with runs on the hardened tree, and this
is independent of the separate agent/eval image-digest mismatch.
