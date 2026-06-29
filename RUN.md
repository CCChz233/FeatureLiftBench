# FeatureLiftBench 实验运行速查

服务器部署清单见 [docs/SERVER_DEPLOY.md](docs/SERVER_DEPLOY.md)。

当前正式实验口径：**Agent 用可选 Docker 边界跑题，Eval 默认用独立 Docker 容器评分**。Docker 的目的不是维护 100 套环境，而是限制 submission/eval 的内存、进程数、日志和网络，并防止 agent 改到宿主 benchmark 仓库或读取 hidden tests。

## 0. 一次性准备

```bash
cd /path/to/FeatureLiftBench
./setup.sh
nano .env

docker/build_agent_image.sh featureliftbench-agent:latest
docker/build_eval_image.sh featureliftbench-eval:latest
```

`.env` 至少要有你使用的 profile 对应 API key/base URL。Docker build 默认使用 `python:3.11-slim`；如必须改 base image：

```bash
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim docker/build_agent_image.sh
FEATURELIFTBENCH_EVAL_PYTHON_BASE=python:3.12-slim docker/build_eval_image.sh
```

## 1. 先跑单题 smoke

先用 1 道题确认 agent Docker + eval Docker 串起来没问题：

```bash
PYTHONPATH=harness .venv/bin/python -B -m featureliftbench.cli run-agent \
  benchmark/tasks/<task_id> \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile deepseek_v4_flash \
  --env-file .env \
  --yolo \
  --agent-docker \
  --eval-docker \
  --output experiments/mini-swe-agent/smoke-<task_id>-$(date +%Y%m%d-%H%M%S)
```

通过标准：

- `run.json` 里 `agent_backend == "docker"`
- `run.json` 里 `eval_backend == "docker"`
- `evaluation.result_json` 指向 `eval/result.json`
- 失败也必须是结构化失败，不能卡死或打爆机器

## 2. 跑正式 suite

推荐用 `run.sh`，它默认跑 `benchmark/tasks` 下当前主榜任务：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
RUN_ID=benchmark-main-flash-run1-$(date +%Y%m%d-%H%M%S) \
./run.sh
```

Pro 示例：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=deepseek_v4_pro \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
RUN_ID=benchmark-main-pro-run1-$(date +%Y%m%d-%H%M%S) \
./run.sh
```

SiliconFlow 示例：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=minimax_m2_5 \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
RUN_ID=benchmark-main-minimax-m2.5-run1-$(date +%Y%m%d-%H%M%S) \
./run.sh
```

可用 profile 以 `harness/config/agents.toml` 为准，常用包括：

```text
deepseek_v4_flash
deepseek_v4_pro
glm_5_2
kimi_k2_7_code
minimax_m2_5
qwen3_coder_30b_vllm
```

## 3. 只跑 batch-1 Docker Flash

如果当前目标是服务器上跑 **batch-1 新增 50 题的 Flash Docker 实验**，用专门脚本，不要用旧的 batch-1 review 脚本：

```bash
./run-batch1-docker-flash.sh
```

这个脚本会自动：

- 只选择带 `batch-1` tag 的 50 个 task
- 使用 `deepseek_v4_flash`
- 打开 `--agent-docker` 和 `--eval-docker`
- 设置 `FEATURELIFTBENCH_LIVE_TRAJECTORY=1`
- 设置 `NUM_WORKERS=1` 和 `RETRY_RATE_LIMIT=5`
- 跑完后生成 `analyze_benchmark_suite.py` 和 `report_entanglement_coverage.py` 输出

中断后续跑同一个 batch-1 run：

```bash
RESUME_DIR=experiments/mini-swe-agent/<run_id> ./run-batch1-docker-flash.sh
```

`run-agent` 返回 1 只表示 benchmark 里有失败题，脚本仍会生成分析；返回 2 或更高才按基础设施失败处理。

## 3.1 长跑稳定性（防挂死 / 双 runner / 丢进度）

**单 runner 规则**：同一 `OUTPUT` 目录只能有一个 suite 进程。脚本会在 `${OUTPUT}/.run.lock` 加 mkdir 锁；若已有锁则立即失败。不要用 `nohup` 叠加上一个仍在跑的目录。

**续跑前 preflight**：`run-batch1-docker-flash.sh` / 带 Docker 的 `run.sh` 会先跑 `preflight.py --docker-suite`，检查 Docker daemon、agent/eval 镜像、以及是否已有 `.run.lock`。

**Eval 外层超时**（默认 10 分钟，防 eval 容器挂死拖住 suite）：

```bash
export FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS=600   # 默认
# 或按单题 metadata.environment.timeout_seconds 推导 max(300, timeout*8)
```

超时后 harness 会 `docker kill` 容器、写结构化 `result.json`（`timed_out: true`），并继续下一题。

**增量 checkpoint**：每题结束后更新 `suite.json`（`checkpoint: true`）。suite 正常结束会覆盖为最终版（无 `checkpoint`）。中途崩溃时 `--resume` 可读 checkpoint + 各题 `run.json` fallback。

**卡住排查三步**：

1. 看 `agent/trajectory.json` 是否已到 `Submitted`
2. `docker ps --filter name=flb-` 找挂住的 agent/eval 容器
3. 看该题 `run.json` / `eval/result.json` 是否已写入

诊断脚本（只读）：

```bash
./harness/scripts/check_run_health.sh experiments/mini-swe-agent/<run_id>
```

**Docker 内存建议**：

| 环境 | 建议 |
| --- | --- |
| Linux 服务器（≥16GB 可用） | 默认 agent 8g + eval 4g 串行即可 |
| macOS Docker Desktop | Settings → Resources → Memory **≥16GB**；避免同 OUTPUT 双 runner |

## 4. 续跑完整主榜

中断后不要新开目录，直接 resume：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
RESUME_DIR=experiments/mini-swe-agent/<run_id> \
./run.sh
```

