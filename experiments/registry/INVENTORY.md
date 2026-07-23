# Experiment Inventory

Generated from task-local `run.json` and `eval/result.json`; `suite.summary` is not trusted as a primary metric source.

## Python-150 composition

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
| `batch3-flash-20260707-112646` | superseded | leaderboard | hard50-fragment | 10 | 0 | 0 | 0.000000 | absolute_artifact_paths |
| `batch3-flash-20260707-113104` | frozen | leaderboard | hard50-fragment | 10 | 10 | 2 | 0.058741 | absolute_artifact_paths |
| `batch3-flash-20260707-wave2wave4` | frozen | leaderboard | hard50-fragment | 20 | 20 | 5 | 0.031127 | absolute_artifact_paths |
| `batch3-flash-20260708-wave5` | frozen | leaderboard | hard50-fragment | 20 | 19 | 1 | 0.031556 | summary_average_mismatch, absolute_artifact_paths |
| `batch3-pydantic-rerun-20260711` | candidate | leaderboard | hard50-fragment | 1 | 1 | 0 | 0.000000 | absolute_artifact_paths |
| `main-flash-20260705-232429` | frozen | leaderboard | core100 | 100 | 98 | 83 | 0.519816 | summary_average_mismatch, absolute_artifact_paths |
| `main-20260702-212731` | frozen | leaderboard | core100 | 100 | 100 | 24 | 0.172782 | absolute_artifact_paths |
| `hard50-qwen3.6-27b-fp8-20260720-023500` | candidate | leaderboard | hard50 | 50 | 44 | 4 | 0.026916 | ok |
| `qwen36-27b-fp8-main-20260704-001328` | frozen | leaderboard | core100 | 100 | 98 | 54 | 0.323569 | summary_average_mismatch, absolute_artifact_paths |
| `hard50-qwen3.6-35b-a3b-fp8-20260720-022800` | candidate | leaderboard | hard50 | 50 | 49 | 3 | 0.024567 | ok |
| `qwen36-35b-a3b-fp8-main-20260704-001313` | frozen | leaderboard | core100 | 100 | 95 | 49 | 0.302750 | summary_average_mismatch, absolute_artifact_paths |
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
