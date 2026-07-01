# OpenHands 服务器运行指南

本文档是服务器上用 **OpenHands 测评 FeatureLiftBench** 的操作手册。
当前口径：OpenHands 是主测 agent；`featurelift-agent` 只作为协议/上下文审计对照。

最后更新：2026-07-01

## 0. 运行原则

- 先跑 `preflight`，再跑 1 题 smoke，再跑 `pilot5`，最后才考虑更大切片。
- 默认启用 agent Docker 和 eval Docker，不在服务器宿主环境直接跑 agent/eval。
- 初始 `NUM_WORKERS=1`；确认 5-10 题稳定后再讨论并发。
- OpenHands 会把任务 prompt、可见 repo/public tests 发送给所选模型 API。不要在未接受该外发风险时跑真实 API。
- OpenHands 结果只有在 `usage.context_audit.usage_unverified == false` 时，才能作为正式 token/context 证据；否则只能标 pilot。

## 1. 拉代码与基础环境

推荐用 git 在服务器拉取代码，不要把本机 `.env` 提交进仓库。

```bash
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench

PYTHON=python3.12 ./setup.sh
source .venv/bin/activate
export PYTHONPATH=$PWD/harness
```

如果服务器没有 Python 3.12：

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-pip
```

## 2. 配置 `.env`

OpenHands DeepSeek profile 默认读 `FEATURELIFTBENCH_API_KEY` 和
`FEATURELIFTBENCH_API_BASE`。

```bash
cp .env.example .env 2>/dev/null || touch .env
nano .env
```

最小配置：

```bash
FEATURELIFTBENCH_API_KEY=sk-...
FEATURELIFTBENCH_API_BASE=https://api.deepseek.com/v1
```

说明：

- 当前 harness 只会把所选 profile 的 key/base 和必要 `FEATURELIFTBENCH_*` 配置透传给 agent Docker。
- 不同平台的 key 可以保留在 `.env`，但 OpenHands DeepSeek profile 不会再把无关的 `SILICONFLOW_API_KEY` 传进容器。
- 不要把 `.env` 加入 git。

## 3. 构建 Docker 镜像

OpenHands 需要 Python 3.12+ 的 agent 镜像，并安装 OpenHands CLI。

```bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest

./docker/build_eval_image.sh featureliftbench-eval:latest
```

必要时先确认 Docker 可用：

```bash
docker info
docker images | grep featureliftbench
```

## 4. 预检

每次服务器开跑前先跑：

```bash
PYTHONPATH=harness python harness/scripts/preflight.py \
  --bootstrap \
  --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash \
  --docker-suite \
  --output-dir experiments/openhands-agent/preflight-$(date +%Y%m%d-%H%M%S)
```

通过时应看到：

```text
preflight: docker ok images=featureliftbench-agent:latest,featureliftbench-eval:latest
preflight: ok agent=openhands-agent profile=openhands_deepseek_v4_flash ...
```

如果提示 `openhands CLI not found`，重新构建 agent 镜像，并确认使用了
`FEATURELIFTBENCH_INSTALL_OPENHANDS=1` 和 Python 3.12 base image。

## 5. 先跑 1 题 smoke

建议在 `tmux` 里跑，避免 SSH 断开中断进程。

```bash
tmux new -s flb-openhands-smoke

FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
NO_PROGRESS=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
./run_openhands.sh benchmark/sanity/iniconfig__parse_config__001 \
  experiments/openhands-agent/smoke-iniconfig-$(date +%Y%m%d-%H%M%S)
```

验收：

```bash
OUT=experiments/openhands-agent/<smoke-run>
python -m json.tool "$OUT/run.json" >/dev/null
python -m json.tool "$OUT/agent/usage.json" >/dev/null
test -f "$OUT/agent/openhands_task.md"
test -f "$OUT/agent/openhands_events.jsonl" || true
test -f "$OUT/agent/context_audit.jsonl" || true
```

重点检查：

- `run.json` 里 `agent_backend == "docker"`。
- `run.json` 里 `eval_backend == "docker"`。
- `evaluation.docker_sandbox_error` 应为 `false`；否则这是基础设施失败，先不要扩大规模。
- `agent/usage.json.exit_status` 不应是 `log_limit_exceeded`。
- 若 provider 返回 usage，`agent/usage.json.context_audit.usage_unverified` 应为 `false`。

## 6. 跑 pilot5

`pilot5` 固定为 3 个 sanity task + 2 个 batch task。脚本会写两个子 suite，避免互相覆盖：

```text
experiments/openhands-agent/<RUN_ID>/
  sanity3/
    suite.json
  batch2/
    suite.json
  pilot5-summary.json
  pilot5-summary.md
```

运行：

```bash
tmux new -s flb-openhands-pilot5

FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
NO_PROGRESS=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
RUN_ID=openhands-pilot5-$(date +%Y%m%d-%H%M%S) \
./run_openhands_pilot5.sh
```

如果中断，用同一个 `RUN_ID` 续跑：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
NO_PROGRESS=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
RUN_ID=<same-run-id> \
RESUME=1 \
./run_openhands_pilot5.sh
```

验收：

```bash
OUT=experiments/openhands-agent/<RUN_ID>
python -m json.tool "$OUT/pilot5-summary.json" >/dev/null
grep -n "Total: 5" "$OUT/pilot5-summary.md"
```

