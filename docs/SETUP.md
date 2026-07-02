# 环境与部署

> Current path: for running the benchmark with OpenHands, use
> [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md) and [../RUN.md](../RUN.md).
> This file remains the broader environment reference.

本文档说明在**本机或 Linux 服务器**上跑 FeatureLiftBench agent suite 所需的环境、配置与常用命令。

相关：[limitations.md](limitations.md) · [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)（续跑与重试）

最后更新：2026-06-29

---

## 快速开始

```bash
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench

./setup.sh              # 创建 .venv，安装 pytest / rich / mini-swe-agent
nano .env               # 填入 API Key（见下文）
docker/build_agent_image.sh featureliftbench-agent:latest
docker/build_eval_image.sh featureliftbench-eval:latest

FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
./run.sh                # 默认 profile 见 harness/config/agents.toml
```

**本机常用（conda + 本地 vLLM 或 SiliconFlow API）**：见根目录 [`RUN.md`](../RUN.md)。

开跑前可选验证：

```bash
PYTHONPATH=harness python harness/scripts/preflight.py \
  --agent-profile minimax_m2_5 \
  --mini-bin "$(which mini)"
```

长跑建议 `tmux` / `screen` 挂后台。

---

## 1. 系统要求

| 项目 | 要求 |
| --- | --- |
| **操作系统** | Linux 或 macOS（服务器推荐 Linux） |
| **Python** | **3.11+**（推荐 **3.12**）。3.9/3.10 缺少 `tomllib`，CLI 无法启动 |
| **Linux 系统包** | Debian/Ubuntu 需 **`python3.12-venv`**（及 `python3.12-pip`）；仅装 `python3.12` 不够 |
| **磁盘** | 仓库约 **150MB+**（含 task `repo/` 快照）；`experiments/` 每轮额外占用（轨迹、submission、eval 日志） |
| **内存** | 建议 **8GB+**；正式 suite 默认 `NUM_WORKERS=1` + 内存上限（见下文 §4） |
| **网络** | 需访问所选模型的 **API**（DeepSeek、SiliconFlow 等）；agent 跑题期间要联网 |
| **Docker** | **正式实验推荐启用**；eval 用禁网短命容器，agent 用 bounded container |

不需要事先全局安装 conda；推荐用项目内 **`.venv`**（`./setup.sh` 自动创建）。

**Debian / Ubuntu 服务器**（在 `./setup.sh` 之前）：

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-pip git
```

若已装 `python3.12` 但 `./setup.sh` 报 `No module named venv`，补装：

```bash
sudo apt install -y python3.12-venv python3.12-pip
```

---

## 2. `./setup.sh` 安装内容

根目录 [`setup.sh`](../setup.sh) 会调用 [`harness/scripts/server_setup.sh`](../harness/scripts/server_setup.sh)，完成：

1. 检测 Python 3.11+
2. 创建 `.venv/`
3. `pip install pytest==7.4.4 rich mini-swe-agent`
4. 从 [`harness/config/agents.example.toml`](../harness/config/agents.example.toml) 生成 `harness/config/agents.toml`（若不存在）
5. 从 [`.env.example`](../.env.example) 生成 `.env`（若不存在）
6. 将各 profile 的 `agent_bin` 指向 `.venv/bin/mini`

Harness **没有**独立的 `requirements.txt`；运行依赖即上述 pip 包 + Python 标准库。

可选环境变量（`setup.sh` / `server_setup.sh`）：

| 变量 | 说明 |
| --- | --- |
| `PYTHON` | 指定创建 venv 的解释器，如 `python3.12` |
| `VENV_DIR` | venv 路径，默认 `.venv` |
| `SKIP_MINI=1` | 跳过 `pip install mini-swe-agent`（需自行提供 `MINI_BIN`） |
| `MINI_BIN` | 已有 `mini` 可执行文件路径 |

---

## 3. 配置文件（不进 Git）

| 文件 | 作用 | 如何获得 |
| --- | --- | --- |
| [`.env`](../.env) | API Key、Base URL | `./setup.sh` 复制 example 后**手工填写** |
| [`harness/config/agents.toml`](../harness/config/agents.toml) | model、profile、`agent_bin` | `./setup.sh` 从 example 生成；可改默认 profile |

`.gitignore` 已忽略上述文件；**换机器需重新配置或 scp**：

```bash
scp .env user@server:/path/to/FeatureLiftBench/.env
```

### DeepSeek（`run.sh` 默认 `deepseek_v4_pro`）

```bash
FEATURELIFTBENCH_API_KEY=sk-...
FEATURELIFTBENCH_API_BASE=https://api.deepseek.com/v1
```

### SiliconFlow API（GLM-5.2 / Kimi / MiniMax / Qwen 等）

```bash
SILICONFLOW_API_KEY=sk-...
SILICONFLOW_API_BASE=https://api.siliconflow.cn/v1
```

**注意：** Base URL 必须是 `https://api.siliconflow.cn/v1`，**不要**带 `/chat/completions`。

