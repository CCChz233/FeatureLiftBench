# FeatureLiftBench 已知缺陷与限制

本文档记录 **pilot 阶段已确认** 的工程缺口、评测局限和实验口径问题。FeatureLiftBench 的长期目标是评估 Agent 能否从 vibe/legacy/entangled 仓库中完成功能级解耦；与 [README.md](README.md) 中的研究性「待讨论问题」不同，这里侧重当前实现里 **已经观察到** 的限制。

最后更新：2026-07-01（OpenHands 跑批踩坑见 [OPENHANDS_RUN_PITFALLS.md](OPENHANDS_RUN_PITFALLS.md)）

## 1. Agent Harness

| 缺陷 | 现状 | 影响 |
| --- | --- | --- |
| Suite 并行 API 限流 | `--retry-rate-limit N` 遇 429 等 ~65s 后重试；无全局 TPM 节流 | SiliconFlow 等 API 建议 `NUM_WORKERS=1`、`RETRY_RATE_LIMIT=5`；勿多模型共 key 并行 |
| 进度与 token 显示 | Rich Live 轮询 `stdout.log` + `trajectory.json`；默认经 `mini_live_runner` **每步写 trajectory** | mini stdout 仅显示 `$0.00` 不显示 token；旧 run 或未重启 harness 可能仍 `0 toks` |
| 断点续跑 | `--resume` 同目录续跑；保留非 retry 状态题，重跑 `missing_submission` / `failed` 等 | 每题增量写 `suite.json` checkpoint；无 `suite.json` 时扫各题 `run.json` fallback |
| misplaced submission | `_recover_misplaced_submission` 从 `workspace/featurelifted/` 等路径回收 | 2026-06-26 前旧 run 无 `recovered_submissions` 字段 |
| 用量 / token | `run.json` / `suite.json` 从 `trajectory.json` messages 聚合 prompt/completion | SiliconFlow 上 cost 常为 0（`MSWEA_COST_TRACKING=ignore_errors`） |
| 不记录 dollar cost | litellm 对多数 API 模型无定价表 | 只记录 token、API call、step；API 费用需按平台单价自行估算 |
| 环境强依赖本机路径 | `agents.toml` / `.env` 不进 Git；`./setup.sh` 会生成并 patch `agent_bin` | 见 [SETUP.md](SETUP.md) |
| Agent 接入仍需逐个验证 | 已内置 `mini-swe-agent`、`featurelift-agent`、`openhands-agent`、`command` | OpenHands 真实 headless 命令和逐调用 token 审计仍需按所选 runtime 验证；无法验证时标 `usage_unverified=true` |
| mini batch 必须 `--yolo` | 默认 confirm 模式会在 `Execute?` 处阻塞非交互 subprocess | `run-agent` 须加 `--yolo` 或改 mini 配置 |

## 2. Evaluator

| 缺陷 | 现状 | 影响 |
| --- | --- | --- |
| 未做容器级网络隔离 | 依赖安装使用 `pip install --no-index`，但运行时没有防火墙/容器隔离 | submission 理论上仍可 `requests` 等出站；反投机靠 forbidden import 与测试，不靠防火墙 |
| 依赖本机 pip cache | 非空 `requirements.lock` 用 `--no-index` 安装；`benchmark/vendor-wheels/` + `bootstrap_vendor_wheels.py` 提供离线 wheel | 干净机器/Docker 需先 bootstrap vendor wheels 并 rebuild eval/agent 镜像 |
| venv 复用宿主机 site-packages | `venv --system-site-packages`；**pytest 已改为显式安装**（`pytest==7.4.4`） | 任务依赖仍可能走 system-site-packages；Docker eval 镜像更干净 |
| 临时 venv 路径 | 每次 eval 在 `/tmp/featureliftbench-eval-*` 建 venv | 正常但不可复现调试同一 venv；日志里只有路径快照 |
| 历史 suite 可能含 eval flake | 修复前并行 eval 偶发 `No module named pytest` | 用 `reeval_suite.py` 重算；`analyze_benchmark_suite.py` 标 `eval_flake` |
| pytest 资源边界 | 正式 eval 用 Docker memory/cpu/pids/log/network/read-only mount；eval 外层 wall-clock 超时默认 600s（`FEATURELIFTBENCH_DOCKER_EVAL_TIMEOUT_SECONDS`） | 完整规格见 [SETUP.md](SETUP.md) §4；论文结果应使用 Docker eval 口径 |
| 无代码相似度 / 来源约束 | 只测行为 + LOC 比例 | Agent 可重写窄实现或通过大量无关代码投机（靠 hidden tests 部分遏制） |
| Oracle / Copy-All 无统一 CLI | `featureliftbench/baselines/` 未实现 | baseline 靠手工 submission + `eval`，`submissions/` 目录基本空置 |

