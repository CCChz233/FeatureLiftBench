# Frozen Paper Run Set

Canonical experiment directories for paper analysis. Do not substitute newer runs without updating this file and regenerating `reports/paper_analysis/`.

**Frozen at:** 2026-07-12  
**Execution harness commit:** `e7835b413e877dd96f2b8b6efd6392635365a1fb`  
**Promoted Python-150 snapshot:** `1e805a2`  
**Analysis/harness-fix commit:** `2d3a9ee`  
**Agent:** OpenHands (standard setting)  
**Suite:** Python-150 = core-100 + hard extension-50 (disjoint union)

## Frozen Reporting Protocol

- The current `benchmark/tasks/` inventory contains exactly 150 tasks.
- The four-model leaderboard uses only the shared **core-100**, because all four models ran that exact set.
- The **full Python-150** result is reported for DeepSeek-V4-Flash only, by joining its core-100 run with the three hard-extension waves.
- The hard-extension-50 remains a separate difficulty slice in tables; it is no longer described as outside the main inventory.
- Average final score uses all assigned tasks as the denominator. Failed gates and missing submissions contribute zero.
- Do not compare another model on Python-150 until it has completed the same hard-extension-50.

Frozen Flash full-split result: **91/150 pass (60.7%), average final score 0.359**.

## Shared Core-100 Leaderboard

| Model slug | Run ID | Path | Pass | Avg final score |
| --- | --- | --- | ---: | ---: |
| deepseek-v4-flash | `main-flash-20260705-232429` | `experiments/python/openhands/deepseek-v4-flash/main-flash-20260705-232429` | 83/100 | 0.520 |
| qwen3.6-27b-fp8 | `qwen36-27b-fp8-main-20260704-001328` | `experiments/python/openhands/qwen3.6-27b-fp8/qwen36-27b-fp8-main-20260704-001328` | 54/100 | 0.324 |
| qwen3.6-35b-a3b-fp8 | `qwen36-35b-a3b-fp8-main-20260704-001313` | `experiments/python/openhands/qwen3.6-35b-a3b-fp8/qwen36-35b-a3b-fp8-main-20260704-001313` | 49/100 | 0.303 |
| qwen3-coder-30b-a3b-instruct | `main-20260702-212731` | `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/main-20260702-212731` | 24/100 | 0.173 |

## Hard Extension-50 Flash Calibration

Merged across waves (50 unique tasks now in the Python main inventory; exclude `batch3-flash-20260707-112646` — all missing submissions):

| Wave run ID | Tasks | Passed | Notes |
| --- | ---: | ---: | --- |
| `batch3-flash-20260707-113104` | 10 | 2 | wave1 retry |
| `batch3-flash-20260707-wave2wave4` | 20 | 5 | waves 2–4 |
| `batch3-flash-20260708-wave5` | 20 | 1 | wave 5 |

**Merged unique pass (8/50):**  
`apscheduler__cron_trigger_core__hard3_001`, `build__pyproject_backend_core__hard3_001`, `celery__signal_dispatch_core__hard3_001`, `multidict__multidict_mutation_core__hard3_001`, `sqlalchemy__event_dispatch_core__hard3_001`, `stevedore__extension_manager_core__hard3_001`, `tenacity__retry_state_core__hard3_001`, `tox__factor_expression_core__hard3_001`

Excluded from merged stats: `batch3-flash-20260707-112646` (infra/pilot, 10/10 missing_submission).

Hard-extension result: **8/50 pass (16.0%), average final score 0.037**.

## Gate Evidence (RQ4 / calibration)

| Scope | Path | Count |
| --- | --- | ---: |
| batch1 gate reports | `evidence/python/batch1/*/review/gate_report.json` | 52 |

Includes oracle, naive, copy-all, and Flash calibration metrics for promoted hard3 tasks and original batch1 tasks.

## Regeneration

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/generate_paper_analysis.py
```

Outputs land in `reports/paper_analysis/`.

## Missing Matched Runs

DeepSeek-V4-Flash covers all 150 tasks. Qwen3-Coder still needs the same hard-extension-50 before it can be compared on the full split:

| Profile | Missing tasks | Planned output family |
| --- | ---: | --- |
| `openhands_qwen3_coder_30b_paper` | 50 | `experiments/python/openhands/qwen3-coder-30b-a3b-instruct/` |

## Candidate Matched Runs (not frozen)

Received and indexed on 2026-07-20. These runs are intentionally excluded from frozen paper tables until their protocol metadata is reviewed and this file is explicitly re-frozen.

| Model | Candidate run | Hard50 | Combined Python-150 |
| --- | --- | ---: | ---: |
| qwen3.6-27b-fp8 | `experiments/python/openhands/qwen3.6-27b-fp8/hard50-qwen3.6-27b-fp8-20260720-023500` | 4/50 | 58/150 |
| qwen3.6-35b-a3b-fp8 | `experiments/python/openhands/qwen3.6-35b-a3b-fp8/hard50-qwen3.6-35b-a3b-fp8-20260720-022800` | 3/50 | 52/150 |

The candidate task sets match the frozen Python-150 task set. Their combined averages, using all 150 assigned tasks as denominator, are 0.224684 and 0.210023 respectively. See `experiments/registry/studies/python150-current.json`.

Preview a run without calling an API:

```bash
./harness/scripts/run_python_hard50_paper.sh openhands_qwen3_coder_30b_paper
./harness/scripts/run_python150_paper.sh openhands_qwen3_coder_30b_paper
```

The scripts require an explicit `--execute` argument to start external model calls. Run only after approving transmission of task instructions, public snapshots, and prompts to the configured provider. Server steps: see `RUN.md` §6.1.
