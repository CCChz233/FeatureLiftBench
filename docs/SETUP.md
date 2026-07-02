# 环境与安装

**跑 OpenHands 实验请直接看 [RUN.md](../RUN.md)。** 本文只说明环境要求、安装步骤与配置项。

---

## 快速开始

```bash
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench

PYTHON=python3.12 ./setup.sh
source .venv/bin/activate
pip install -e .

cp flb.local.toml.example flb.local.toml
cp .env.example .env
# 编辑上述两个文件

export PYTHONPATH=$PWD/harness
PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py

FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest
./docker/build_eval_image.sh featureliftbench-eval:latest

featureliftbench setup
```

---

## 系统要求

| 项目 | 要求 |
|------|------|
| OS | Linux（服务器推荐）或 macOS |
| Python | **3.11+**，推荐 **3.12**（OpenHands agent 镜像同） |
| 内存 | 8GB+；长跑建议 16GB+ |
| Docker | 正式实验必须（agent + eval 镜像） |
| 磁盘 | 仓库 ~150MB+；`experiments/` 全量预留 50GB+ |

Debian/Ubuntu：`sudo apt install -y python3.12 python3.12-venv python3.12-pip git docker.io`

---

## `./setup.sh` 做什么

1. 创建 `.venv`
2. 安装 `pytest`、`rich`、`mini-swe-agent`（legacy 对照用）
3. 从 example 生成 `harness/config/agents.toml`、`.env`（若不存在）

Harness 无独立 `requirements.txt`；OpenHands 实验依赖 **agent Docker 镜像**内的 `openhands`。

---

## 配置文件

| 文件 | 用途 | Git |
|------|------|-----|
| `flb.local.toml` | **当前主线**：模型、base_url、suite、steps | 忽略 |
| `.env` | API 密钥 | 忽略 |
| `harness/config/agents.toml` | 多 profile / CI / `agents.example.toml` 对照 | 通常忽略 |

### 云端 API（`.env`）

```bash
# DeepSeek
FEATURELIFTBENCH_API_KEY=sk-...
FEATURELIFTBENCH_API_BASE=https://api.deepseek.com/v1

# SiliconFlow
SILICONFLOW_API_KEY=sk-...
SILICONFLOW_API_BASE=https://api.siliconflow.cn/v1
```

### 本地 vLLM（`.env` 密钥 + `flb.local.toml` 地址）

```bash
VLLM_QWEN3_CODER_30B_API_KEY=sk-dummy
VLLM_QWEN3_CODER_30B_API_BASE=http://127.0.0.1:8008/v1
```

```toml
# flb.local.toml
[llm]
model = "Qwen3-Coder-30B-A3B-Instruct"
base_url = "http://127.0.0.1:8008/v1"
api_key_env = "VLLM_QWEN3_CODER_30B_API_KEY"
native_tool_calling = true
```

本地 vLLM 时 CLI 自动设置 `FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host`。

---

## Docker 镜像

| 镜像 | 作用 |
|------|------|
| `featureliftbench-agent:latest` | 跑 OpenHands（需 `FEATURELIFTBENCH_INSTALL_OPENHANDS=1` 构建） |
| `featureliftbench-eval:latest` | 禁网评测 submission |

换机器或更新 `benchmark/vendor-wheels`、lock 文件后**必须重建 eval 镜像**。

---

## 底层 CLI（调试用）

不经过 `featureliftbench run` 时：

```bash
PYTHONPATH=harness python -m featureliftbench.cli validate-task benchmark/sanity/iniconfig__parse_config__001
PYTHONPATH=harness python -m featureliftbench.cli eval <task_dir> <submission_dir> --output /tmp/out --docker
PYTHONPATH=harness python harness/scripts/preflight.py --bootstrap --agent openhands-agent --local-config flb.local.toml --docker-suite --llm-health-check
```

---

## Legacy：`mini-swe-agent` / `run.sh`

`./run.sh` + `AGENT_PROFILE` + `mini-swe-agent` 为历史路径，append-only 轨迹不适合作为长上下文主线证据。仅作对照实验时使用；命令见旧版 git 历史或 `harness/config/agents.toml` profile。

---

## 相关文档

- [RUN.md](../RUN.md) — 实验命令
- [ARCHITECTURE.md](ARCHITECTURE.md) — 实现架构
- [limitations.md](limitations.md) — 已知局限
- [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md) — 排错
