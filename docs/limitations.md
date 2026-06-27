# FeatureLiftBench 已知缺陷与限制

本文档记录 **pilot 阶段已确认** 的工程缺口、评测局限和实验口径问题。FeatureLiftBench 的长期目标是评估 Agent 能否从 vibe/legacy/entangled 仓库中完成功能级解耦；与 [README.md](README.md) 中的研究性「待讨论问题」不同，这里侧重当前实现里 **已经观察到** 的限制。

最后更新：2026-06-27（新增 pytest OOM 事故记录与内存隔离待办）

## 1. Agent Harness

| 缺陷 | 现状 | 影响 |
| --- | --- | --- |
| Suite 并行 API 限流 | `--retry-rate-limit N` 遇 429 等 ~65s 后重试；无全局 TPM 节流 | SiliconFlow 等 API 建议 `NUM_WORKERS=1`、`RETRY_RATE_LIMIT=5`；勿多模型共 key 并行 |
| 进度与 token 显示 | Rich Live 轮询 `stdout.log` + `trajectory.json`；默认经 `mini_live_runner` **每步写 trajectory** | mini stdout 仅显示 `$0.00` 不显示 token；旧 run 或未重启 harness 可能仍 `0 toks` |
| 断点续跑 | `--resume` 同目录续跑；保留非 retry 状态题，重跑 `missing_submission` / `failed` 等 | 无 agent 中途 checkpoint；`--skip-completed` 仍可用 |
| misplaced submission | `_recover_misplaced_submission` 从 `workspace/featurelifted/` 等路径回收 | 2026-06-26 前旧 run 无 `recovered_submissions` 字段 |
| 用量 / token | `run.json` / `suite.json` 从 `trajectory.json` messages 聚合 prompt/completion | SiliconFlow 上 cost 常为 0（`MSWEA_COST_TRACKING=ignore_errors`） |
| 不记录 dollar cost | litellm 对多数 API 模型无定价表 | 只记录 token、API call、step；API 费用需按平台单价自行估算 |
| 环境强依赖本机路径 | `agents.toml` / `.env` 不进 Git；`./setup.sh` 会生成并 patch `agent_bin` | 见 [SETUP.md](SETUP.md) |
| 仅内置 `mini-swe-agent` 与 `command` | 无通用 SDK 接入层 | 换 Agent 需写 adapter 或 shell 模板 |
| mini batch 必须 `--yolo` | 默认 confirm 模式会在 `Execute?` 处阻塞非交互 subprocess | `run-agent` 须加 `--yolo` 或改 mini 配置 |

## 2. Evaluator

| 缺陷 | 现状 | 影响 |
| --- | --- | --- |
| 未做容器级网络隔离 | 依赖安装使用 `pip install --no-index`，但运行时没有防火墙/容器隔离 | submission 理论上仍可 `requests` 等出站；反投机靠 forbidden import 与测试，不靠防火墙 |
| 依赖本机 pip cache | 非空 `requirements.lock` 用 `--no-index` 安装 | 干净机器/Docker 若未预置 wheel（如 `text-unidecode`）会装依赖失败 |
| venv 复用宿主机 site-packages | `venv --system-site-packages`；**pytest 已改为显式安装**（`pytest==7.4.4`） | 任务依赖仍可能走 system-site-packages；Docker eval 镜像更干净 |
| 临时 venv 路径 | 每次 eval 在 `/tmp/featureliftbench-eval-*` 建 venv | 正常但不可复现调试同一 venv；日志里只有路径快照 |
| 历史 suite 可能含 eval flake | 修复前并行 eval 偶发 `No module named pytest` | 用 `reeval_suite.py` 重算；`analyze_benchmark_suite.py` 标 `eval_flake` |
| pytest 无内存沙箱 | Agent 自测与最终 eval 都会执行 untrusted submission；当前只有限时，没有 per-process memory/cgroup 上限 | 2026-06-27 观察到 Linux OOM killer 杀死 `pytest`，单进程 RSS 可达数百 GB；需给 agent/eval 的 pytest 加内存上限 |
| 无代码相似度 / 来源约束 | 只测行为 + LOC 比例 | Agent 可重写窄实现或通过大量无关代码投机（靠 hidden tests 部分遏制） |
| Oracle / Copy-All 无统一 CLI | `featureliftbench/baselines/` 未实现 | baseline 靠手工 submission + `eval`，`submissions/` 目录基本空置 |

## 3. Benchmark 任务与评分

