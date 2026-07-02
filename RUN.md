# FeatureLiftBench 运行手册

当前实验主线：**OpenHands + Agent Docker + Eval Docker**。配置用 `flb.local.toml`（模型与 suite），密钥只在 `.env`。

更完整的实现说明见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。排错见 [docs/OPENHANDS_RUN_PITFALLS.md](docs/OPENHANDS_RUN_PITFALLS.md)。

---

## 1. 一次性环境准备

```bash
cd /path/to/FeatureLiftBench
PYTHON=python3.12 ./setup.sh
source .venv/bin/activate
pip install -e .                    # 安装 featureliftbench CLI

cp flb.local.toml.example flb.local.toml
cp .env.example .env
# 编辑 flb.local.toml：model、base_url
# 编辑 .env：API key（本地 vLLM 用 VLLM_*_API_KEY=sk-dummy）

export PYTHONPATH=$PWD/harness

PYTHONPATH=harness python harness/scripts/bootstrap_vendor_wheels.py

FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest

./docker/build_eval_image.sh featureliftbench-eval:latest
```

每台机器拉代码或更新依赖后都要重建 Docker 镜像。

---

## 2. 配置说明

| 文件 | 内容 | Git |
|------|------|-----|
| `flb.local.toml` | 模型、`base_url`、suite、`max_steps`、workers | 忽略（从 example 复制） |
| `.env` | API key、base URL 密钥 | 忽略 |
| `harness/config/agents.toml` | CI / 多 profile 对照（可选） | 通常忽略 |

本地 vLLM 示例（`flb.local.toml`）：

```toml
[llm]
model = "Qwen3-Coder-30B-A3B-Instruct"
base_url = "http://127.0.0.1:8008/v1"
api_key_env = "VLLM_QWEN3_CODER_30B_API_KEY"
native_tool_calling = true

[agent]
kind = "openhands-agent"
max_steps = 180

[run]
suite = "pilot5"    # 可被 CLI --suite 覆盖
workers = 1
```

CLI 会自动：本地 vLLM → `AGENT_DOCKER_NETWORK=host`；开启 agent/eval Docker；规范化 health-check 模型名（`openai/` 前缀仅给 LiteLLM，probe 用裸名）。

---

## 3. Suite 一览

| suite | 题数 | 用途 |
|-------|------|------|
| `smoke` | 1 | 冒烟（`iniconfig__parse_config__001`），结束后自动 `check_openhands_smoke` |
| `sanity` | 3 | 快速烟雾集 `benchmark/sanity` |
| `pilot5` | 5 | sanity3 + batch2（arrow、bleach），合并 `pilot5-summary.json` |
| `main` | ~100 | 全量 `benchmark/tasks`，**不含**内嵌冒烟 |
| `custom` | 自定 | `[run.custom]` 指定目录与 `task_ids` |

推荐毕业路径：**setup → smoke → pilot5 → main**（无强制门禁，由你决定是否跳过）。

---

## 4. 常用命令

```bash
export PYTHONPATH=$PWD/harness

featureliftbench setup

# 冒烟（单独目录）
featureliftbench smoke --output experiments/openhands-agent/smoke-$(date +%Y%m%d-%H%M%S)

# Pilot5
featureliftbench run --suite pilot5 --max-steps 120

# 全量 main（先 smoke 再跑；进度条从 ~100 题开始）
MAIN_OUT=experiments/openhands-agent/main-$(date +%Y%m%d-%H%M%S)
mkdir -p "$MAIN_OUT"
featureliftbench run --suite main --max-steps 180 --output "$MAIN_OUT" | tee "$MAIN_OUT/run.log"

# 续跑
featureliftbench resume experiments/openhands-agent/<run-id>
```

**进度条**：不要用 `2>&1 | tee`（会破坏 Rich TTY），用 `| tee` 只重定向 stdout。

**全量前**（可选）：`PYTHONPATH=harness python harness/scripts/audit_task_dependencies.py`

**长跑**：用 `tmux`，预留 `experiments/` 50GB+ 磁盘，`NUM_WORKERS=1`。

---

## 5. 输出目录结构

```text
experiments/openhands-agent/<run-id>/
  run.meta.json              # suite、model、配置指纹
  suite.json                 # 汇总（main/sanity；pilot5 在子目录）
  benchmark-analysis.md
  featurelift-analysis.md
  infra-summary.json         # main suite；infra_clean 为基础设施达标
  <task_id>/
    run.json
    agent/usage.json
    agent/openhands_events.jsonl
    submission/featurelifted/
    eval/result.json
```

Pilot5：

```text
<run-id>/sanity3/   batch2/   pilot5-summary.json
```

---

## 6. 结果怎么读

**基础设施失败**（需先修环境，不算模型能力）：`agent_setup_failed`、`eval_infra_failed`、`rate_limited`、`agent_step_limited`、`docker_sandbox_failures > 0`。

**基准结果**：`model_failed`、`missing_submission`（在 infra 正常时）。

```bash
PYTHONPATH=harness python harness/scripts/summarize_suite_infra.py "$MAIN_OUT"
```

Pilot5 基础设施干净：`total==5`、`docker_sandbox_failures==0`、无 `eval_infra_failed` / `agent_setup_failed`。

---

## 7. 遗留脚本

| 脚本 | 行为 |
|------|------|
| `./run_openhands.sh` | 转调 `featureliftbench run`（`benchmark/tasks` → `--suite main`） |
| `./run_openhands_pilot5.sh` | 转调 `--suite pilot5` |
| `./run_easy.sh` | `featureliftbench run` 别名 |

`mini-swe-agent` 为历史对照，不作当前长上下文主线证据。

---

## 8. 相关文档

| 文档 | 用途 |
|------|------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 项目如何实现（数据流、模块、Docker） |
| [docs/SETUP.md](docs/SETUP.md) | 系统要求与安装细节 |
| [docs/CONCEPTS.md](docs/CONCEPTS.md) |  benchmark 测什么 |
| [docs/BENCHMARK_SPEC.md](docs/BENCHMARK_SPEC.md) | 可复现评测契约 |
| [docs/TASK_FORMAT.md](docs/TASK_FORMAT.md) | 单题目录格式 |
| [docs/limitations.md](docs/limitations.md) | 已知局限 |