## 3. Benchmark 任务与评分

| 缺陷 | 现状 | 影响 |
| --- | --- | --- |
| 任务规模 | 主榜 **100 hard**（batch-0 五十题冻结 + batch-1 新增五十题）+ smoke **3** | batch-1 经 staging 新增，见 [EXPANSION.md](EXPANSION.md) |
| Functional 与解耦判别 | Flash-50 **41/50 (82%)** functional pass | 难度可再评估；判别靠 **final_score** + high/compact extraction 分层 |
| Entangled 覆盖 | 43 OSS + 7 策展 `vibe_app` | 论文应分层报告；vibe_app 为 legacy 应力非真实 PyPI 库 |
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

**Canonical doc：** [SETUP.md](SETUP.md) §4（威胁模型、默认配置、结果解读、实验 checklist）。

**现象**：服务器内核日志多次 `Out of memory: Killed process ... (pytest)`；单进程 RSS 可达数百 GB。MiniMax run1 等 suite 出现半截 task（无 `run.json`），与系统级 OOM 一致。

**当前缓解**：正式实验使用 Docker 边界：`FEATURELIFTBENCH_EVAL_DOCKER=1` 限制 submission/pytest 的内存、CPU、进程数、日志和网络；`FEATURELIFTBENCH_AGENT_DOCKER=1` 限制 agent 可见/可写的宿主文件范围。`run.sh` 仍保留本地 `EVAL_MEMORY_MB` / `AGENT_MEMORY_MB` 作为非 Docker 调试兜底。eval 结果字段包含 `resource_limited`、`log_limit_exceeded`、`docker_sandbox_error`。

**仍待办**：跑完整主榜 Docker oracle 验收；分析脚本/论文表格中把 resource/log/sandbox failure 与普通 functional failure 分开报告。

## 5. 仓库与文档

| 缺陷 | 现状 |
| --- | --- |
| 无 Docker / CI 一键复现 | 已有 `docker/Dockerfile.eval`、`docker/Dockerfile.agent`、`.github/workflows/eval-oracles.yml` | 官方 baseline eval 推荐 Docker；agent Docker 用于长跑/共享机器/外部 agent |
| License / 引用占位 | README「Coming soon」 |
| 设计文档仍很轻 | 已建立 `docs/task_designs/` 并完成第一条 `sqlparse` hard-plus 设计；更完整的方法论和任务构造规范仍分散在 README / TODO / 本文 |
| 大量 `experiments/` 与 `.pytest_cache` 在仓库内 | 体积大；experiments 为 gitignore 的本地 run |

## 6. 安全与运维

* **`.env` 存 API key**：已在 `.gitignore`；密钥不应写入 `run.json` / `suite.json`，只记录 `api_key_present` 这类无密钥摘要。
* **用户在聊天/文档中粘贴 key 的风险**：需靠轮换 key，仓库侧无法防止。
* **Cursor 等 IDE 内长跑 agent**：可能触发环境 usage limit；与项目 bug 无关，但会阻断 suite。

## 7. 建议的修复优先级（非承诺）

当前重心：**batch-0 五十题已闭环**；**batch-1 +50** 进行中（见 [EXPANSION.md](EXPANSION.md)）。实验汇总见 [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md)。

1. **P0（official run）**：用 agent Docker + eval Docker 跑 Flash / Pro 完整主榜，保存可复现产物。
2. **P0（official eval）**：Docker oracle 全量验收，确认 eval image 依赖闭包和资源边界。
3. **P0（task gate）**：`audit_output_imports.py --fail-on-gap` 作为 staging 和 promote 硬门，防止 batch-1 重复早期 L1 缺口。
4. **P1（扩题）**：按 [EXPANSION.md](EXPANSION.md) 从 starter idea → shortlist → staging pilot → batch-1 **+50**；batch-0 不修改。
5. **P1（experiments）**：多模型主榜 run 继续；分析时把 OOM / resource / log / sandbox failure 与模型功能失败分开。
6. **P2（harness）**：全局 TPM 节流；`analyze_benchmark_suite` 跨 run 对比；baselines CLI；evaluator 离线 wheel。
7. **暂缓**：公开 hostile sandbox、代码相似度约束、Go v2 扩题、替换 batch-0 弱题。

## 8. 相关文件

* 用量汇总：新 run 的 `run.json` / `suite.json`，以及历史 `experiments/mini-swe-agent/*/agent_usage.md`
* 模型对比：`experiments/mini-swe-agent/suite-comparison.md`
* 逐步轨迹：`experiments/mini-swe-agent/<suite>/<task>/agent/trajectory.json`
* 评测日志：`experiments/mini-swe-agent/<suite>/<task>/eval/logs/`
* **Benchmark 现状与待修清单**：[BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)
