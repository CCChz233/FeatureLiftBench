# harness/scripts

> **Status: current · Last verified: 2026-09-02**

跑新实验用 [`../../scripts/run_benchmark.sh`](../../scripts/run_benchmark.sh)，
不要用本目录里的旧 paper runner。

## 当前

| Script | Role |
| --- | --- |
| `verify_all_oracles.py` | CI oracle smoke |
| `verify_module_probes.py` | Isolation probes |
| `preflight.py` / `preflight.sh` | Suite preflight |
| `list_tasks.py` | List / filter tasks |
| `summarize_experiment_runs.py` | Summarize runs |
| `reeval_suite.py` | Re-evaluate a suite |
| `analyze_python200_hard_main.py` | Paper-suite analysis |
| `analyze_failure_taxonomy.py` | Failure labels |
| `analyze_agent_failure_process.py` | Process-level failure |
| `audit_contract_entailment.py` | Gate C1/C2 |
| `audit_source_entrypoints.py` | Gate C2 entrypoints |
| `generate_gate_report.py` | Oracle G1–G4 report |
| `generate_paper_analysis.py` | Paper analysis helper |
| `build_oracle_submission.py` | Oracle submissions |
| `merge_python200_main_results.py` | Merge shards |
| `run_runtime_ablation.sh` | DeepSeek Harness / Codex |
| `server_setup.sh` / `pin_runtime_agents.sh` | Server / runtime pins |
| `run_go_openhands.sh` / `preflight_go_*` / `go_copy_naive_agent.py` | Go calibration |
| `analyze_token_utility_*.py` | RQ3/RQ5 offline gold |

## Archive

[archive/](archive/README.md)：出题脚手架、Kill 方法比较脚本、**旧套件 paper runner**
（`run_python200_paper.sh` 等）以及会和正式入口撞名的 `run_benchmark.sh`
（mini-swe）。
