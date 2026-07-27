# FeatureLiftBench 运行速查

正式服务器流程见
[docs/SERVER_RUNBOOK_PYTHON150.md](docs/SERVER_RUNBOOK_PYTHON150.md)。
本页只保留当前命令，不再收录旧 batch、mini-swe-agent 和 v1 迁移复现步骤。

## 1. Setup

```bash
PYTHON=python3.12 SKIP_MINI=1 ./setup.sh
cp harness/config/agents.example.toml harness/config/agents.toml
```

在 `.env` 配置 profile 所需的 API key/base URL。不要提交 `.env`。

构建镜像：

```bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
  docker/build_agent_image.sh featureliftbench-agent:latest

docker/build_eval_image.sh featureliftbench-eval:latest
```

## 2. Materialize and verify v3

```bash
python3 scripts/materialize_full_sources.py --workers 8
python3 scripts/materialize_full_sources.py --check
python3 scripts/build_source_registry.py --check
python3 scripts/build_pruned_source_registry.py --check
python3 scripts/check_task_lifecycle.py
python3 scripts/build_v3_benchmark_freeze.py --check
python3 scripts/audit_v3_main_readiness.py --strict
```

Expected:

```text
150/150 v3-ready
132/132 source snapshots ready
450/450 Docker Oracle, 0 unstable
12/12 adversarial canaries
active freeze: artifacts/research_analysis/v3/current_benchmark_freeze.json
```

若 source/spec/reference/evaluator/environment 有任何变化，必须重建并重新
验收 freeze，不能沿用上述 ID。

## 3. Validate one task

```bash
PYTHONPATH=harness .venv/bin/python -B -m featureliftbench.cli \
  validate-task benchmark/tasks/arrow__parse_format_core__001
```

重新生成 `TASK.md`：

```bash
PYTHONPATH=harness .venv/bin/python -B -m featureliftbench.cli \
  render-task benchmark/tasks/<task_id> --write
```

## 4. Evaluate an existing submission

Local:

```bash
PYTHONPATH=harness .venv/bin/python -B -m featureliftbench.cli eval \
  benchmark/tasks/<task_id> \
  <submission_dir> \
  --output <result_dir>
```

正式结果应使用 evaluator Docker；具体参数见 CLI help 和服务器 runbook。

## 5. Run one OpenHands smoke

```bash
export FEATURELIFTBENCH_MOUNT_PUBLIC_TESTS=0
export FEATURELIFTBENCH_PROMPT_STYLE=standard
export FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120

PYTHONPATH=harness .venv/bin/python -B -m featureliftbench.cli run-agent \
  benchmark/tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile openhands_deepseek_v4_flash \
  --agent-command "openhands --headless --override-with-envs --exit-without-confirmation -f {prompt_file} --json" \
  --no-agent-public-tests \
  --no-agent-source-hints \
  --prompt-style standard \
  --source-context full_repository \
  --env-file .env \
  --num-workers 1 \
  --timeout-seconds 3600 \
  --extra-agent-passes 0 \
  --max-task-attempts 1 \
  --retry-rate-limit 5 \
  --agent-docker \
  --agent-docker-image featureliftbench-agent:latest \
  --eval-docker \
  --eval-docker-image featureliftbench-eval:latest \
  --task-id arrow__parse_format_core__001 \
  --output experiments/smoke/v3-openhands-main
```

Smoke 必须记录：

- agent/eval backend 均为 Docker；
- arm=`main`；
- public/hidden tests 未挂载；
- source hints 未暴露；
- source scope 为 `full_tracked_tree`；
- benchmark freeze 匹配 active v3 freeze；
- `eval/result.json` 存在，并记录 public/hidden/isolation 三个显式门、
  `evaluation_capsule_digest` 和 `compactness_status=ok`。

## 6. Run Python-150

Plan only，不调用模型：

```bash
./harness/scripts/run_python150_paper.sh \
  <openhands-profile> \
  <run-id>
```

确认 model、150 tasks、Full-Repository / No-Hint Main、agent/eval images、
attempt=1 和 active freeze 后执行：

```bash
./harness/scripts/run_python150_paper.sh \
  <openhands-profile> \
  <run-id> \
  --workers 1 \
  --execute
```

Resume：

```bash
./harness/scripts/run_python150_paper.sh \
  <openhands-profile> \
  --resume experiments/python/openhands/<model-slug>/<run-id> \
  --workers 1 \
  --execute
```

Resume 只补没有终态 `run.json` 的任务；已有失败不会重试，因此仍是严格
Pass@1。

## 7. Monitor and analyze

```bash
bash harness/scripts/check_run_health.sh \
  experiments/python/openhands/<model-slug>/<run-id>

PYTHONPATH=harness .venv/bin/python \
  harness/scripts/analyze_benchmark_suite.py <suite-dir>

PYTHONPATH=harness .venv/bin/python \
  harness/scripts/report_entanglement_coverage.py --suite-dir <suite-dir>
```

重要文件：

```text
<suite>/suite.json
<suite>/<task_id>/run.json
<suite>/<task_id>/agent/
<suite>/<task_id>/submission/
<suite>/<task_id>/eval/result.json
```

Headline 从 evaluator `functional_gate` 计算，不从 OpenHands
`run.status` 计算。

## 8. Run explicit ablations

```bash
./run_experiment.sh --help

./run_experiment.sh \
  --compare-arms main,entrypoint_hint,public_feedback,pruned_context \
  --tasks <task_id>
```

消融必须保持 task/spec/model/agent/evaluator/environment 一致，只改变臂定义
的变量。详见 [docs/EXPERIMENT_ARMS.md](docs/EXPERIMENT_ARMS.md)。

## 9. Safety defaults

Evaluator Docker：

```text
network: none
memory: 4 GiB
cpus: 2
pids: 256
root fs: read-only
```

Agent Docker：

```text
agent network: Docker bridge by default (host mode for a local API endpoint)
evaluator network: none
memory: 8 GiB
cpus: 2
pids: 512
mounted: prepared workspace rw, agent output rw, harness ro
not mounted: benchmark root, evaluator tests, host home, .env, Docker socket
```

不要对同一个 output directory 启动两个 runner，也不要为不同模型、arm 或
freeze 复用同一个 run ID。
