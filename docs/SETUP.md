# 环境与部署

本文档说明在**本机或 Linux 服务器**上跑 FeatureLiftBench agent suite 所需的环境、配置与常用命令。

相关：[limitations.md](limitations.md) · [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)（续跑与重试）

最后更新：2026-06-25

---

## 快速开始

```bash
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench

./setup.sh              # 创建 .venv，安装 pytest / rich / mini-swe-agent
nano .env               # 填入 API Key（见下文）
./run.sh                # 默认 deepseek_v4_pro，50 hard，4 workers
```

开跑前可选验证：

```bash
PYTHONPATH=harness .venv/bin/python harness/scripts/preflight.py \
  --agent-profile deepseek_v4_pro
```

长跑建议 `tmux` / `screen` 挂后台。

---

## 1. 系统要求

| 项目 | 要求 |
| --- | --- |
| **操作系统** | Linux 或 macOS（服务器推荐 Linux） |
| **Python** | **3.11+**（推荐 **3.12**）。3.9/3.10 缺少 `tomllib`，CLI 无法启动 |
| **磁盘** | 仓库约 **150MB+**（含 50 题 `repo/` 快照）；`experiments/` 每轮额外占用（轨迹、submission、eval 日志） |
| **内存** | 建议 **8GB+**；`NUM_WORKERS=4` 并行时更吃内存 |
| **网络** | 需访问所选模型的 **API**（DeepSeek、SiliconFlow 等）；agent 跑题期间要联网 |
| **Docker** | **非必须**；仅在使用 `eval --docker` 或 CI oracle 时需要 |

不需要事先全局安装 conda；推荐用项目内 **`.venv`**（`./setup.sh` 自动创建）。

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

### SiliconFlow（Qwen、Nex 等）

```bash
SILICONFLOW_API_KEY=sk-...
SILICONFLOW_API_BASE=https://api.siliconflow.cn/v1
```

运行时指定 profile：

```bash
AGENT_PROFILE=qwen3_6_27b ./run.sh
```

### Profile 一览

见 [`harness/config/agents.example.toml`](../harness/config/agents.example.toml)：

| Profile | 模型 | Key 环境变量 |
| --- | --- | --- |
| `deepseek_v4_pro` | deepseek-v4-pro | `FEATURELIFTBENCH_*` |
| `deepseek_v4_flash` | deepseek-v4-flash | `FEATURELIFTBENCH_*` |
| `qwen3_6_27b` | Qwen3.6-27B | `SILICONFLOW_*` |
| `nex_n2_pro` | Nex-N2-Pro | `SILICONFLOW_*` |

---

## 4. 运行 suite

[`run.sh`](../run.sh) 在开跑前会调用 [`harness/scripts/preflight.py`](../harness/scripts/preflight.py)，检查 Python、配置、`mini`、pytest、**非空 API Key**。

常用环境变量：

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `AGENT_PROFILE` | `deepseek_v4_pro` | `agents.toml` 中的 profile |
| `NUM_WORKERS` | `4` | 并行题数 |
| `RUN_ID` | 时间戳 | 新 run 的目录名 |
| `RESUME_DIR` | — | 中断续跑，同目录 `--resume` |
| `EXTRA_AGENT_PASSES` | `0` | 首轮结束后自动再跑失败题 |

示例：

```bash
# 新跑
./run.sh

# 续跑
RESUME_DIR=experiments/mini-swe-agent/benchmark-50-hard-pro-20260625-212817 ./run.sh

# 挂机自动二轮
EXTRA_AGENT_PASSES=1 ./run.sh

# 换 Flash、降并行
AGENT_PROFILE=deepseek_v4_flash NUM_WORKERS=2 ./run.sh
```

输出目录：`experiments/mini-swe-agent/<run_id>/`（gitignored）。

手动 CLI 等价命令见 [README.md](../README.md) 中 `run-agent` 一节。

---

## 5. Eval 阶段的额外说明

Harness 评测每题时会：

1. 在 `/tmp/featureliftbench-eval-*` 建临时 venv
2. 显式安装 **pytest==7.4.4**
3. 若 `requirements.lock` 非空，用 `pip install --no-index` 装 submission 依赖

因此：

- **多数题** `requirements.lock` 为空，eval 只依赖 harness 已装的 pytest
- **少数题** 有第三方依赖（如 `text-unidecode`），依赖**本机 pip 缓存**里已有 wheel；极干净的服务器可能 eval 失败
- 修复 eval 基础设施问题用 [`harness/scripts/reeval_suite.py`](../harness/scripts/reeval_suite.py)（**不重跑 agent**）
- 更干净的可复现 eval 可用 Docker：[`docker/Dockerfile.eval`](../docker/Dockerfile.eval)

---

## 6. 服务器部署清单

```bash
# 1. 克隆 / 更新
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench
# 或: git pull origin main

# 2. 环境（首次或换机器）
./setup.sh

# 3. 密钥（必做）
nano .env

# 4. 预检
PYTHONPATH=harness .venv/bin/python harness/scripts/preflight.py

# 5. 长跑
tmux new -s flb
./run.sh
# Ctrl-B D 脱离

# 6. 分析
python harness/scripts/analyze_benchmark_suite.py experiments/mini-swe-agent/<run_id>
```

### 常见失败与处理

| 现象 | 可能原因 | 处理 |
| --- | --- | --- |
| `agent config file not found` | 未跑 `./setup.sh` | `./setup.sh` |
| `FEATURELIFTBENCH_API_KEY is empty` | `.env` 未填 key | 编辑 `.env` |
| `mini-swe-agent CLI not found` | 未装 mini 或 PATH 不对 | `./setup.sh`；或 `export PATH="$PWD/.venv/bin:$PATH"` |
| 50 题全 `missing_submission` | API key/模型/base URL 错误 | 查 `preflight`、agent `stderr.log` |
| eval `No module named pytest` | 旧 harness | `git pull`；或对旧 suite 跑 `reeval_suite.py` |
| eval 装依赖失败 | pip 缓存无 wheel | 在该机先 `pip download` 相关包，或用 Docker eval |

---

## 7. 与本仓库其他层的关系

| 层级 | 是否需要本页环境 |
| --- | --- |
| 跑 **agent suite**（`run.sh`） | 是：Python 3.11+、`.venv`、`mini`、`.env` |
| 只跑 **oracle / eval**（`verify_all_oracles.py`） | Python 3.11+、pytest；不需 API key |
| 只跑 **harness 单测** | `pip install pytest==7.4.4` + `PYTHONPATH=harness` |

Agent **中途 checkpoint**（trajectory 断点恢复）当前不支持；续跑粒度为**整题**，见 [BENCHMARK_STATUS.md — 续跑与失败重试](BENCHMARK_STATUS.md#续跑与失败重试)。