如果想让首轮失败题自动再跑一轮：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
EXTRA_AGENT_PASSES=1 \
./run.sh
```

## 5. 只重评，不重跑 agent

如果 agent 已经产出 submission，但你要用 Docker eval 重新评分：

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/reeval_suite.py \
  experiments/mini-swe-agent/<run_id> \
  --docker \
  --workers 1
```

论文/正式表格只引用 Docker eval 后的 `suite.json` 和每题 `eval/result.json`。

## 6. 跑完看哪里

```text
experiments/mini-swe-agent/<run_id>/
  suite.json
  <task_id>/
    run.json
    agent/stdout.log
    agent/stderr.log
    agent/trajectory.json
    submission/
    eval/result.json
    eval/logs/
```

常用分析：

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/analyze_benchmark_suite.py \
  experiments/mini-swe-agent/<run_id>

PYTHONPATH=harness .venv/bin/python harness/scripts/report_entanglement_coverage.py \
  --suite-dir experiments/mini-swe-agent/<run_id>
```

## 7. 资源与安全默认值

Eval Docker 默认：

```text
network: none
memory: 4g
memory-swap: 4g
cpus: 2
pids-limit: 256
root filesystem: read-only
/tmp: tmpfs 2g
stdout/stderr: 8 MiB per stream
```

Agent Docker 默认：

```text
network: bridge
memory: 8g
cpus: 2
pids-limit: 512
mounts: prepared workspace rw, agent output rw, harness ro
not mounted: benchmark root, hidden tests, host home, .env, Docker socket
stdout/stderr: 8 MiB per stream
```

常用覆盖：

```bash
FEATURELIFTBENCH_DOCKER_MEMORY=6g
FEATURELIFTBENCH_DOCKER_CPUS=2
FEATURELIFTBENCH_DOCKER_PIDS=256
FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS=600
FEATURELIFTBENCH_AGENT_DOCKER_MEMORY=8g
FEATURELIFTBENCH_AGENT_DOCKER_CPUS=2
FEATURELIFTBENCH_AGENT_DOCKER_PIDS=512
FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES=8388608
```

`FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES` 名称含 `BYTES`，解析单位为 **MiB**（见 harness 实现）；正式实验优先用 Docker 边界。

本地 `EVAL_MEMORY_MB` / `AGENT_MEMORY_MB` 仍可用于非 Docker 调试；正式实验优先使用 Docker 边界。

## 8. 当前建议顺序

1. 先 build 两个镜像。
2. 用 `--agent-docker --eval-docker` 跑 1 道 smoke。
3. Flash 跑完整主榜 1 次。
4. Pro 跑完整主榜 1 次。
5. 如果要写强模型稳定性比较，再对每个模型跑 3 次。
6. 所有正式结果都保留 `suite.json`、每题 `run.json`、每题 `eval/result.json`。
