# FeatureLiftBench 论文大纲（草案）

**标题（暂定）：** FeatureLiftBench: Can Code Agents Decouple Features from Entangled Repositories?

**最后更新：** 2026-06-29

本文档是论文写作的**主大纲**，整合了 benchmark 定义、与 SWE-bench 的差异、创新点、实验口径，以及基于真实 agent 轨迹的失败模式分析。

---

## 0. 电梯演讲（30 秒）

给定一个**能跑但结构缠绕**的 Python 仓库，Agent 能否把**某个已有功能**抽成**独立可安装、可测试**的小包，且**行为不变**？

- **不是** SWE-bench 的 issue → patch
- **是** 固定仓库 + 功能规格 → 新 package（`featurelifted/`）
- **不只问** 测试过没过，还问 **抄了多少代码**（extraction）

---

## 1. Benchmark 有什么用

### 1.1 在评测里

| 作用 | 说明 |
| --- | --- |
| 补 SWE 缺口 | SWE-bench 测修 bug / 打 patch；FeatureLiftBench 测 **从乱仓库里抽功能** |
| 双维评分 | Functional Gate + Extraction Ratio，区分「会抄」和「会抽」 |
| 可复现榜单 | 100 题、Docker 协议、hidden tests、forbidden import |

### 1.2 在实际工程里

| 场景 | 在测什么 |
| --- | --- |
| Legacy 迁移 | 从 monolith 抽出 parser/validator，不能再 import 原包 |
| Vibe coding 收尾 | Demo 能跑，但要抽可复用模块给别的项目 |
| 内部库化 | 从大 repo 抽 config loader、rules engine 当独立包 |
| Agent 产品选型 | 评估 coding agent 在 hidden 边界、import 约束上是否可靠 |

**不直接解决：** 自动 refactor 上线（这是评测，不是产品）；不保证架构最优（只保证行为 + 大致体量）。

---

## 2. 任务是什么

### 2.1 单题形式

**给定：**

- 固定 commit 的 `repo/` 快照（如 httpx、pytest、pydantic…）
- 功能规格：`metadata.feature`（包含/排除哪些行为）
- Agent 可见 `public_tests/`；**hidden tests 评测时才跑**

**要求交付：**

- `submission/featurelifted/` 独立 Python 包
- 行为兼容原实现中该功能切片
- **运行时禁止** `import httpx` 等原包名或依赖原仓库路径

**例题（`httpx__request_model_core__001`）：** 抽出 URL、Headers、Request 等**离线请求模型**，不要网络 I/O、Client.send、连接池。

### 2.2 规模与结构

| 项 | 内容 |
| --- | --- |
| 规模 | **100 道 hard**（batch-0 五十题冻结 + batch-1 新增五十题） |
| 语言 | Python |
| 来源 | 43 题 pinned OSS + 7 题策展 `vibe_app` |
| 缠绕标注 | `entanglement.primary`：parser_state、framework、config_environment 等 |
| 目录 | `metadata.json`、`repo/`、`public_tests/`、`hidden_tests/`、`evaluation/` |

---

## 3. 与 SWE-bench 的区别

| 维度 | SWE-bench 等 | FeatureLiftBench |
| --- | --- | --- |
| 任务来源 | GitHub issue / PR | 功能规格 + 固定仓库快照 |
| 要做什么 | 修 bug、实现需求 | **从已有代码里抽出**一块功能 |
| 输出形态 | **Patch / PR** | **新 package** |
| 成功标准 | 测试过即可 | 测试过 + **不能依赖原包** + 鼓励代码尽量小 |
| 难度来源 | 定位 + 改对几行 | **Closure 规划**：跨模块、改 import、去框架耦合 |
| 测试设计 | issue 自带测试 | **public + hidden**；hidden 更严 |
| 反投机 | 相对弱 | forbidden import、禁止原包依赖、copy-all baseline |

**直觉：**

- SWE-bench → 「这个 issue 修好了吗？」
- FeatureLiftBench → 「这块功能能不能干净地拆出来给别人用？」

---

## 4. 创新点（Contributions）

1. **任务范式**：从 issue resolution 扩展到 **behavior-preserving feature-level decoupling**。
2. **双维评分**：Functional Gate + Extraction Ratio → Final Score；pass 不含 extraction，专门用来区分解耦质量。
3. **出题质量控制（batch-1）**：oracle / naive / copy-all / Flash 校准 gate，避免无判别力的题进榜。
4. **缠绕类型标注**：按 entanglement 分析 Agent 在不同耦合形态上的弱点。
5. **工程化复现协议**：agent/eval 双 Docker、eval 外层超时、suite 锁、增量 checkpoint；基础设施失败与功能失败分开报。