API 跑完整主榜建议（限流 500 RPM / 2M TPM）：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=minimax_m2_5 NUM_WORKERS=1 RETRY_RATE_LIMIT=5 ./run.sh
```

完整命令见 [`RUN.md`](../RUN.md)。

### 本地 vLLM（自建 endpoint）

```bash
VLLM_GPT_OSS_120B_API_KEY=sk-dummy
VLLM_GPT_OSS_120B_API_BASE=http://127.0.0.1:8008/v1

VLLM_QWEN3_CODER_30B_API_KEY=sk-dummy
VLLM_QWEN3_CODER_30B_API_BASE=http://127.0.0.1:8009/v1
```

推荐 `conda activate bench`，`run.sh` 优先用 `$CONDA_PREFIX/bin/python`：

```bash
AGENT_PROFILE=qwen3_coder_30b_vllm NUM_WORKERS=1 ./run.sh
```

运行时指定 profile：

```bash
AGENT_PROFILE=qwen3_6_27b ./run.sh
```

### Profile 一览

见 [`harness/config/agents.example.toml`](../harness/config/agents.example.toml)（本地 `agents.toml` 可能含机器专属 `agent_bin` 路径）：

| Profile | 模型 | Key 环境变量 |
| --- | --- | --- |
| `deepseek_v4_pro` | deepseek-v4-pro | `FEATURELIFTBENCH_*` |
| `deepseek_v4_flash` | deepseek-v4-flash | `FEATURELIFTBENCH_*` |
| `gpt_oss_120b_vllm` | GPT-OSS-120B（本地 vLLM） | `VLLM_GPT_OSS_120B_*` |
| `qwen3_coder_30b_vllm` | Qwen3-Coder-30B（本地 vLLM） | `VLLM_QWEN3_CODER_30B_*` |
| `glm_5_2` | zai-org/GLM-5.2 | `SILICONFLOW_*` |
| `kimi_k2_7_code` | moonshotai/Kimi-K2.7-Code | `SILICONFLOW_*` |
| `minimax_m2_5` | MiniMaxAI/MiniMax-M2.5 | `SILICONFLOW_*` |
| `qwen3_6_27b` | Qwen/Qwen3.6-27B | `SILICONFLOW_*` |
| `nex_n2_pro` | nex-agi/Nex-N2-Pro | `SILICONFLOW_*` |

---

## 4. 运行 suite

[`run.sh`](../run.sh) 在开跑前会调用 [`harness/scripts/preflight.py`](../harness/scripts/preflight.py)，检查 Python、配置、`mini`、pytest、**非空 API Key**。

正式实验推荐直接打开 agent Docker 和 eval Docker：

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
RUN_ID=benchmark-main-flash-run1-$(date +%Y%m%d-%H%M%S) \
./run.sh
```

常用环境变量：

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `AGENT_PROFILE` | `agents.toml` 中 `profile` 字段 | 如 `minimax_m2_5`、`qwen3_coder_30b_vllm` |
| `FEATURELIFTBENCH_AGENT_DOCKER` | 空 | 设为 `1` 后 agent 在短命 Docker container 中运行 |
| `FEATURELIFTBENCH_EVAL_DOCKER` | 空 | 设为 `1` 后每题 submission 用 Docker eval 评分 |
| `NUM_WORKERS` | `1` | 并行题数；正式 Docker 跑批和 SiliconFlow API 建议 `1` |
| `RETRY_RATE_LIMIT` | `2` | 429 限流时最多重试次数（每次等 ~65s）；API 建议 `5` |
| `RUN_ID` | 时间戳 | 新 run 的目录名 |
| `RESUME_DIR` | — | 中断续跑，同目录 `--resume` |
| `EXTRA_AGENT_PASSES` | `0` | 首轮结束后自动再跑失败题 |
| `NO_PROGRESS` | — | 设为 `1` 关闭 Rich 进度条 |

示例：

```bash
# 新跑
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 ./run.sh

# 续跑
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 \
RESUME_DIR=experiments/mini-swe-agent/<run_id> ./run.sh

# 挂机自动二轮
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 \
EXTRA_AGENT_PASSES=1 ./run.sh

# 换 Flash，保持串行
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=deepseek_v4_flash NUM_WORKERS=1 ./run.sh
```

