# FeatureLiftBench 运行速查

> **Status: current · Last verified: 2026-08-29**
> 完整服务器流程见 [Python-200 runbook](docs/SERVER_RUNBOOK_PYTHON200.md)，
> 当前 release 事实见 [STATUS.md](docs/STATUS.md)。
> 实验轴是 **benchmark × agent × method**（`--arm` 是 `--method` 的别名）。

只认两个启动方式：`./scripts/run_benchmark.sh` 与安装后的 `featureliftbench` CLI。
根目录 `run_benchmark.sh` / `run_experiment.sh` 是薄转发。其它根目录 `run_*.sh`
已弃用，见 [scripts/README.md](scripts/README.md)。

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./harness
cp harness/config/agents.example.toml harness/config/agents.toml
```

或 `./setup.sh`：会写出 `agents.toml`，并安装 pinned DeepSeek Harness / Codex CLI
（与 OpenHands 同级）。OpenHands host CLI 仍用 `INSTALL_OPENHANDS=1`。

评测与 catalog 在 macOS 上用 **python3.12**（系统 python3 可能是 3.9）。
配置 `.env` 和 `harness/config/agents.toml`，不要提交凭据。

## 论文主套件（Python-200'）

冻结 Python-150 + Hard-50。**整套 Flash 未出分。** 不要用
`./harness/scripts/run_python200_paper.sh`（仍指向已 superseded 的 150+External-50）。

```bash
./scripts/run_benchmark.sh \
  --benchmark python200_hard \
  --agent openhands \
  --method main \
  --output experiments/python/openhands/<model>/<run-id> \
  --docker --workers 1 --timeout 3600
```

V1（Main + 2M cap）只改 `--method v1`。DeepSeek Harness / Codex 只改 `--agent`，
数字不进 OpenHands 主表。

列出已注册的 suite / agent / method：

```bash
PYTHONPATH=harness python3.12 -B -m featureliftbench.cli catalog list
PYTHONPATH=harness python3.12 -B -m featureliftbench.cli catalog check
```

`--arm` 等于 `--method`。`./harness/scripts/run_python200_paper.sh` 仍会跑旧
150 freeze check，不能用来写新主表。

## 无模型调用的套件检查

Python-200' 视图与 150 freeze（freeze 只约束 150，不把 Hard-50 写进 `tasks/`）：

```bash
python3.12 benchmark/selection/scripts/materialize_python200_hard_release.py --check
python3.12 benchmark/selection/scripts/check_python200_baseline_freeze.py
PYTHONPATH=harness python3.12 -B -m featureliftbench.cli catalog check
```

旧 150+External-50 的 plan-only（历史套件，不是新主表）：

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  python200-plan
```

## Resume

```bash
./scripts/run_benchmark.sh \
  --benchmark python200_hard \
  --agent openhands \
  --method main \
  --resume experiments/python/openhands/<model>/<run-id> \
  --docker --workers 1
```

Resume 只能补没有 terminal `run.json` 的题，不得把已完成失败重跑后仍称 Pass@1。

## Analyze

```bash
PYTHONPATH=harness python3.12 harness/scripts/analyze_benchmark_suite.py \
  experiments/python/openhands/<model>/<run-id>

PYTHONPATH=harness python3.12 harness/scripts/report_entanglement_coverage.py \
  --suite-dir experiments/python/openhands/<model>/<run-id>
```

主结果读取逐题 `run.json -> evaluation.scores.functional_gate`，并与
`eval/result.json` 交叉检查；`suite.summary` 只是可重建缓存。

跨模型合并表
`artifacts/research_analysis/current_results/python200_cross_model_main_20260818.json`
是 **已 superseded 的 150+External-50**，不是 Python-200' 主表。重建命令：

```bash
PYTHONPATH=harness python3.12 harness/scripts/merge_python200_main_results.py
```

Runtime ablation 输出在
`experiments/python/runtime/<adapter>/<model>/<run-id>/`，用同一分析脚本，
不要并入 OpenHands 主表。

## 历史套件（150 + External-50）

仅复现旧分数或旧 V1。正式条件见当时的 `run_python200_paper.sh` 记录。
当前 cost arm 规范见 [METHOD_V1.md](docs/METHOD_V1.md)。Qwen V1-200 **55/200**
落在该旧套件上，不要写成 200' 通过率。

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  <run-id> \
  --workers <n> \
  --agent-image <pinned-agent-image> \
  --eval-image <pinned-eval-image> \
  --execute
```

只跑 External-50 时加 `--external-only`，且必须已有同条件冻结 baseline。
不要再开 `contract_closure_gate_lite_v1*` 作为正式 V1。

可选 runtime ablation（Core-12 包装，不是 Official Main）：

```bash
./harness/scripts/run_runtime_ablation.sh deepseek-harness dsh_deepseek_v4_flash_main
```

见 [METHOD_AGENT_RUNTIME.md](docs/METHOD_AGENT_RUNTIME.md)。

## Task Maintenance

```bash
PYTHONPATH=harness python3.12 -B -m featureliftbench.cli validate-task \
  benchmark/staging/<task-id> --json
```

任务创建、验证与 promotion 分别遵循仓库内 FeatureLiftBench skills 和
[Task Design Rules](docs/TASK_DESIGN_RULES.md)。Hard-50 不得写入 `benchmark/tasks/`。
