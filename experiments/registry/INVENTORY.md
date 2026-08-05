# Experiment Inventory

> **Documentation status: generated · Last verified: 2026-08-04**

Generated from task-local `run.json` and `eval/result.json`; `suite.summary` is not trusted as a primary metric source.

> The composition below is the historical `mixed_snapshot_v1` study. Current Python-200 evidence eligibility is maintained in `docs/STATUS.md`.

## Historical mixed-snapshot Python-150 composition

| Model | Status | Coverage | Pass | Pass rate | Avg final |
| --- | --- | ---: | ---: | ---: | ---: |
| `deepseek-v4-flash` | frozen | 150/150 | 91/150 | 60.7% | 0.358817 |
| `qwen3.6-27b-fp8` | candidate | 150/150 | 58/150 | 38.7% | 0.224684 |
| `qwen3.6-35b-a3b-fp8` | candidate | 150/150 | 52/150 | 34.7% | 0.210023 |
| `qwen3-coder-30b-a3b-instruct` | incomplete | 100/150 | 24/100 | 24.0% | 0.172782 |

## Registered suites

| Run ID | Lifecycle | Category | Scope | Tasks | Evaluated | Pass | Avg final | Quality |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `go-openhands-deepseek-v4-flash-20260705-001` | support | calibration | go-calibration | 3 | 3 | 3 | 0.501318 | absolute_artifact_paths |
| `compliant150-flash-dspark-main-001` | candidate | leaderboard | python150 | 150 | 0 | 84 | 0.417602 | absolute_artifact_paths, missing_eval_results |
| `batch3-flash-20260707-112646` | superseded | leaderboard | hard50-fragment | 10 | 0 | 0 | 0.000000 | absolute_artifact_paths |
| `batch3-flash-20260707-113104` | frozen | leaderboard | hard50-fragment | 10 | 10 | 2 | 0.058741 | absolute_artifact_paths |
| `batch3-flash-20260707-wave2wave4` | frozen | leaderboard | hard50-fragment | 20 | 20 | 5 | 0.031127 | absolute_artifact_paths |
| `batch3-flash-20260708-wave5` | frozen | leaderboard | hard50-fragment | 20 | 19 | 1 | 0.031556 | summary_average_mismatch, absolute_artifact_paths |
| `batch3-pydantic-rerun-20260711` | candidate | leaderboard | hard50-fragment | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `context-compression-64k-local-smoke-20260720-202600` | candidate | leaderboard | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `context-compression-64k-local-smoke-20260720-204055` | candidate | leaderboard | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `context-compression-64k-local-smoke-20260720-204440` | candidate | leaderboard | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `context-compression-64k-smoke-20260720-193557` | candidate | leaderboard | other | 1 | 0 | 0 | 0.000000 | absolute_artifact_paths |
| `main-flash-20260705-232429` | frozen | leaderboard | core100 | 100 | 98 | 83 | 0.519816 | summary_average_mismatch, absolute_artifact_paths |
| `compliant150-gptoss120b-main-002` | candidate | leaderboard | python150 | 150 | 0 | 37 | 0.184544 | absolute_artifact_paths, missing_eval_results |
| `main-20260702-212731` | frozen | leaderboard | core100 | 100 | 100 | 24 | 0.172782 | absolute_artifact_paths |
| `compliant150-qwen122b-main-001` | candidate | leaderboard | python150 | 150 | 0 | 56 | 0.275992 | absolute_artifact_paths, missing_eval_results |
| `hard50-qwen3.6-27b-fp8-20260720-023500` | candidate | leaderboard | hard50 | 50 | 44 | 4 | 0.026916 | ok |
| `qwen36-27b-fp8-main-20260704-001328` | frozen | leaderboard | core100 | 100 | 98 | 54 | 0.323569 | summary_average_mismatch, absolute_artifact_paths |
| `compliant150-qwen35b-main-001` | candidate | leaderboard | python150 | 150 | 0 | 47 | 0.208269 | absolute_artifact_paths, missing_eval_results |
| `hard50-qwen3.6-35b-a3b-fp8-20260720-022800` | candidate | leaderboard | hard50 | 50 | 49 | 3 | 0.024567 | ok |
| `qwen36-35b-a3b-fp8-main-20260704-001313` | frozen | leaderboard | core100 | 100 | 95 | 49 | 0.302750 | summary_average_mismatch, absolute_artifact_paths |
| `cgcc-lite-focus-s1-20260730-codex01` | support | method | other | 2 | 2 | 0 | 0.000000 | absolute_artifact_paths |
| `cgcc-rmc-alembic-s1-20260730-codex01` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `cgcc-roc-focus-s1-20260730-codex01` | support | method | other | 2 | 2 | 0 | 0.000000 | absolute_artifact_paths |
| `main` | support | method | other | 50 | 50 | 11 | 0.120691 | absolute_artifact_paths |
| `nopublic` | support | method | other | 50 | 50 | 4 | 0.045947 | absolute_artifact_paths |
| `clean3` | support | method | other | 6 | 6 | 2 | 0.333333 | absolute_artifact_paths |
| `main` | support | method | other | 6 | 6 | 2 | 0.333333 | absolute_artifact_paths |
| `20260723_bidict_baseline_smoke` | support | method | other | 1 | 1 | 1 | 0.523591 | absolute_artifact_paths |
| `20260723_bidict_rsg_closure_smoke` | support | method | other | 1 | 1 | 1 | 0.523133 | absolute_artifact_paths |
| `isort__settings_resolver_core__hard3_001__p0` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `isort__settings_resolver_core__hard3_001__tuned` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `scrapy__item_loader_core__hard3_001__p0` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `scrapy__item_loader_core__hard3_001__tuned` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `transitions__state_machine_core__hard3_001__p0` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `transitions__state_machine_core__hard3_001__tuned` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `live-api-verify-20260723-210022` | support | method | other | 1 | 1 | 1 | 0.499250 | absolute_artifact_paths |
| `attempt_01` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `attempt_01` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `001_celery_p0_r1` | support | method | other | 1 | 1 | 1 | 0.197007 | absolute_artifact_paths |
| `002_celery_p3_r1` | support | method | other | 1 | 0 | 0 | 0.000000 | absolute_artifact_paths, missing_eval_results |
| `smoke-d0-auto_support-v2-20260723-200929` | support | method | other | 1 | 1 | 1 | 0.499250 | absolute_artifact_paths |
| `smoke-p0-baseline-v2-20260723-200737` | support | method | other | 1 | 1 | 1 | 0.544228 | absolute_artifact_paths |
| `smoke-p2-bidict-v2-20260723-201043` | support | method | other | 1 | 1 | 1 | 0.523591 | absolute_artifact_paths |
| `smoke-p2-tool_only-v2-20260723-200606` | support | method | other | 1 | 1 | 1 | 0.521739 | absolute_artifact_paths |
| `p0-easy` | support | method | other | 1 | 1 | 1 | 0.544228 | absolute_artifact_paths |
| `tuned-efficient-easy` | support | method | other | 1 | 1 | 1 | 0.499250 | absolute_artifact_paths |
| `tuned-hard-transitions` | support | method | other | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `p0` | support | method | other | 1 | 1 | 1 | 0.515742 | absolute_artifact_paths |
| `tuned` | support | method | other | 1 | 1 | 1 | 0.499250 | absolute_artifact_paths |
| `r1-p0` | support | method | other | 1 | 1 | 1 | 0.544228 | absolute_artifact_paths |
| `r1-tuned` | support | method | other | 1 | 1 | 1 | 0.544228 | absolute_artifact_paths |
| `r2-p0` | support | method | other | 1 | 1 | 1 | 0.499250 | absolute_artifact_paths |
| `r2-tuned` | support | method | other | 1 | 1 | 1 | 0.499250 | absolute_artifact_paths |
| `r3-p0` | support | method | other | 1 | 1 | 1 | 0.499250 | absolute_artifact_paths |
| `r3-tuned` | support | method | other | 1 | 1 | 1 | 0.544228 | absolute_artifact_paths |
| `dev6_20260731` | support | method | other | 6 | 6 | 1 | 0.166667 | absolute_artifact_paths |
| `dev6_tfl_p0_20260731` | support | method | other | 6 | 5 | 1 | 0.166667 | absolute_artifact_paths |
| `smoke_returns_20260731` | support | method | other | 1 | 0 | 0 | 0.000000 | absolute_artifact_paths |
| `smoke_returns_20260731b` | support | method | other | 1 | 1 | 1 | 1.000000 | absolute_artifact_paths |
| `batch2` | support | smoke | smoke | 2 | 2 | 1 | 0.233201 | absolute_artifact_paths |
| `sanity3` | support | smoke | smoke | 3 | 3 | 3 | 0.753134 | absolute_artifact_paths |
| `batch2` | support | smoke | smoke | 2 | 2 | 0 | 0.000000 | absolute_artifact_paths |
| `sanity3` | support | smoke | smoke | 3 | 3 | 3 | 0.726951 | absolute_artifact_paths |
| `pilot-5-20260701-161103` | support | smoke | smoke | 2 | 2 | 1 | 0.233658 | absolute_artifact_paths |
| `sanity-pilot-20260701-151923` | support | smoke | smoke | 3 | 3 | 0 | 0.000000 | absolute_artifact_paths |
| `workers2-sanity-20260701-162415` | support | smoke | smoke | 3 | 3 | 0 | 0.000000 | absolute_artifact_paths |
| `batch3-flash-20260707-wave2wave4` | support | validation | infra-reevaluation | 2 | 2 | 0 | 0.000000 | absolute_artifact_paths |
| `main-20260702-212731` | support | validation | infra-reevaluation | 21 | 21 | 2 | 0.074430 | absolute_artifact_paths |
| `qwen36-27b-fp8-main-20260704-001328` | support | validation | infra-reevaluation | 21 | 21 | 14 | 0.374977 | absolute_artifact_paths |
| `qwen36-35b-a3b-fp8-main-20260704-001313` | support | validation | infra-reevaluation | 18 | 18 | 9 | 0.333297 | absolute_artifact_paths |