### Batch-1 Flash 专用跑法

如果只跑 batch-1 新增 50 题的 Docker Flash 实验，直接用根目录脚本：

```bash
./run-batch1-docker-flash.sh
```

它会自动筛选 `batch-1` tag、启用 agent/eval Docker、使用 `deepseek_v4_flash`、设置 `FEATURELIFTBENCH_LIVE_TRAJECTORY=1`、串行运行并在结束后生成分析。中断后续跑：

```bash
RESUME_DIR=experiments/mini-swe-agent/<run_id> ./run-batch1-docker-flash.sh
```

旧的 batch-1 review 脚本只用于出题验收，不用于正式 Docker Flash 实验。

### 长跑稳定性

| 机制 | 说明 |
| --- | --- |
| `.run.lock` | `run.sh` / `run-batch1-docker-flash.sh` 在 `OUTPUT` 下 mkdir 锁；禁止同目录双 runner |
| `preflight --docker-suite` | 检查 `docker info`、agent/eval 镜像、`LIVE_TRAJECTORY=0` 警告、残留 `flb-*` 容器 |
| Eval 超时 | `FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS`（默认 600）；超时记失败并继续 |
| 增量 checkpoint | 每题写完 `suite.json`（`checkpoint: true`）；resume 可读中途进度 |
| 健康诊断 | `./harness/scripts/check_run_health.sh <output-dir>` |

Mac Docker Desktop 长跑建议 Memory **≥16GB**；Linux 单 worker 默认 8g agent + 4g eval 串行峰值约 8–10GB。

### Docker 安全运行

Untrusted submission 会在 pytest 中执行；**资源边界是 benchmark 运行规格的一部分**。正式实验优先用 Docker，而不是只依赖本地 `RLIMIT_AS`。

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

本地 `EVAL_MEMORY_MB` / `AGENT_MEMORY_MB` 仍可用于非 Docker 调试；正式实验结果请优先用 Docker eval 口径。

输出目录：`experiments/mini-swe-agent/<run_id>/`（gitignored）。

手动 CLI 等价命令见根目录 [RUN.md](../RUN.md)。

---

## 5. Eval 阶段的额外说明

正式 eval 推荐走 Docker：

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/reeval_suite.py \
  experiments/mini-swe-agent/<run_id> \
  --docker \
  --workers 1
```

`run-agent` 时如果已经设置 `FEATURELIFTBENCH_EVAL_DOCKER=1` 或传入 `--eval-docker`，则每题会直接写 Docker eval 结果，不需要额外 re-eval。

Harness 评测每题时会：

1. 在 `/tmp/featureliftbench-eval-*` 建临时 venv（`--system-site-packages`）
2. 显式安装 **pytest==7.4.4**
3. 若 `requirements.lock` 非空，用 `pip install --no-index --no-deps -r requirements.lock` 装 submission 依赖（wheel 来自 `benchmark/vendor-wheels/`）

因此：

- **`allowed_dependencies` 与 `requirements.lock` 必须一致**；非空 lock 的每个包需有离线 wheel（见 `harness/scripts/bootstrap_vendor_wheels.py`）
- **pure-python 题** 保持 `allowed_dependencies: []` 且空 lock
- **Docker eval 镜像** 预装 `harness/config/benchmark_requirements.lock`，避免运行时缺 wheel；改 lock 后需重建 `featureliftbench-eval:latest`
- 维护者审计：`python harness/scripts/audit_task_dependencies.py`
- 修复 eval 基础设施问题用 [`harness/scripts/reeval_suite.py`](../harness/scripts/reeval_suite.py)（**不重跑 agent**）
- 资源与并发见上文 §4；Docker eval 会记录 `resource_limited`、`log_limit_exceeded`、`docker_sandbox_error`
- local eval 只用于开发调试，不作为论文 official baseline

---

## 6. 服务器部署清单

OpenHands 主线路见 [SERVER_DEPLOY.md](SERVER_DEPLOY.md) 与 [OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md)。简要步骤：

```bash
# 1. 克隆 / 更新
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench
git pull origin main

# 2. 环境
PYTHON=python3.12 ./setup.sh
source .venv/bin/activate
export PYTHONPATH=$PWD/harness

# 3. 密钥
cp .env.example .env
nano .env

# 4. vendor wheels + Docker 镜像（每台机器 / 每次依赖变更后）
PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py
FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest
./docker/build_eval_image.sh featureliftbench-eval:latest