---

## 5. 评分与实验口径

### 5.1 指标

- **Functional Gate** \(G\)：install + import + public/hidden pytest + forbidden import → 0 或 1
- **Extraction Ratio** \(E\)：submission LOC / repo LOC（越小越像「抽出来」）
- **Final Score** \(S = G \times (1 - E)\)

**Pass** 只看 \(G\)；\(S\) 和 extraction 分层用来区分解耦质量。

**Suite 报告建议并列：**

| 指标 | 含义 |
| --- | --- |
| functional pass rate | 主 headline |
| average final_score | 辅 |
| high-extraction pass（\(E \ge 0.8\) 且 pass） | copy-heavy 成功 |
| compact pass（\(E \le 0.25\) 且 pass） | 强解耦成功 |
| missing_submission / docker_sandbox_error | 运行质量，非模型能力 |

### 5.2 正式跑法

- Agent：**mini-swe-agent**，`--yolo`
- 正式实验：**`--agent-docker` + `--eval-docker`**
- `NUM_WORKERS=1` 串行；`RETRY_RATE_LIMIT=5`
- 产物：`suite.json`、每题 `run.json`、`eval/result.json`

```bash
./run-batch1-docker-flash.sh          # batch-1 五十题
RESUME_DIR=experiments/.../run_id ./run-batch1-docker-flash.sh
./run.sh                              # 完整一百题
```

详见 [SERVER_DEPLOY.md](SERVER_DEPLOY.md)。

---

## 6. 研究问题（RQs）

| RQ | 问题 |
| --- | --- |
| **RQ1** | 强 Agent 的 functional pass rate 是多少？ |
| **RQ2** | functional pass 与解耦质量（final_score / compact pass）是否一致？ |
| **RQ3** | 失败主要来自 hidden、forbidden import、missing submission，还是 eval 基础设施？ |
| **RQ4**（可选） | 不同 entanglement 类型上的 pass rate / extraction 有何差异？ |

---

## 7. 实验结果（已有数据）

### 7.1 数据来源

| Run | 协议 | 用途 |
| --- | --- | --- |
| `benchmark-50-hard-flash-001` | 本地 agent + eval，4 workers | **Pilot** |
| `benchmark-50-hard-pro-20260625-125553` | 同上（re-eval 后） | **Pilot** |
| `benchmark-batch1-flash-docker-*` | Docker agent + eval | **Official（进行中）** |

### 7.2 Pilot：Flash / Pro on batch-0（50 hard）

| 指标 | Flash | Pro |
| --- | ---: | ---: |
| Functional pass | **41/50 (82%)** | **42/50 (84%)** |
| Avg final_score | 0.472 | 0.481 |
| High-extraction pass（≥0.8，在 passed 内） | 9/41 | 9/42 |
| Compact pass（≤0.25，在 passed 内） | 16/41 | 16/42 |
| Head-to-head | 39 双过 · 6 双挂 · 2 仅 Flash · 3 仅 Pro | |

**解读：** Pro 仅略高；两者 functional pass **远高于** 早期校准目标 ~20–30%。判别力在 **extraction / final_score**，不在 pass rate。

### 7.3 Pilot：失败题清单（Flash，9 题）

全部 9 题失败模式一致：**public ✅，hidden ❌**（无 forbidden import 失败、无 missing submission）。

`networkx__dag_topo_core__001`，`pygments__lexer_core__001`，`pytest__fixture_resolve_core__001`，`pytest__ini_markers_core__001`，`pytest__skipif_eval_core__001`，`rich__markup_parse_core__001`，`vibe_app__orm_query_ast_core__001`，`vibe_app__rules_engine_core__001`，`vibe_app__session_registry_core__001`

### 7.4 Pilot：Copy-heavy pass 示例（Flash）

| 题 | extraction | final_score |
| --- | ---: | ---: |
| marshmallow__schema_core__001 | 0.987 | 0.013 |
| typer__command_parser_core__001 | 0.977 | 0.023 |
| lark__parse_tree_core__001 | 0.921 | 0.079 |
| click__option_parser__001 | 0.844 | 0.156 |

### 7.5 Official：batch-1 Docker Flash（早期，6 题）

| 题 | 结果 | 备注 |
| --- | --- | --- |
| arrow / astroid / bidict / bleach | failed | 多题 public+hidden 均未过，部分 build 不过 |
| boltons / cachetools | failed | eval docker OOM / 挂死（infra） |

