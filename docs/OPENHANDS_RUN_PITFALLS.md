# OpenHands 全量跑批踩坑记录与改进建议

本文档汇总 **2026-07-01** 在服务器上并行跑 FeatureLiftBench（OpenHands + 本地 vLLM + DeepSeek API）时遇到的全部基础设施问题、根因、已落地修复，以及对当前 harness 的改进建议。

适用场景：OpenHands 主测 agent、Docker agent/eval、多模型并行长跑。

最后更新：2026-07-01

---

## 1. 当天实验配置（上下文）

| 实验 | Profile | 后端 | Workers | 输出目录示例 |
|------|---------|------|---------|--------------|
| Qwen3-Next-80B | `openhands_qwen3_next_80b_vllm` | 本机 vLLM `:8008` | 2 | `openhands-qwen3-80b-main-*` |
| Qwen3-Coder-30B | `openhands_qwen3_coder_30b_vllm` | 本机 vLLM `:8009`（已开 tool-choice） | 2 | `openhands-qwen3-coder-30b-main-*` |
| DeepSeek v4-flash | `openhands_deepseek_v4_flash` | `https://api.deepseek.com/v1` | 1 | `openhands-sanity-*` |

共同环境：`FEATURELIFTBENCH_AGENT_DOCKER=1`、`FEATURELIFTBENCH_EVAL_DOCKER=1`（`run_openhands.sh` 现已默认开启）。

---

## 2. 问题清单（按严重性与出现频率）

### 2.1 「秒级 missing_submission」——最先要识别的坏信号

**现象**

- 单题 ~10–15 秒结束，`exit_status: missing_submission`
- `agent/usage.json` 中 `api_calls: 0`（或极少）、`total_tokens: 0`
- 终端进度条快速刷题，不像正常做题

**含义**：不是模型不会做，而是 **Agent 根本没连上 LLM 或首轮请求就失败**。不要续跑污染目录，应先查 `agent/openhands_events.jsonl` 或 `agent/stderr.log`。

**当天触发的具体根因**（见下文各节）：

1. Docker bridge 访问不到宿主机 `127.0.0.1:8008`
2. LiteLLM cost tracking 因未知模型崩溃（mini）
3. OpenHands `tool_choice=auto` 但 vLLM 未开 `--enable-auto-tool-choice`
4. DeepSeek 模型名被错误剥前缀，LiteLLM 报 `LLM Provider NOT provided`
5. 命令行写了占位符 `FEATURELIFTBENCH_API_KEY=你的key`，覆盖 `.env` 真 key

---

### 2.2 本机 vLLM：Docker 网络（Qwen 80B / mini）

**现象**

- `Connection refused` 访问 `http://127.0.0.1:8008/v1`
- mini-swe-agent / OpenHands 在 agent 容器内均失败

**根因**

- 默认 `FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=bridge`
- 容器内 `127.0.0.1` 指向容器自身，不是宿主机 vLLM

**修复**

```bash
export FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host
```

仅 **本机 vLLM** 需要；DeepSeek 等公网 API 用默认 bridge 即可。

**改进建议**：preflight 对 `api_base` 含 `127.0.0.1` / `host.docker.internal` 且 network≠host 时打印 **明确 warning**（见 §4）。

---

### 2.3 mini-swe-agent：LiteLLM cost tracking（Qwen 80B）

**现象**

- mini 在真正调用模型前退出
- 报错与 `openai/Qwen3-Next-80B-A3B-Instruct` 不在 LiteLLM 价目表有关

**修复**

在 `agents.toml` profile 增加：

```toml
cost_tracking = "ignore_errors"
```

对应环境变量 `MSWEA_COST_TRACKING=ignore_errors`（`agent_config.py` 已支持 profile 字段）。

---

### 2.4 OpenHands + vLLM：原生 tool calling（80B 未重启 vLLM）

**现象**

```text
LLMBadRequestError: "auto" tool choice requires --enable-auto-tool-choice
and --tool-call-parser to be set
```

- `assistant_steps: 0`，OpenHands 首轮 400 后直接退出
- mini 能跑、OpenHands 不能：mini 解析 bash 文本块，不依赖 function calling

