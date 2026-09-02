# FeatureLiftBench harness

> **Status: current · Last verified: 2026-09-02**
> 评测、CLI、agent adapter。不是第三根实验轴。实验入口是
> [`scripts/run_benchmark.sh`](../scripts/run_benchmark.sh)。

## 现在认这些

- 评测核心：`featureliftbench/evaluator.py`、`cli.py`、`catalog.py`、`benchmark_gate.py`、`validate.py`、`docker_eval.py`
- 跑实验：安装后的 `featureliftbench` CLI，或仓库根的 `./scripts/run_benchmark.sh`
- 辅助脚本清单：[scripts/README.md](scripts/README.md)

## 仍挂着、后续会改的方法

实现留在包顶层，**不要为了看起来干净而改 import**。`agent_runner.py` /
`openhands_runner.py` 按这些路径 lazy import；`method/registry.toml` 的
`retired` / `screening` 条目还要能复现旧 run。

- `cgvl/`
- `adaptive_budget_v2.py`
- `td_cognition.py`
- `exec_contract/`
- `test_first_lift/`
- `self_contract/`
- `spec_adversarial/`
- `contract_closure_gate/`
- `pre_submit_contract_audit.py`
- `differential_probe.py`

新主表只用 `--method main`（OpenHands）。不要把上面这些当成当前论文路径。