**论文主表建议：** batch-1 + Docker 全量；batch-0 作 pilot 对照，并说明协议差异。

---

## 8. Agent 轨迹分析：主要缺陷

> 依据：`benchmark-50-hard-flash-001` 全部 50 题 trajectory + eval；batch-1 Docker 前 6 题。

### 8.1 失败模式分布（Flash-50）

| 模式 | 数量 | 说明 |
| --- | ---: | --- |
| Public 过、Hidden 挂 | **9** | **全部** functional fail 都是此模式 |
| Copy-heavy pass（≥0.8） | 9/41 passed | functional 过但几乎整库抄 |
| Compact pass（≤0.25） | 16/41 passed | 真正抽紧了 |
| Forbidden import 挂 | 0 | Agent 会 grep，很少留原包 import |
| Missing submission | 0 | 基本都会交卷 |

### 8.2 缺陷 1：把解耦题当修 bug 题做

mini 默认模板仍是 SWE 工作流（复现 issue → 改源码 → 验证 → submit）。Agent 行为：`grep` / `sed` / `head` 大文件，而非：

1. 画 **closure**（要哪些文件、哪些依赖）
2. **批量 copy + 系统改 import**
3. 对照 **Required Output API** 查漏

### 8.3 缺陷 2：Public 驱动，Hidden 盲飞（最致命）

`pytest__fixture_resolve_core__001` 轨迹典型：

- TASK.md 已警告 hidden 更严
- Agent 跑通 `pytest public_tests/` 后认为「implementation looks good」→ 直接 `COMPLETE_TASK_AND_SUBMIT`
- Eval：public ✅，hidden ❌

Agent **不会在 workspace 里模拟 hidden 强度**，也没有提交前 checklist。

### 8.4 缺陷 3：默认 Copy-All，不是 Minimal Closure

`marshmallow__schema_core__001` 推理中明确计划 copy schema.py、fields.py、utils.py、orderedset.py 等十余文件 → extraction **0.99**，functional pass，final_score **0.01**。

**根因：** copy + `sed` 改 import 比分析依赖图省事；**pass 门槛不看 extraction**，Agent 无动力抽紧。

### 8.5 缺陷 4：Closure 规划弱 — 两个极端

| 极端 | 例子 | 后果 |
| --- | --- | --- |
| 过薄 | pytest fixture（205 LOC，extraction 0.003） | public 过，hidden 挂 |
| 过厚 | marshmallow / lark / typer | functional 过，final_score ≈ 0 |
| 探索烧 token | pygments formatter **634 万 tokens** | 在大 repo 里打转 |

### 8.6 缺陷 5：Framework / 全局状态题几乎无解

稳定失败簇：

- **pytest 族 3/3 挂**：fixture 绑 Session、FixtureManager、plugin 体系
- **vibe_app 3/4 挂**：ORM AST、rules engine、session registry
- **networkx / pygments / rich**：组合 hidden / 状态机

Agent 常写**窄 API 壳**，未带上框架/registry/scope 语义。

### 8.7 缺陷 6：Harness 交互浪费步数

轨迹中大量 `Please always provide EXACTLY ONE action` 格式纠错（marshmallow 49 步内多次），有效写码步数被吃掉。

### 8.8 Agent 擅长 vs 不擅长

| 擅长 | 不擅长 |
| --- | --- |
| 探索 repo、grep、读大文件 | 系统做 closure 规划 |
| Copy 源码 + 批量改 import | 删到真正 minimal |
| 让 public tests 绿 | 猜 hidden 边界、组合行为 |
| 避免 forbidden import | 框架/插件/全局状态解耦 |
| 简单切片 compact pass（coverage、faker） | vibe/legacy 策展题、pytest 内核题 |

### 8.9 对论文 Discussion 的要点

1. **82% pass 说明「能抄能改 import」，不说明「会解耦」** — 必须报 compact / high-extraction 分层。
2. TASK.md 警告 hidden **不够** — 需要 agent 侧 hidden-aware 策略或专用 workflow prompt。
3. mini 的 SWE 模板与解耦任务 **不对齐** — 值得换 adapter / prompt。
4. Pass 不含 extraction → Agent **理性选择 copy-all** — 这是 benchmark 设计的有意 trade-off，论文里要说清。

---

## 9. 论文结构（章节草案）

### 1. Introduction

- 动机：vibe code / legacy / 内部库化
- RQ1–RQ4
- 贡献（§4 五条）
- 主要发现预告：pass 高、解耦弱；hidden 是主 discriminator