| 缺陷 | 现状 | 影响 |
| --- | --- | --- |
| 任务规模 | 主榜 **50 hard** + smoke **3**（`benchmark/sanity/`） | 规模已扩至目标；单题仍影响 suite 比例 2% |
| Functional 校准未达标 | Flash-50 **41/50 (82%)** functional pass | 目标 ~20–30%；copy-all 路径 + hidden 偏软导致 functional 偏高 |
| Entangled 覆盖 | 含 sqlparse/coverage/jinja2/pytest 多题同库及策展 `vibe_app` | 缠绕类型仍待结合 Agent 失败模式继续校准 |
| 缠绕类型标注未校准 | metadata 已有 `entanglement.level/types/signals`，但当前标注主要来自人工静态判断 | 后续需要结合 Manual Oracle Closure、Agent 失败模式和 hidden tests 覆盖来校准 |
| Hard 任务区分度不足（解耦维度） | Flash-50：9/41 passed 题 extraction≥0.8；marshmallow/typer/markdown_it 等仍 copy-heavy pass | functional pass 高不等于解耦强；须看 `final_score` 与 high-extraction pass 占比 |
| 难度标签未充分校验 | `difficulty` 在 metadata 中为人工标注 | 与真实 oracle closure 可能有偏差 |
| 任务规范曾落后于 hidden tests | `tomlkit` 等曾出现 public/metadata 未写清、hidden 已测的行为 | Agent 易在 hidden 上失败；全量审计见 [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) |
| `metadata.output.import` 偏窄 | 约 8 题测试需要的符号/子模块未写在 `output.import` | Agent 按 output 做最小实现时 hidden 挂；entrypoints 往往更全 |
| Agent 指令（TASK.md）缺工作流 | 未强调 forbidden import gate、hidden 更严、跑 public pytest | public 过即 submit；与 spec 缺口叠加 |
| 无 property-based hidden tests 系统化 | 多为手写用例 | 存在硬编码通过 public 的空间（README 反投机规则尚未全自动化检测） |
| `scoring_reference` 未参与自动评分 | 字段存在，evaluator 不用 | Copy-All / Oracle 参考值仅供人工对比 |
| 无 Rewrite Track 隔离 | 仅 Decoupling / Extraction Track 跑通 | 无法区分「解耦已有代码」与「按说明重写」 |

## 4. 实验与结果口径（已跑 suite）

### 4.1 两轮 10 条 suite 不可直接当公平模型对比

| Run | 模型配置 | API | Passed | Avg `final_score` |
| --- | --- | --- | --- | ---: |
| `deepseek-v4-pro-suite-10-hard-001` | `openai//data1/models/llm/DeepSeek-V4-Pro` | 内网 OpenAI-compatible router | 10/10 | 0.407 |
| `deepseek-v4-flash-suite-10-hard-001` | `deepseek/deepseek-v4-flash` | 官方 `https://api.deepseek.com/v1` | 9/10 | 0.346 |

**缺陷**：endpoint、模型名格式、路由延迟/配额不一致；Flash 失败 `jsonschema` 不能单独归因于「模型更弱」，也可能是解耦不完整。

### 4.2 全量 28 题 baseline（DeepSeek V4 Flash）

| Run | 模型 | Passed | Avg `final_score` | 备注 |
| --- | --- | --- | ---: | --- |
| `benchmark-28-deepseek-flash-003` | `deepseek/deepseek-v4-flash` | 19/28 | 0.407 | `--yolo`，4 workers；见 [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) |

失败 9 题：8 题 public 过、hidden 或 forbidden import 挂；pytest 族 0/3。

### 4.3 已观测失败模式

* **Flash `jsonschema__validator_core__001`**（10-hard suite）：public 过、hidden 挂。
* **高 LOC 提交仍可通过功能门控**：多条 hard 任务 `final_score < 0.1` 但 `functional_gate = 1`。
* **click forbidden import**：public/hidden 全过但 `original_import_pass=false`（整题 failed）。

### 4.4 用量汇总口径

* 新 `run-agent` 结果会在单条 `run.json` 写 `agent.usage`，并在 suite 根目录 `suite.json` 写 `agent_usage_totals`。
* `experiments/mini-swe-agent/*/agent_usage.{json,md}` 与 `suite-comparison.*` 是已有实验的额外聚合报告；新 suite 若需要跨模型对比仍需单独生成对比报告。

### 4.5 本地 vLLM 与 SiliconFlow API（2026-06-26）

| 设置 | Functional pass | 说明 |
| --- | ---: | --- |
| Flash-50（官方 API baseline） | 41/50 (82%) | [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) |
| GPT-OSS-120B vLLM（3-run mean） | ~6.3/50 | [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) §3 |
| Qwen3-Coder-30B vLLM（3-run mean） | ~7.0/50 | 同上 |
| GLM-5.2 SiliconFlow（run1 进行中） | 2/50（部分） | ~¥5–6/题；全量估算 ¥250–300 |

**缺陷**：endpoint、missing_submission 率、eval harness 版本均不同；不可与 Flash-50 直接排名对比。

### 4.6 pytest OOM 事故（2026-06-27）

**现象**：服务器内核日志显示多次：

```text
Out of memory: Killed process ... (pytest)
```