`pilot5-summary.json.summary` 中应重点看：

- `total == 5`
- `agent_failures == 0`
- `docker_sandbox_failures == 0`
- `log_limit_failures == 0`

如果这四项不满足，先查失败题，不要扩大到 50/100 题。

## 7. 固定 5-10 题小切片

pilot5 通过后，再用明确 task id 跑 5-10 题。示例：

```bash
OUT=experiments/openhands-agent/slice10-$(date +%Y%m%d-%H%M%S)

PYTHONPATH=harness python -B -m featureliftbench.cli run-agent benchmark/tasks \
  --agent openhands-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile openhands_deepseek_v4_flash \
  --env-file .env \
  --agent-docker \
  --eval-docker \
  --num-workers 1 \
  --output "$OUT" \
  --task-id arrow__parse_format_core__001 \
  --task-id bleach__sanitize_core__001
```

继续追加 task id 即可。不要用随机抽样替代固定切片；固定切片才便于复现和对比。

## 8. 正式大跑

只有在 1 题 smoke、pilot5、固定小切片都满足验收后，才跑主榜。

```bash
tmux new -s flb-openhands-main

OUT=experiments/openhands-agent/main-$(date +%Y%m%d-%H%M%S)

FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
NO_PROGRESS=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=1 \
./run_openhands.sh benchmark/tasks "$OUT"
```

续跑：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
NO_PROGRESS=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash \
RESUME_DIR=experiments/openhands-agent/<main-run-id> \
./run_openhands.sh benchmark/tasks
```

说明：

- `run_openhands.sh` 会在输出目录加 `.run.lock`，同一目录不要开第二个 runner。
- `run-agent` 返回 1 代表 benchmark 有失败题，不等于基础设施失败；返回 2 或更高才按 harness/配置失败处理。
- 正式论文口径不要混用 `usage_unverified=true` 的结果来证明长上下文能力。

## 9. 结果文件

每题关键文件：

```text
<OUT>/<task_id>/
  run.json
  agent/usage.json
  agent/context_audit.jsonl
  agent/openhands_events.jsonl
  agent/openhands_stdout.log
  agent/openhands_stderr.log
  eval/result.json
```

Suite 级关键文件：

```text
<OUT>/suite.json
<OUT>/suite-comparison.json
<OUT>/benchmark-analysis.md
<OUT>/entanglement-coverage.md
```

快速检查：

```bash
OUT=experiments/openhands-agent/<run-id>
python harness/scripts/analyze_benchmark_suite.py "$OUT"
python harness/scripts/report_entanglement_coverage.py --suite-dir "$OUT"
```

## 10. 资源与限制

默认推荐：

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_MEMORY=8g
export FEATURELIFTBENCH_AGENT_DOCKER_CPUS=2
export FEATURELIFTBENCH_AGENT_DOCKER_PIDS=512
export FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS=600
export FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES=8388608
```

说明：

- `FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES` 同时保护 wrapper 日志和 Docker 外层日志；OpenHands 输出超限会被终止并归类为 `log_limit_exceeded`。
- Eval Docker 默认禁网，agent Docker 默认可联网访问模型 API。
- OpenHands usage proxy 默认启用。如需临时关闭：

```bash
export FEATURELIFTBENCH_OPENHANDS_USAGE_PROXY=0
```

关闭后若 OpenHands JSONL 本身没有 usage 字段，结果会保持 `usage_unverified=true`。

## 11. 常见问题

**完整踩坑记录（vLLM 网络、tool calling、DeepSeek 模型名、GitHub clone 等）** → [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md)

| 现象 | 处理 |
| --- | --- |
| `openhands CLI not found` | 用 Python 3.12 base 重建 agent 镜像，并设置 `FEATURELIFTBENCH_INSTALL_OPENHANDS=1` |
| `docker_sandbox_error=true` | 先看 `eval/result.json` 和 Docker 超时/OOM；这是基础设施失败，不应计入模型功能结论 |
| `log_limit_exceeded` | 降低 OpenHands 噪声、提高 `FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES`，或保留为日志超限失败 |
| `usage_unverified=true` | provider 未返回 usage，或 proxy 被关闭；该 run 只能标 pilot |
| 全题 `missing_submission` | 先查 `api_calls` 是否为 0；见 [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md) §5 排障表 |
| `.run.lock` 阻止开跑 | 确认没有旧进程；崩溃残留才执行 `rmdir <OUT>/.run.lock` |

## 12. 最小安全检查清单

开跑前：

- [ ] `.env` 只放需要的 API key/base，不进 git。
- [ ] `preflight.py --docker-suite` 通过。
- [ ] agent image 是 Python 3.12 + OpenHands 版本。
- [ ] eval image 已构建。
- [ ] `NUM_WORKERS=1`。

扩大规模前：

- [ ] 1 题 smoke 无 `docker_sandbox_error`。
- [ ] pilot5 `total == 5`。
- [ ] pilot5 `agent_failures == 0`。
- [ ] pilot5 `docker_sandbox_failures == 0`。
- [ ] pilot5 `log_limit_failures == 0`。
- [ ] 每题有 `agent/usage.json`。
- [ ] token/context 证据已明确：verified 或标 `usage_unverified=true`。
