# 服务器部署与长跑指南

在 Linux 服务器上跑 **batch-1 Docker Flash** 或完整主榜的简明清单。详细环境说明见 [SETUP.md](SETUP.md)；命令速查见 [RUN.md](../RUN.md)。

当前如果要用 **OpenHands 测 FeatureLiftBench**，不要按本文的 mini-swe-agent
batch-1 流程直接大跑；使用专门的
[OpenHands 服务器运行指南](OPENHANDS_SERVER_RUNBOOK.md)。

最后更新：2026-06-29

---

## 1. 一次性准备

```bash
git clone git@github.com:CCChz233/FeatureLiftBench.git
cd FeatureLiftBench

./setup.sh
nano .env   # 填入 deepseek_v4_flash 等 profile 对应的 API key / base URL

docker/build_agent_image.sh featureliftbench-agent:latest
docker/build_eval_image.sh featureliftbench-eval:latest
```

预检（含 Docker 镜像与 daemon）：

```bash
source .venv/bin/activate
export PYTHONPATH=$PWD/harness
python harness/scripts/preflight.py \
  --bootstrap \
  --agent-profile deepseek_v4_flash \
  --docker-suite \
  --output-dir experiments/mini-swe-agent/preflight-check
```

---

## 2. 推荐：batch-1 Flash Docker（50 题）

```bash
tmux new -s batch1
./run-batch1-docker-flash.sh
# Ctrl-B D 脱离会话
```

脚本会自动：

- 筛选 `batch-1` tag 的 50 题
- 启用 `--agent-docker` + `--eval-docker`
- `NUM_WORKERS=1`、`RETRY_RATE_LIMIT=5`、`FEATURELIFTBENCH_LIVE_TRAJECTORY=1`
- preflight → `.run.lock` 单实例锁 → 跑 suite → 生成分析

续跑：

```bash
RESUME_DIR=experiments/mini-swe-agent/<run_id> ./run-batch1-docker-flash.sh
```

---

## 3. 完整主榜（100 题）

```bash
tmux new -s flb
FEATURELIFTBENCH_AGENT_DOCKER=1 \
FEATURELIFTBENCH_EVAL_DOCKER=1 \
AGENT_PROFILE=deepseek_v4_flash \
NUM_WORKERS=1 \
RETRY_RATE_LIMIT=5 \
RUN_ID=benchmark-main-flash-$(date +%Y%m%d-%H%M%S) \
./run.sh
```

续跑：`RESUME_DIR=experiments/mini-swe-agent/<run_id> ./run.sh`

---

## 4. 长跑稳定性机制

| 机制 | 说明 |
| --- | --- |
| **单 runner** | 同一 `OUTPUT` 只能有一个 suite 进程；`${OUTPUT}/.run.lock` 拒绝第二个 |
| **Eval 超时** | `FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS=600`（默认 10 分钟）；eval 挂死会记失败并继续 |
| **增量 checkpoint** | 每题写完 `suite.json`（`checkpoint: true`）；崩溃后 `--resume` 可读中途进度 |
| **run.json fallback** | 无完整 `suite.json` 时，resume 扫各题 `run.json` 保留已完成题 |
| **健康诊断** | `./harness/scripts/check_run_health.sh experiments/mini-swe-agent/<run_id>` |

### 资源建议

| 环境 | 建议 |
| --- | --- |
| Linux 服务器（≥16GB 可用） | 默认 agent 8g + eval 4g **串行**即可；1TB 机器无需特殊扩容 |
| macOS Docker Desktop | Memory **≥16GB**；避免同 OUTPUT 双 runner |

### 卡住排查

1. `agent/trajectory.json` 是否已到 `Submitted`
2. `docker ps --filter name=flb-` 是否有挂住容器
3. 该题是否已有 `run.json` / `eval/result.json`

Eval 超过 15 分钟无进展（旧 harness）：`docker kill <容器ID>`

---

## 5. 跑完看哪里

```text
experiments/mini-swe-agent/<run_id>/
  suite.json              # 汇总（长跑结束或 checkpoint）
  <task_id>/
    run.json
    agent/trajectory.json
    eval/result.json
```

```bash
python harness/scripts/analyze_benchmark_suite.py experiments/mini-swe-agent/<run_id>
python harness/scripts/report_entanglement_coverage.py --suite-dir experiments/mini-swe-agent/<run_id>
```

---

## 6. 常见失败

| 现象 | 处理 |
| --- | --- |
| `another suite run holds .run.lock` | 确认无旧 runner；崩溃残留则 `rmdir experiments/.../.run.lock` |
| Docker image not found | 跑 `docker/build_*_image.sh` |
| `FEATURELIFTBENCH_API_KEY is empty` | 编辑 `.env` |
| eval `timed_out: true` | 正常结构化失败，suite 会继续 |
| eval `docker_sandbox_error: true` | 容器 OOM/被杀；记录为基础设施失败，非模型功能结论 |
| 全题 `missing_submission` | 查 API key、模型名、agent `stderr.log` |

更多见 [SETUP.md §6 常见失败](SETUP.md#常见失败与处理)。

---

## 7. 相关文档

| 文档 | 用途 |
| --- | --- |
| [SETUP.md](SETUP.md) | 完整环境、Docker 边界、env 变量 |
| [RUN.md](../RUN.md) | 命令速查、smoke、续跑 |
| [limitations.md](limitations.md) | 已知局限 |
| [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) | batch-1 出题流程（非正式实验） |