**根因**

- OpenHands 默认 `native_tool_calling=True`，请求带 `tool_choice="auto"`
- 80B vLLM 启动时未加 tool-choice 参数

**两条修复路径**

| 路径 | 做法 | 是否动 vLLM |
|------|------|-------------|
| A. 重启 vLLM | `--enable-auto-tool-choice --tool-call-parser hermes`（或模型对应 parser） | 是 |
| B. 提示词式工具调用（当天采用） | profile 设 `native_tool_calling = false` | 否 |

**路径 B 的隐藏坑**：`openhands --override-with-envs` **只覆盖** `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`，**不读** `LLM_NATIVE_TOOL_CALLING`。

**最终修复**（`openhands_runner.py`）：

- 当 `LLM_NATIVE_TOOL_CALLING=false` 时，启动前用 OpenHands SDK 生成 `~/.openhands/agent_settings.json`，写入 `native_tool_calling=False`

**改进建议**：在 preflight smoke 里检测 vLLM `/v1/models` 是否支持 tools，或与 profile 的 `native_tool_calling` 不一致时 fail fast（见 §4）。

---

### 2.5 OpenHands 启动卡住 ~3 分钟无输出

**现象**

- 进程在跑，但几分钟内 0 events、0 stdout
- 最终可能超时或极慢才开始

**根因**

- OpenHands CLI 启动时 **无条件** `git clone github.com/OpenHands/extensions` 加载 public skills
- 服务器无法访问 GitHub → git 内置超时 ~120s，且可能多次重试

**修复**（`agent_docker.py`）

- OpenHands agent 容器默认 `--add-host`：
  - `github.com:127.0.0.1`
  - `codeload.github.com:127.0.0.1`
  - `raw.githubusercontent.com:127.0.0.1`
- git 秒级 connection refused → OpenHands 跳过 public skills 继续跑

可覆盖：`FEATURELIFTBENCH_AGENT_DOCKER_ADD_HOSTS`（逗号分隔；设空可禁用）。

---

### 2.6 DeepSeek API：LiteLLM 模型 provider 前缀

**现象**

```text
LLMBadRequestError: LLM Provider NOT provided.
You passed model=deepseek-v4-flash
```

- 与 2.1 相同：`api_calls: 0`、快速 `missing_submission`

**根因**

- profile 配置 `deepseek/deepseek-v4-flash`
- `normalize_api_model_name()` 对 `api.deepseek.com` 会剥掉 `deepseek/` 前缀（为 mini 直连接口设计）
- `apply_openhands_llm_env()` 曾复用该逻辑 → `LLM_MODEL=deepseek-v4-flash`
- OpenHands 经 LiteLLM 调用时 **必须保留** `deepseek/deepseek-v4-flash`

**修复**（`llm_env.py`）

- `apply_openhands_llm_env()` 不再剥前缀，原样写入 `LLM_MODEL`

**说明**：`normalize_api_model_name()` 仍保留给 mini 等路径使用；OpenHands 与 mini 对模型字符串需求不同，不宜共用一套 normalize。

---

### 2.7 配置与操作失误

| 问题 | 现象 | 正确做法 |
|------|------|----------|
| 命令行占位符 key | `FEATURELIFTBENCH_API_KEY=你的key` 覆盖 `.env` | 只写 `.env`，直接 `./run_openhands.sh` |
| 误用 `RESUME_DIR` 续跑坏目录 | 重试仍 `api_calls: 0` | 基础设施修好后 **新开 RUN_ID**，或确认 events 无 LLM 错误再 resume |
| `exit 130` | `Stopping suite run...` | 用户 Ctrl+C，非 harness bug |
| `run_openhands.sh` 默认 RUN_ID 名 | 全量 benchmark 输出到 `openhands-sanity-*` | 全量时设 `RUN_ID=openhands-deepseek-flash-main-$(date +%Y%m%d-%H%M%S)` |
| 残留 `flb-*` 容器 | preflight warning | 空闲时 `docker rm -f $(docker ps -aq --filter name=flb-)`，勿杀正在跑的 |

**env 优先级**（`agent_config.py`）：

```text
os.environ（命令行 export） > .env 文件
```