# 5. 预检
PYTHONPATH=harness python harness/scripts/preflight.py \
  --bootstrap --agent openhands-agent \
  --agent-profile openhands_deepseek_v4_flash \
  --docker-suite --llm-health-check --strict \
  --output-dir experiments/openhands-agent/preflight-$(date +%Y%m%d)

# 6. 依赖门禁（100 题主跑前）
PYTHONPATH=harness python harness/scripts/audit_task_dependencies.py

# 7. 100 题主跑（tmux）
tmux new -s flb-main100
OUT=experiments/openhands-agent/main-$(date +%Y%m%d-%H%M%S)
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=openhands_deepseek_v4_flash NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=180 \
FEATURELIFTBENCH_SUITE_TASK_COOLDOWN_SECONDS=15 \
./run_openhands.sh benchmark/tasks "$OUT" 2>&1 | tee "$OUT/run.log"
# Ctrl-B D 脱离

# 8. 验收
PYTHONPATH=harness python harness/scripts/summarize_suite_infra.py "$OUT"
```

legacy mini-swe-agent 流程（`run.sh` / `run-batch1-docker-flash.sh`）仅作历史对照，见 [RUN.md](../RUN.md) §6。

实验结果汇总表见 [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md)。

### 常见失败与处理

| 现象 | 可能原因 | 处理 |
| --- | --- | --- |
| `No module named venv` / `ensurepip is not available` | Debian/Ubuntu 未装 `python3.12-venv` | `sudo apt install python3.12-venv python3.12-pip` 后重跑 `./setup.sh` |
| `agent config file not found` | 未跑 `./setup.sh` | `./setup.sh` |
| `FEATURELIFTBENCH_API_KEY is empty` | `.env` 未填 key | 编辑 `.env` |
| `mini-swe-agent CLI not found` | 未装 mini 或 PATH 不对 | `./setup.sh`；或 `export PATH="$PWD/.venv/bin:$PATH"` |
| 全题 `missing_submission` | API key/模型/base URL 错误 | 查 `preflight`、agent `stderr.log` |
| eval `No module named pytest` | 旧 harness | `git pull`；或对旧 suite 跑 `reeval_suite.py` |
| eval 装依赖失败 | pip 缓存无 wheel | 在该机先 `pip download` 相关包，或用 Docker eval |
| Docker build 拉不到 `python:3.12-slim` | Docker mirror / DNS 问题 | 默认已用 `python:3.11-slim`；需要 3.12 时先修 Docker mirror，再设 `FEATURELIFTBENCH_*_PYTHON_BASE` |
| eval `resource_limited: true` | submission/pytest 超出 Docker 内存或被 OOM kill | 记录为资源失败；必要时调 `FEATURELIFTBENCH_DOCKER_MEMORY` |
| eval `log_limit_exceeded: true` | submission 或测试大量输出 | 记录为日志边界失败；必要时调 `FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES` |
| eval 挂死超过 10 分钟 | 旧 harness 无外层超时 | `git pull` 后用新代码；或 `docker kill` 挂住容器 |
| eval `timed_out: true` | eval 超过 `FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS` | 正常失败，suite 会继续 |
| `.run.lock` 拒绝启动 | 同 OUTPUT 已有 runner 或崩溃残留 | 确认无旧进程；`rmdir experiments/.../.run.lock` |
| agent `timed_out: true` | agent 卡住或模型长时间无响应 | 续跑该题；必要时调 `--timeout-seconds` 或 profile 限额 |
| 系统 OOM，内核日志显示 `Killed process ... (pytest)` | 未启用 Docker eval 或 Docker memory 设得过高 | 正式实验用 `FEATURELIFTBENCH_EVAL_DOCKER=1`；必要时降低 worker/内存 |

---

## 7. 与本仓库其他层的关系

| 层级 | 是否需要本页环境 |
| --- | --- |
| 跑 **agent suite**（`run.sh`） | 是：Python 3.11+、`.venv`、`mini`、`.env`；正式实验还需要 agent/eval Docker image |
| 只跑 **oracle / eval**（`verify_all_oracles.py` / `reeval_suite.py --docker`） | Python 3.11+、pytest；Docker eval 不需 API key |
| 只跑 **harness 单测** | `pip install pytest==7.4.4` + `PYTHONPATH=harness` |

Agent **单题 trajectory 中途 checkpoint** 当前不支持；**suite 级**续跑粒度为整题，支持增量 `suite.json` checkpoint + 各题 `run.json` fallback，见 [SERVER_DEPLOY.md](SERVER_DEPLOY.md) 与 [BENCHMARK_STATUS.md — 续跑与失败重试](BENCHMARK_STATUS.md#续跑与失败重试)。