被杀进程名是 `pytest`，不是 vLLM 服务。部分 `pytest` 的 RSS 达数十 GB 到数百 GB，说明内存峰值来自测试执行阶段。

**具体行为链路**：

1. Agent 生成不可信的 `submission/featurelifted/`。
2. Agent 自测或 harness eval 启动 `pytest public_tests/` / `pytest hidden_tests/`。
3. `pytest` import 并执行 submission 代码。
4. 某些错误实现触发无限递归、无限循环追加、parser 不消费输入、指数级数据结构膨胀、错误目录遍历或反复加载数据。
5. 因当前只有 timeout、没有内存上限，单个 `pytest` 可以持续申请内存，最终由 Linux OOM killer 杀掉。

**证据与限制**：

- OOM 截图只记录 pid 与进程名 `pytest`，没有 cwd/argv，无法 100% 反推出唯一 task。
- `eval/result.json` 中未必能看到 `returncode=-9`：若系统 OOM 在 agent 自测阶段或 harness 来不及写结果时发生，结果文件会缺失或只留下不完整 task 目录。
- MiniMax run1 在 `vibe_app__csv_transform_core__001` 停在无 `run.json` / 无 `trajectory.json` 的状态，和系统级中断特征一致，但不能单独证明该题就是唯一触发点。

**短期规避**：

- 正式实验先用 `NUM_WORKERS=1`，避免多个 pytest 同时失控。
- 不要同时跑多个 suite 或多个本地 vLLM 模型。
- 临时用 shell `ulimit -v` 包住 `./run.sh`，让 agent 自测继承内存上限。

**待修方向**：

- 在 harness 中增加 `AGENT_MEMORY_MB` / `EVAL_MEMORY_MB`，对 mini 子进程与 evaluator pytest 分别设置内存上限。
- 最终 eval 推荐 Docker/cgroup：`--memory` / `--memory-swap` 限制 untrusted submission。
- 将内存超限归档为明确状态（如 `resource_limit_exceeded`），避免被误判为普通 test fail 或 missing submission。

## 5. 仓库与文档

| 缺陷 | 现状 |
| --- | --- |
| 无 Docker / CI 一键复现 | 已有 `docker/Dockerfile.eval` + `.github/workflows/eval-oracles.yml`；Agent 仍本机跑 | 官方 baseline eval 推荐 Docker 或 pinned local evaluator |
| License / 引用占位 | README「Coming soon」 |
| 设计文档仍很轻 | 已建立 `docs/task_designs/` 并完成第一条 `sqlparse` hard-plus 设计；更完整的方法论和任务构造规范仍分散在 README / TODO / 本文 |
| 大量 `experiments/` 与 `.pytest_cache` 在仓库内 | 体积大；experiments 为 gitignore 的本地 run |

## 6. 安全与运维

* **`.env` 存 API key**：已在 `.gitignore`；密钥不应写入 `run.json` / `suite.json`，只记录 `api_key_present` 这类无密钥摘要。
* **用户在聊天/文档中粘贴 key 的风险**：需靠轮换 key，仓库侧无法防止。
* **Cursor 等 IDE 内长跑 agent**：可能触发环境 usage limit；与项目 bug 无关，但会阻断 suite。

## 7. 建议的修复优先级（非承诺）

当前重心：**把 50 hard 主榜做扎实**（见 [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)）。本地 vLLM 与 SiliconFlow API 实验汇总见 [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md)。

1. **P0（benchmark spec）**：补 5 题 `metadata.output.import`；全题 oracle `eval` 回归。
2. **P1（agent 指令）**：`TASK.md` 工作流 + forbidden import / hidden 提示。
3. **P2（safety）**：给 agent 自测与 evaluator pytest 增加内存沙箱（`AGENT_MEMORY_MB` / `EVAL_MEMORY_MB` 或 Docker/cgroup），防止 untrusted submission OOM 宿主机。
4. **P3（harness）**：全局 TPM 节流；`analyze_benchmark_suite` 跨 run 对比。（429 重试见 `RETRY_RATE_LIMIT`；续跑见 `--resume` / `EXTRA_AGENT_PASSES`）
5. **P4（infra）**：evaluator 离线 wheel；baselines CLI；Agent 容器化（eval 容器已提供）
6. **暂缓**：网络隔离；代码相似度约束。（扩题至 50 hard 已完成）

## 8. 相关文件

* 用量汇总：新 run 的 `run.json` / `suite.json`，以及历史 `experiments/mini-swe-agent/*/agent_usage.md`
* 模型对比：`experiments/mini-swe-agent/suite-comparison.md`
* 逐步轨迹：`experiments/mini-swe-agent/<suite>/<task>/agent/trajectory.json`
* 评测日志：`experiments/mini-swe-agent/<suite>/<task>/eval/logs/`
* **Benchmark 现状与待修清单**：[BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)