命令行一旦写了 key，`.env` 不会生效。

---

### 2.8 进度条与 token 显示

| 现象 | 原因 |
|------|------|
| 无 Rich 进度条 | 命令带了 `NO_PROGRESS=1` |
| 进度显示 `Event N` 而非 token | OpenHands poller 读 `openhands_events.jsonl`；token 仅在 event 带 usage 时出现 |
| `usage.json` 题中为空 | 通常题末才写；题中用 events 判断是否在跑 |

**正常健康信号**：events 持续增长、`file_editor` / `terminal` 等 ActionEvent、stdout 出现 `Agent initialized with model: ...`。

---

### 2.9 Eval 与其它

| 问题 | 说明 |
|------|------|
| `docker_returncode=124` | eval 外层 `docker run` 墙钟超时（默认 `max(300, timeout_seconds×8)`，常见 **480s**），不一定是 OOM |
| 模型 `failed` 但 `api_calls > 0` | 基础设施正常，分数低是模型能力问题 |
| 内存 | 见 §3 Docker 资源限制调研；当天 **无需调大** Docker 内存限额 |

---

## 3. Docker 资源限制调研（2026-07-01）

本节记录当天在三路 OpenHands 并行长跑期间，对 **agent / eval Docker 限额是否足够** 的实测结论与调参建议。调研方法：`docker stats`、扫描 `experiments/**/eval/result.json`、检查 `OOMKilled` / `resource_limited` 字段。

### 3.1 结论摘要

| 结论 | 说明 |
|------|------|
| **内存不用调大** | agent 峰值 ~340 MiB / 8 GiB（~4%）；eval ~45 MiB / 4 GiB（~1%） |
| **CPU / pids 不用调大** | 无 `resource_limited`、无 agent `log_limit_exceeded` |
| **真正要关注的是 eval 超时与并发** | 11/22 次 eval 为 `returncode=124`，且 `resource_limited=false`、`OOMKilled=false` |
| **宿主机 RAM 充裕** | ~1.9 TiB 总内存，~1.2 TiB available；瓶颈在 GPU 显存（vLLM），非 Docker cgroup |

**推荐保持默认**（正式实验口径见 [SETUP.md](SETUP.md) §4）：

```bash
# Agent 容器
FEATURELIFTBENCH_AGENT_DOCKER_MEMORY=8g
FEATURELIFTBENCH_AGENT_DOCKER_CPUS=2
FEATURELIFTBENCH_AGENT_DOCKER_PIDS=512

# Eval 容器
FEATURELIFTBENCH_DOCKER_MEMORY=4g
FEATURELIFTBENCH_DOCKER_CPUS=2
FEATURELIFTBENCH_DOCKER_PIDS=256

# pytest 子进程 RLIMIT（非 Docker 层；run_openhands.sh 默认 4096）
EVAL_MEMORY_MB=4096

# 日志保护
FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES=8388608
```

### 3.2 默认限额与代码位置

| 层级 | 环境变量 | 默认值 | 定义位置 |
|------|----------|--------|----------|
| Agent 内存 | `FEATURELIFTBENCH_AGENT_DOCKER_MEMORY` | `8g` | `agent_docker.py` |
| Agent CPU | `FEATURELIFTBENCH_AGENT_DOCKER_CPUS` | `2` | `agent_docker.py` |
| Agent pids | `FEATURELIFTBENCH_AGENT_DOCKER_PIDS` | `512` | `agent_docker.py` |
| Agent tmpfs | `FEATURELIFTBENCH_AGENT_DOCKER_TMPFS` | `/tmp:rw,nosuid,nodev,size=2g` | `agent_docker.py` |
| Eval 内存 | `FEATURELIFTBENCH_DOCKER_MEMORY` | `4g` | `docker_eval.py` |
| Eval swap | `FEATURELIFTBENCH_DOCKER_MEMORY_SWAP` | 同 memory（禁 swap 超出） | `docker_eval.py` |
| Eval CPU | `FEATURELIFTBENCH_DOCKER_CPUS` | `2` | `docker_eval.py` |
| Eval pids | `FEATURELIFTBENCH_DOCKER_PIDS` | `256` | `docker_eval.py` |
| Eval tmpfs | `FEATURELIFTBENCH_DOCKER_TMPFS` | `/tmp:rw,nosuid,nodev,size=2g` | `docker_eval.py` |
| Eval 墙钟超时 | `FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS` | 未设时 `max(300, per_step×8)` | `docker_eval.py` |
| pytest RLIMIT | `EVAL_MEMORY_MB` / `FEATURELIFTBENCH_EVAL_MEMORY_MB` | 宿主 `run_*.sh` 默认 `4096` | `resource_limits.py` → `run_limited.py` |