### 2. Related Work

- SWE-bench、RepoBench、HumanEval 等
- 模块化 / refactoring metrics
- Agent 沙箱评测

### 3. Task Definition

- 输入 / 输出 / Decoupling track
- 与 SWE-bench 对比表（§3）
- 例题（httpx request model）

### 4. Benchmark Construction

- batch-0 冻结 + batch-1 staging promote → 100 hard
- entanglement 标注、public/hidden 设计
- Quality gates：oracle / naive / copy-all / Flash 校准
- 一张 pipeline 图：backlog → staging → gates → promote

### 5. Evaluation Methodology

- Evaluator 流程
- 评分公式（§5.1）
- Docker 边界与复现要求
- Agent 协议（mini-swe-agent + Docker）

### 6. Experiments

- 设置：Flash / Pro；pilot vs official 分层
- **Table 1**：主结果（pass + final_score + extraction 分层）
- **Table 2**：失败模式 taxonomy（§8.1）
- **Figure**：extraction vs final_score 散点（passed 题）
- 可选：按 entanglement 分组

### 7. Agent Behavior Analysis

- 轨迹方法（trajectory.json + eval result.json）
- §8.2–§8.8 缺陷归纳
- 案例：`pytest__fixture_resolve_core__001`（hidden 挂）、`marshmallow__schema_core__001`（copy-heavy pass）

### 8. Discussion

- Functional pass 高 ≠ 解耦强
- Benchmark 设计 trade-off（pass vs extraction）
- 工程教训：Docker eval、OOM、eval 超时
- 局限（§10）

### 9. Conclusion

- 问题、benchmark、主要发现、未来工作

### Appendix

- A：100 题列表
- B：metadata schema / TASK_FORMAT
- C：Gate rubric（G0–G6）
- D：Docker / env 变量
- E：Pilot（batch-0）与 Official（batch-1 Docker）协议差异
- F：代表性 trajectory 片段

---

## 10. 图表清单

| # | 类型 | 内容 |
| --- | --- | --- |
| 1 | Fig | SWE-bench vs FeatureLiftBench 范式对比 |
| 2 | Fig | 端到端 pipeline（repo → agent → eval → scores） |
| 3 | Fig | batch-1 curation pipeline（staging → gates → promote） |
| 4 | Table | Benchmark 统计（100 题、entanglement、测试数） |
| 5 | Table | 主结果 Flash vs Pro（pass + final_score + 分层） |
| 6 | Table | 失败模式 taxonomy |
| 7 | Fig | extraction vs final_score 散点 |
| 8 | Fig | 按 entanglement 的 pass rate（可选） |

---

## 11. 局限与未来工作

| 局限 | 说明 |
| --- | --- |
| 仅 Python | Go v2 规划中 |
| LOC extraction 粗糙 | 可被无关代码 / 重写窄实现投机 |
| Pass 不含 extraction | 有意设计；须报 final_score 分层 |
| Hidden 平均偏少 | 部分题挡不住 copy-all |
| mini SWE 模板 | 与解耦 workflow 不对齐 |
| 无 rewrite track | 无法区分「抽」vs「重写」 |
| Pilot 与 Official 协议不一 | 论文须分表/report |

**未来：** hidden-aware agent、专用 prompt/adapter、property-based hidden、baselines CLI、多语言扩展。

---

## 12. 当前进度（写论文时对照）

| 项 | 状态 |
| --- | --- |
| 100 题定义 + GitHub | ✅ |
| batch-0 Flash/Pro pilot 结果 | ✅（本地 agent+eval，作对照） |
| batch-1 Docker Flash 正式跑 | ⏳ 待服务器全量 |
| Docker 稳定性 harness | ✅ |
| Agent 轨迹分析（§8） | ✅ 基于 Flash-50 + batch-1 前 6 题 |

**建议叙事：**

> 100-task benchmark（结构完整）；**主表为 batch-1 50 hard + Docker 协议**；batch-0 50 为 pilot 历史对照。

---

## 13. 相关仓库文档

| 文档 | 用途 |
| --- | --- |
| [CONCEPTS.md](CONCEPTS.md) | 概念与流程 |
| [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) | 复现契约 |
| [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) | baseline 数字 |
| [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) | 历史实验表 |
| [SERVER_DEPLOY.md](SERVER_DEPLOY.md) | 服务器部署 |
| [BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) | 出题流程 |
| [limitations.md](limitations.md) | 已知局限 |
