# FeatureLiftBench 运行速查

> **Status: current · Last verified: 2026-08-18**
> 完整服务器流程见 [Python-200 runbook](docs/SERVER_RUNBOOK_PYTHON200.md)，
> 当前 release 事实见 [STATUS.md](docs/STATUS.md)。

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./harness
cp harness/config/agents.example.toml harness/config/agents.toml
```

配置 `.env` 和 `harness/config/agents.toml`，不要提交凭据。

## Validate Without Model Calls

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  python200-plan
```

该命令检查 release materialization、source/dependency closure、balance、
Python 3.11 wheels、冻结 Python baseline 和全部 runnable task。

## Run Python-200

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  <run-id> \
  --workers <n> \
  --agent-image <pinned-agent-image> \
  --eval-image <pinned-eval-image> \
  --execute
```

正式实验必须固定镜像 identity，不使用未记录 digest 的浮动 `latest` 作为论文条件。

## Run V1 (Main + 2M cap)

当前 cost arm 规范见 [METHOD_V1.md](docs/METHOD_V1.md)。

DeepSeek API：

```bash
./logs/run_python200_v1_deepseek_flash.sh
```

Qwen3.6-35B 本机四路（`:8030`–`:8033`，各 50 题，自动合并）：

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host
./logs/start_python200_v1_qwen35b_4shard_tmux.sh
```

不要再开 `contract_closure_gate_lite_v1*` 作为正式 V1。

## Run Only External-50

已有同模型、同协议、同镜像的完整冻结 baseline 时，可以只运行扩展集：

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  <run-id> \
  --external-only \
  --workers <n> \
  --agent-image <pinned-agent-image> \
  --eval-image <pinned-eval-image> \
  --execute
```

旧 baseline 与新 extension 分开保存，分析阶段按 task ID 合并；不得覆盖或重试
旧失败样本后仍称 Pass@1。

## Resume

```bash
./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  --resume experiments/python/openhands/<model>/<run-id> \
  --workers <n> \
  --execute
```

External-only suite 恢复时继续传入 `--external-only`。

## Analyze

```bash
PYTHONPATH=harness python3 harness/scripts/analyze_benchmark_suite.py \
  experiments/python/openhands/<model>/<run-id>

PYTHONPATH=harness python3 harness/scripts/report_entanglement_coverage.py \
  --suite-dir experiments/python/openhands/<model>/<run-id>
```

主结果读取逐题 `run.json -> evaluation.scores.functional_gate`，并与
`eval/result.json` 交叉检查；`suite.summary` 只是可重建缓存。
`--aggregate` 是跨 suite 的均值/方差，不是 200 题并集。

跨模型 Python-200 Main（冻结 150 + External-50 按题号合并）：

```bash
PYTHONPATH=harness python3 harness/scripts/merge_python200_main_results.py
```

输出：
`artifacts/research_analysis/current_results/python200_cross_model_main_20260818.{json,md}`。
这不是当前 V1。

## Task Maintenance

```bash
PYTHONPATH=harness python3 -B -m featureliftbench.cli validate-task \
  benchmark/staging/<task-id> --json
```

任务创建、验证与 promotion 分别遵循仓库内 FeatureLiftBench skills 和
[Task Design Rules](docs/TASK_DESIGN_RULES.md)。