说明：

- Eval 容器 `--network none`；agent 容器默认 `bridge`（本机 vLLM 需 `FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host`）。
- `EVAL_MEMORY_MB` 通过 `docker run --env EVAL_MEMORY_MB` **继承宿主值**（仅当宿主已 export）；在容器内对 pytest 施加 `RLIMIT_AS`，与 Docker `--memory 4g` **双重限制、数值对齐**。
- 本地非 Docker 调试仍可用 `AGENT_MEMORY_MB` / `EVAL_MEMORY_MB`；论文口径以 Docker 为准。

### 3.3 当天实测占用（`docker stats --no-stream`）

| 容器类型 | 限额 | 实测 RSS | 占限额 |
|----------|------|----------|--------|
| `flb-agent-*`（OpenHands） | 8 GiB | 300–340 MiB | ~4% |
| `flb-eval-*` | 4 GiB | 45–47 MiB | ~1% |

宿主机（同期）：used ~707 GiB / 1.9 TiB，available ~1.2 TiB，swap 无。

### 3.4 失败模式分析（`eval/result.json` 扫描）

当天 `experiments/` 共 22 份 eval 结果：

| 指标 | 数量 | 含义 |
|------|------|------|
| eval 正常完成 | 12 | 写入完整 `result.json`，`docker_sandbox_error=false` |
| **`docker_returncode=124`** | **11** | 外层 `communicate(timeout=…)` 超时后 `docker kill` |
| `resource_limited=true` | **0** | 无 cgroup OOM / RLIMIT 判定 |
| `log_limit_exceeded` | **0** | 8 MiB 日志上限未触发 |
| agent `log_limit_exceeded` | **0** | — |

**124 超时特征**（以 `astroid__nodes_core__001` 为例）：

- `errors`: `["docker eval timed out after 480s"]`
- 各 phase（`build` / `public_tests` / `hidden_tests`）`duration_seconds: 0`，`resource_limited: false`
- `docker inspect` → `OOMKilled: false`
- 部分卡住容器 `docker logs` 仅见 `MemoryError`（线程启动），但 cgroup 内存仍 ~45 MiB → **更像 eval 挂起/并发争抢，而非 4 GiB 真不够**

**成功 eval 耗时参考**（80B 轮，`arrow__parse_format_core__001` 等）：各 phase 合计约 **0.5s**（build 失败早停），说明正常路径下 4 g/2CPU 绰绰有余。

### 3.5 与「调大内存」的对比：何时才需要加

| 信号 | 建议 |
|------|------|
| `resource_limited: true` 或 `OOMKilled: true` | 考虑 `FEATURELIFTBENCH_DOCKER_MEMORY=6g` 或 `8g`，并同步 `EVAL_MEMORY_MB` |
| pytest stderr 含 `Cannot allocate memory` 且容器 RSS 接近限额 | 同上 |
| **`returncode=124` 且 `resource_limited=false`** | **不要先加内存**；见 §3.6 |
| agent `log_limit_exceeded` | 提高 `FEATURELIFTBENCH_COMMAND_OUTPUT_LIMIT_BYTES` 或降噪，非加内存 |

当天数据 **不满足** 加内存条件。

### 3.6 124 超时的运维建议（优先于加内存）

1. **每路实验 `NUM_WORKERS=1`**  
   三路 benchmark 已并行；单路 2 workers 易出现多个 `flb-eval-*` 同时挂起（当天曾见容器 Up 6+ 分钟）。

2. **可选加大 eval 墙钟超时**（若重试后仍 124）：
   ```bash
   export FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS=900
   ```
   默认公式见 `docker_eval.py` `_docker_eval_timeout_seconds()`；显式设置可覆盖。

3. **清理 stale `flb-*` 容器**（确认无在跑任务后）：
   ```bash
   docker rm -f $(docker ps -aq --filter name=flb-)
   ```

4. **代码侧改进（待做）**：见 §5 建议 13——超时与 `infra_failed` 分栏、preflight 检测僵尸 eval 容器。

### 3.7 快速自检命令

```bash
# 当前 flb 容器占用
docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}' | grep flb-

# 扫描 eval 超时 vs OOM
python3 -c "
import json
from pathlib import Path
from collections import Counter
c = Counter()
for p in Path('experiments').rglob('eval/result.json'):
    r = json.loads(p.read_text())
    if r.get('docker_returncode') == 124: c['timeout_124'] += 1
    if r.get('resource_limited'): c['resource_limited'] += 1
    if r.get('log_limit_exceeded'): c['log_limit'] += 1
print(dict(c))
"

# 单个卡住容器是否 OOM
docker inspect <container_name> --format 'OOM={{.State.OOMKilled}} MemLimit={{.HostConfig.Memory}}'
```

---

## 4. 已落地代码/配置变更（2026-07-01）

| 文件 | 变更 |
|------|------|
| `harness/config/agents.toml` | 新增 `openhands_*` profiles；80B 设 `native_tool_calling=false`、`cost_tracking` |
| `harness/featureliftbench/agent_config.py` | `cost_tracking`、`native_tool_calling` profile 字段 |
| `harness/featureliftbench/llm_env.py` | OpenHands 不剥 DeepSeek 前缀 |
| `harness/featureliftbench/openhands_runner.py` | 预置 `agent_settings.json` 关闭 native tool calling |
| `harness/featureliftbench/agent_docker.py` | OpenHands 默认 block GitHub `--add-host` |
| `run_openhands.sh` | 默认开启 agent/eval Docker |
| `.env` | 写入 DeepSeek key/base（不提交 git） |

---

## 5. 对当前代码的改进建议（优先级）

### P0 — 跑批前就能拦住

1. **preflight 增强 LLM 连通性**
   - 对当前 profile 发一次最小 chat/completions（或 OpenHands 支持的 health check）
   - 失败时打印模型名、base URL、完整 LiteLLM 错误，**exit non-zero**
   - 避免全量 100 题刷 `missing_submission`

2. **preflight 检测无效 API key**
   - 拒绝字面量占位符（如 `你的key`、`sk-...`、`changeme`）
   - 若 `os.environ` 与 `.env` 不一致，打印 warning：「命令行 key 覆盖了 .env」

3. **单题 smoke 纳入 CI / `run_openhands.sh` 可选 `--smoke-first`**
   - 要求 `api_calls >= 1` 且 events 无 `LLMBadRequestError` 才进入全量

### P1 — 降低配置复杂度

4. **拆分模型名 normalize 策略**
   - `normalize_api_model_name_for_mini()` vs `normalize_api_model_name_for_openhands()`
   - 或在 profile 增加 `strip_provider_prefix = false`，避免运行时隐式行为

5. **本地 vLLM profile 自动提示 network=host**
   - `api_base` 匹配 `127.0.0.1|localhost` 且未设 host 网络 → preflight warning/fail

6. **`run_openhands.sh` 全量默认 RUN_ID**
   - `benchmark/tasks` 时用 `openhands-main-*`，sanity 用 `openhands-sanity-*`，减少目录混淆

7. **`.env.example` 补充 OpenHands / vLLM 变量说明**
   - `VLLM_QWEN3_NEXT_80B_*`、`FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host` 注释

### P2 — 可观测性与运维

8. **suite 级「基础设施失败」与「模型失败」分栏**
   - `api_calls==0` → `infra_failed` 或 `agent_setup_failed`，与 `failed`（有 submission 但分低）区分

9. **进度 UI 显示最近 LLM 错误摘要**
   - 从 `openhands_events.jsonl` 拉 `ConversationErrorEvent`，不必人工 grep

10. **preflight 可选清理 stale `flb-*`**
    - `--cleanup-stale-containers` 或文档一键脚本（带确认）

11. **resume 前检查**
    - 若目录内多数题 `api_calls==0`，提示「疑似基础设施失败，建议新 RUN_ID」

### P3 — 长期

12. **vLLM tool-choice 能力与 profile 对齐**
    - 文档化：80B 用 prompt-based FC；Coder 30B 用 native FC + `qwen3_coder` parser

13. **eval 124 超时**
    - 高 worker 时考虑调 `FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS` 或降并发

14. **密钥管理**
    - 支持 `FEATURELIFTBENCH_API_KEY_FILE`，减少 key 进 shell history

---

## 6. 快速排障检查表

题跑得太快或 `missing_submission` 时，按顺序执行：

```bash
TASK=arrow__parse_format_core__001
OUT=experiments/openhands-agent/<your-run>

# 1. 有无 LLM 调用
cat "$OUT/$TASK/agent/usage.json" 2>/dev/null | python -m json.tool

# 2. OpenHands 事件错误
python3 -c "
import json
for i,l in enumerate(open('$OUT/$TASK/agent/openhands_events.jsonl')):
    e=json.loads(l)
    if e.get('code'):
        print(i+1, e['code'][:300])
"

# 3. 模型是否初始化
grep -i 'initialized\|Error\|BadRequest' "$OUT/$TASK/agent/openhands_stdout.log" | tail -5

# 4. preflight 用的 key 来源
grep FEATURELIFTBENCH_API_KEY .env
# 确认当前 shell 没有 export 覆盖
echo "shell key=${FEATURELIFTBENCH_API_KEY:-<unset>}"
```

| 检查项 | 健康 | 异常 |
|--------|------|------|
| `api_calls` | > 0 | 0 → 查 events |
| events 行数 | 持续增长 | 0 或仅 1–2 条 |
| `LLMBadRequestError` | 无 | 按 §2.4–2.6 修 |
| preflight `api_key_present` | true | 填 `.env` |

---

## 7. 推荐启动命令（修复后）

### DeepSeek（读 `.env`，无需手写 key）

```bash
cd /data_nvme0/chz2/FeatureLiftBench
RUN_ID=openhands-deepseek-flash-main-$(date +%Y%m%d-%H%M%S) \
./run_openhands.sh benchmark/tasks
```

### Qwen3-Next-80B OpenHands（prompt-based FC + host 网络）

```bash
VLLM_QWEN3_NEXT_80B_API_KEY=sk-dummy \
VLLM_QWEN3_NEXT_80B_API_BASE=http://127.0.0.1:8008/v1 \
FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host \
AGENT_PROFILE=openhands_qwen3_next_80b_vllm \
NUM_WORKERS=1 \
RUN_ID=openhands-qwen3-80b-main-$(date +%Y%m%d-%H%M%S) \
./run_openhands.sh benchmark/tasks
```

### Qwen3-Coder-30B OpenHands（native FC，vLLM 已开 tool-choice）

```bash
VLLM_QWEN3_CODER_30B_API_KEY=sk-dummy \
VLLM_QWEN3_CODER_30B_API_BASE=http://127.0.0.1:8009/v1 \
FEATURELIFTBENCH_AGENT_DOCKER_NETWORK=host \
AGENT_PROFILE=openhands_qwen3_coder_30b_vllm \
NUM_WORKERS=1 \
RUN_ID=openhands-qwen3-coder-30b-main-$(date +%Y%m%d-%H%M%S) \
./run_openhands.sh benchmark/tasks
```

---

## 8. 相关文档

- 操作手册：[OPENHANDS_SERVER_RUNBOOK.md](OPENHANDS_SERVER_RUNBOOK.md)
- 通用局限：[limitations.md](limitations.md)
- 速查：[RUN.md](../RUN.md)

---

## 9. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-07-01 | 首版：mini/vLLM 网络、cost tracking、OpenHands tool calling、GitHub clone、DeepSeek 模型名、`.env` 与 resume 踩坑 |
| 2026-07-01 | 增补 §3 Docker 资源限制调研：默认限额、实测占用、124 超时 vs OOM、调参建议 |
