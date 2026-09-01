# FeatureLiftBench 当前状态

> **Status: current · Last verified: 2026-08-30**
> 本文件是当前规模、release、可用结果和证据缺口的唯一手写事实源。

## Paper main suite（Python-200'）

论文主套件是 **冻结 Python-150 + Hard-50**，不是 150 + External-50。
Hard-50 **不得**写入 `benchmark/tasks/`。旧 E50 实体与历史分数保留，只作旁路。

| Item | Current value |
| --- | --- |
| Suite | `python200-hard-full-repository-no-hint-unreleased` |
| Task count | 200（150 + 50） |
| Repositories / snapshots | 176 / 182 |
| Baseline freeze | `846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd` |
| Hard-50 selection | `hard50-expansion-20260827-v1-reviewed` |
| Hard-50 release tree | `6b1cac758212…`（全哈希见 suite JSON） |
| Unified task root | `benchmark/python200_hard_tasks/` |
| Unified source registry | `benchmark/sources/python200_hard_registry.json` |
| Hard-50 packages | `benchmark/hard50/`（无 `reference_solution/`） |
| Paper table | **收到包的审计 headline 为 132/200（66.0%）**；仅 183 题启动，严格替换集合 84 题，不得写成最终冻结主表。 |

权威组合清单：
[`benchmark/selection/python200_hard_suite.json`](../benchmark/selection/python200_hard_suite.json)。
计划：[PLAN_HARD50_EXPANSION.md](PLAN_HARD50_EXPANSION.md)。
题集口径：[汇报_题集构成.md](汇报_题集构成.md)。

Hard-50 Flash 校准（functional_gate，不是 suite `status`）：

- Pilot 10：**4/10 = 40%**（换题后）
- 余 40：**25/40 = 62.5%**
- 6 道 copy-heavy 换题：**6/6** 功能过，通过解 RRES 约 0.10–0.72
- **合计 29/50 = 58%**（目标带 40%–65%）

2026-08-29 已收到 200 题 Flash 结果包，原始记录为 **132/200 = 66.0%**（Wilson 95%
59.2%–72.2%）；拆分为 Python-150 **103/150 = 68.7%**、Hard-50
**29/50 = 58.0%**。任务 ID 200/200 匹配，183 个有 source provenance 的运行全部
匹配 registry，Docker sandbox failures = 0。但这不是完整、合格的 200 题运行：只有
183 题启动 Agent；17 个 Python-150 任务在启动前因 active-spec/freeze hash mismatch
被挡住；16 个 Hard-50 任务因离线锁定依赖缺 wheel，尚未进入行为测试；另有 59 个
已启动运行触发 context-window audit（37 个功能通过）。三类问题去重后冻结为 **84 题
严格替换集合**；固定不动的 116 题中 95 题通过。因此 132/200 只能作为收到包的
**audit headline**，不能进摘要或最终主表。分析、证明和替换清单见
[`reports/paper_analysis/python200_hard_main_20260829/`](../reports/paper_analysis/python200_hard_main_20260829/)。

`run_python200_paper.sh` 仍指向旧 150+E50，且会跑 150 freeze check。新主表入口：

```bash
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main \
  --output experiments/<run-id> --docker --workers 1 --timeout 3600
```

等价写法：`--arm` 是 `--method` 的别名；也可显式传
`--tasks-root benchmark/python200_hard_tasks` 与
`--source-registry benchmark/sources/python200_hard_registry.json`。

工作区 `benchmark/tasks/` 相对 freeze artifact 有预先存在的 drift（约
95/150 unchanged），**不是** Hard-50 造成的，不要 revert。论文 150 分应对
freeze artifact，不要把脏工作树上的 150 分写成冻结主表。

## Superseded suite（150 + External-50）

下列 leaderboard 仍有效，但是 **旧 Python-200**
（`python200-full-repository-no-hint-20260801-v1`）。Flash 在 External-50 上
**90%–94%**，通过解 RRES 中位数贴 1.000。这些数字 **不得** 当作新主表，也不得
与 Hard-50 58% 混排。

| Item | Historical value |
| --- | --- |
| Unified suite | `python200-full-repository-no-hint-20260801-v1` |
| Task set SHA256 | `cee22c263a3c190e8b13b0c3c70d9fabac5c6c767010e5c21220f2c8c61bfa74` |
| External selection | `external50-expansion-20260801-v2` |
| Unified task root | `benchmark/python200_tasks/` |
| Unified source registry | `benchmark/sources/python200_registry.json` |

权威组合清单（旧）：
[`benchmark/selection/python200_suite.json`](../benchmark/selection/python200_suite.json)。
`artifacts/research_analysis/v3/current_benchmark_freeze.json` 仍是不可变的
Python-150 freeze，不把 External-50 或 Hard-50 写入该 freeze。

## Metric Contract

当前主结果只有两项核心指标：

1. **Functional Pass Rate**：`build ∧ public ∧ hidden ∧ isolation`。
2. **Reference-Relative Extraction Size (RRES)**：只在 Functional Pass 题上计算，越低越紧凑。方法对比必须用同题双方都通过的成对子集。

`final_score` 等于 `functional_gate`，不是额外指标。Tokens、steps、time 和 agent
completion 只是运行诊断。每道 Functional Fail 按 missing submission、build、public、
hidden、isolation 的首败阶段分类。完整定义见 [EVALUATION.md](EVALUATION.md)。

## Historical Python-200 Main Leaderboard（150 + External-50）

**不是论文新主表。** 条件：旧 suite 上 Full-Repository / No-Hint Main，120 步，
每题一次。指标来自逐题 `eval/result.json` 的 `functional_gate`，**不是**
`summary.passed` / `run.status`。这不是当前 [V1 = Main+2M](METHOD_V1.md)，也不是
旧 Lite V1 checker/repair 协议。新主表见上文 Paper main suite。

| 模型 | 端点 | Functional Pass | Pass Rate | Wilson 95% |
| --- | --- | ---: | ---: | --- |
| DeepSeek V4 Flash local vLLM | local | **145/200** | **72.5%** | 65.9%–78.2% |
| DeepSeek V4 Flash API | API | **144/200** | **72.0%** | 65.4%–77.8% |
| Qwen3.5 122B local vLLM | local | **96/200** | **48.0%** | 41.2%–54.9% |
| Qwen3.6 35B local vLLM | local | **95/200** | **47.5%** | 40.7%–54.4% |
| GPT-OSS 120B local vLLM | local | **43/200** | **21.5%** | 16.4%–27.7% |

| 模型 | Python-150 | External-50 | Python-200 |
| --- | ---: | ---: | --- |
| DeepSeek V4 Flash API | 99/150 (66.0%) | 45/50 (90.0%) | **144/200 (72.0%)** |
| DeepSeek V4 Flash local vLLM | 98/150 (65.3%) | 47/50 (94.0%) | **145/200 (72.5%)** |
| Qwen3.5 122B local vLLM | 59/150 (39.3%) | 37/50 (74.0%) | **96/200 (48.0%)** |
| Qwen3.6 35B local vLLM | 59/150 (39.3%) | 36/50 (72.0%) | **95/200 (47.5%)** |
| GPT-OSS 120B local vLLM | 27/150 (18.0%) | 16/50 (32.0%) | **43/200 (21.5%)** |

资格：

- Qwen3.5 / GPT-OSS：冻结 Python-150 整包 + 2026-08-17 External-50。
- Qwen3.6-35B：冻结 Python-150 三片（p8008 / p8020 / p8021）并集 + 同日 External-50。
- DeepSeek API：既有 150 + External-50；DeepSeek 本地：一次跑满 200。
- Agent / evaluator image 均钉在 `sha256:f328e2ce…` / `sha256:a491d620…`，五组均匹配。
- Qwen3.6-35B External-50 的 `run.status` 几乎全失败，但 Functional 仍按
  `functional_gate` 计（36/50）；不得用 `summary.passed`。
- 通过题的 RRES 中位数全部贴 1.000，主要来自 External-50 copy-heavy 解；跨模型
  RRES / token **不能**比紧凑度或成本。Qwen 122B 与 35B 的 Wilson 区间重叠，
  不能宣称 122B 高于 35B。

机器可读快照：
[`python200_cross_model_main_20260818.json`](../artifacts/research_analysis/current_results/python200_cross_model_main_20260818.json)。
组会表：[汇报_Python200跨模型Main.md](汇报_Python200跨模型Main.md)。
重建：

```bash
PYTHONPATH=harness python3 harness/scripts/merge_python200_main_results.py
```

## Current Method: V1

**V1 = Main 协议 + 2,000,000 total-token cap**（无 checker / structure-stop / repair）。
规范见 [METHOD_V1.md](METHOD_V1.md)。旧 Lite V1 协议已退役，只作历史对照。

Qwen3.6-35B Python-200 V1 已完成：**55/200（27.5%）**，约 329M tokens。不要与上表
Main 95/200 直接相减：c150 Main 与 V1 的 condenser / 日期不完全对齐。干净切片是
External-50 成对 n=46：Main 35 → V1 19。解释见 [FINDINGS.md](FINDINGS.md)，快照见
[`qwen_v1_vs_main_20260818.json`](../artifacts/research_analysis/current_results/qwen_v1_vs_main_20260818.json)。

DeepSeek API 全量 V1-200 **未跑**；Flash Core-12 诊断为 Main 8/12 → V1 4/12，不是
Python-200 通过率。不补跑 gpt-oss / 122B / 27B 的 V1-200。

## Current DeepSeek Method Comparison

下表是 **已完成的** DeepSeek Main vs **旧 Lite V1 协议**（checker + repair，
Main 预算 120 步），不是 45+10 Frozen 信封，也不是当前 V1。

| 端点 | 方法 | Functional Pass | Pass Rate | RRES | 成对 RRES Δ 中位数 |
| --- | --- | ---: | ---: | --- | ---: |
| API | Main | **144/200** | **72.0%** | 144/144，median 1.000 |  |
| API | Lite V1 | 131/200 | 65.5% | 131/131，median 1.000 | **0.000**（126 题） |
| 本地 vLLM | Main | **145/200** | **72.5%** | 145/145，median 1.000 |  |
| 本地 vLLM | Lite V1 | 127/200 | 63.5% | 127/127，median 1.000 | **0.000**（125 题） |

结论：Main 在 API 上领先 6.5 个百分点，在本地 vLLM 上领先 9.0 个百分点。Lite V1
省 token（API −50.3%，本地 −32.1%），但不提高正确率，也没有成对紧凑度优势。
完整解释见 [FINDINGS.md](FINDINGS.md)。

机器可读对账快照：
[`deepseek_main_vs_lite_v1_20260817.json`](../artifacts/research_analysis/current_results/deepseek_main_vs_lite_v1_20260817.json)。

## Evidence Completeness

| Result set | Functional | Failure stages | RRES | Paired RRES |
| --- | --- | --- | --- | --- |
| 跨模型 Main-200（5 组） | 完整 | 完整 | 通过题齐全 | 跨模型不成对 |
| API Main-200 | 完整 | 完整 | 144/144 | 与 Lite 成对 126/126 |
| API Lite V1-200 | 完整 | 完整 | 131/131 | 同上 |
| 本地 Main-200 | 完整 | 完整 | 145/145 | 与 Lite 成对 125/125 |
| 本地 Lite V1-200 | 完整 | 完整 | 127/127 | 同上 |
| Qwen3.6-35B V1-200 | 完整 | 完整 | 未作跨方法 RRES 主表 | E50 成对 n=46 |
| DeepSeek Harness / Codex runtime | 未跑 | — | — | — |

原始结果包的 `summary.passed` 是 workflow/run status，不是 Functional Pass。

## Readiness

最近一次针对 **旧 150+E50** 的本地无模型 preflight（2026-08-21 口径）：

- release materialization：150 frozen + 50 external；
- External source mapping：50/50 ready；
- dependency closure：50/50 current；
- balance design：PASS；
- Python 3.11 wheel coverage：200/200；
- baseline freeze：当时记录 150/150 unchanged（**当前工作树已 drift，约 95/150**）；
- runnable task compliance：200/200。

Hard-50 / Python-200' 工程门：50 题 release、无 oracle、symlink 200/200 无断链、
registry summary 176 仓 / 200 题。Docker 正式 200' 跑仍必须执行 strict preflight，
并记录 agent/evaluator image identity。**不要**用 `run_python200_paper.sh` 跑新主表。

## Historical Evidence

旧 Python-150 跨模型 Main 数字已并入 superseded 150+E50 表的 150 列，**不得**单独
当作当前论文主表，也不得与方法对比混排：

- DeepSeek V4 Flash：99/150（66.0%）；
- Qwen3.5 122B：59/150（39.3%）；
- Qwen3.6 35B：59/150（39.3%）；
- GPT-OSS 120B：27/150（18.0%）。

这些模型没有旧 Lite V1 协议的 Python-200 结果。当前 cost arm 是
[V1 = Main+2M](METHOD_V1.md)。不补跑退役 Lite 协议。

## Method Pilots Outside The Main Table

全部方法脚手架已停扩，只作 RQ4 负结果：

| 臂 | 结果 | 文档 |
| --- | --- | --- |
| 当前 V1 Core-12 | Flash Main 8/12 → V1 4/12 | [METHOD_V1.md](METHOD_V1.md) |
| Adaptive Budget V2 Core-12 | 2/12；extra→pass=0 | [archive/methods/METHOD_ADAPTIVE_BUDGET_V2.md](archive/methods/METHOD_ADAPTIVE_BUDGET_V2.md) |
| 旧 Lite V1 Python-200 | Flash −6.5~9.0 pp | [FINDINGS.md](FINDINGS.md) |
| Rescue+ v2.1 / v2.2 | 3/12、2/12 | [archive/snapshots/](archive/snapshots/README.md) |
| TFL / TD / PDR / Exec-Contract | 相对 Main 零翻盘或更差 | [archive/methods/](archive/methods/README.md) |
| Verification-aware Distill-24 | 同日 LLM summary 16/24 → VA 14/24；overflow 修补重跑未齐，停 | [archive/methods/METHOD_VERIFICATION_AWARE.md](archive/methods/METHOD_VERIFICATION_AWARE.md) |
| RQ6 Public-feedback Flash-12 | 同日 Main 0/12 → PF **4/12**；public 6/6 救回；Hidden 多数不动 | [METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md) |
| Spec-adversarial Hidden-4 | 同日 Main 0/4 → SA 0/4；Hidden 0→1 **0/4** → **Kill** | [archive/methods/METHOD_SPEC_ADVERSARIAL.md](archive/methods/METHOD_SPEC_ADVERSARIAL.md) |
| Best-so-far checkpoint 离线 | Flash 失败 51 题全量独特树 Functional 0→1 = **0/51** → **Kill** | [TOKEN_UTILITY.md](TOKEN_UTILITY.md) |
| DeepSeek Harness / Codex runtime | `./setup.sh` 安装 CLI，尚无 Core-12 分数 | [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md) |

12 题通过率不能换算成 Python-200。RQ6 / Spec-adversarial / runtime ablation
数字不进 Python-200 主表。

## Runtime Ablation

基础设施已落地，**尚无正式分数**。DeepSeek Harness 与 Codex 是与 OpenHands
同级的 coding runtime，不是信息消融，也不是 Official Main。先 Core-12 成对，
输出在 `experiments/python/runtime/`。见
[METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md)。

## Current Evidence Gaps

0. **Python-200' 已有收到包的审计 headline，尚无合格主表分。** Flash 原始记录为
   132/200=66.0%，但只有 183 题启动；17 题 freeze-preflight blocked、16 题离线依赖
   失败、59 题 context violation，去重后的严格替换集合是 84 题。固定子集为
   95/116。2026-08-30 离线 wheel 已 200/200；84 题替换因缺少原 Docker digest 未启动。
   任务集与已发出的 source snapshot 均匹配；分析层与结果层已合并：
   `artifacts/research_analysis/python200_hard_task_taxonomy.csv`（200 行，
   `python200_hard_v1`）。旧 150+E50 的 21.5%–72.5% **不是** 新主表。
1. RQ6 Public-feedback Flash-12 同日成对已齐：Main 0/12 → PF 4/12。Entrypoint-Hint
   未跑。见 [METHOD_RQ6_PUBLIC_FEEDBACK.md](METHOD_RQ6_PUBLIC_FEEDBACK.md)。
2. Spec-adversarial Hidden-4 已 Kill（Hidden 0→1 = 0/4）。不要扩面。见
   [archive/methods/METHOD_SPEC_ADVERSARIAL.md](archive/methods/METHOD_SPEC_ADVERSARIAL.md)。
3. Hidden provenance Flash-33 初标已落盘（AI 辅助，非 gold）。下一步按
   [顶会投稿就绪路线图](paper/07_top_conference_readiness_plan.md) 做双 Agent
   consensus；冲突和无法证明的 obligation 保持 abstain 后再做敏感性分析。见
   [HIDDEN_CONTRACT_PROVENANCE.md](HIDDEN_CONTRACT_PROVENANCE.md)。
4. DeepSeek API 全量 V1-200 未跑；不是 blocker，Flash Core-12 已表明 cap 税。
5. 旧 Python-200（150+E50）RRES 中位数贴 1.000，主要来自 E50 copy-heavy。新主表
   紧凑度应拆 Python-150 与 Hard-50，并报 copy 比例。E50 只作旁路对照。独立升格
   计划见 [PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md](PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md)
   （不并进 150，也不进新主表）。
6. 跨模型没有成对 RRES；不得用无配对中位数比较紧凑度。
7. 论文主表前仍需确认 evaluator image 和 context-window 实验资格。
8. Token utility 金标与分层已写入论文 RQ3/RQ5 稿
   [paper/03_results_token_utility.md](paper/03_results_token_utility.md)。Flash 138
   道通过题最早充分中位数 0.40（Direct 0.36 / Composite 0.51）；7 道需要 2M 之后。
   验证循环组合 AUC 弱，不写停机规则。Best-so-far checkpoint 离线已 Kill（失败题
   全量独特树 0/51 Functional 0→1）。见 [TOKEN_UTILITY.md](TOKEN_UTILITY.md)。
9. DeepSeek Harness / Codex runtime ablation 只有 adapter 与 pin，没有 Core-12
   分数。不要把空列写进 Python-200 主表。见
   [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md)。

## Next Actions

0. **论文主套件。** 收到包与离线审计已入库（audit headline 132/200）。2026-08-30
   已把 CPython 3.11 Linux wheel 补到 **200/200**；冻结输入
   `python200-hard-freeze846-input` `--check` 仍通过。84 题严格替换已在独立目录
   **启动**（`python200-hard-main-20260830-strict84-replacement`），workers=1，
   题根为 freeze 输入；**未覆盖** 20260829。本机没有收到包镜像 digest，实际用的是
   本地 `latest`（agent `cc622920…` / eval `cccf858c…`），已写入
   `launch_identity.json`，**不能**无声明并进最终主表。记录见
   [`experiments/registry/python200_hard_wheel_closure_and_strict84_20260830.md`](../experiments/registry/python200_hard_wheel_closure_and_strict84_20260830.md)。
   按 task ID 合并前不写最终主表。旧 150+E50 分数只作 superseded 对照。
1. **停止脚手架迭代。** 不再开 V3、behavior_probe、TFL、Rescue+、V2 扩到 200；
   Spec-adversarial 已 Kill；Best-so-far checkpoint 离线已 Kill，不要实现 Agent。
   不要把 Active Dynamic Exploration 写成论文核心贡献。
2. 保持 Main 为默认对照和论文 RQ1；cost arm 用已完成的 Qwen V1 + Flash Core-12
   （数字在旧 200 上，换套件后需重标，不把 55/200 直接写成 200'）。
3. Context-efficiency / pre-submit audit 的 Core-12 筛选已结束，**不要扩到
   Distill-24 或 Python-200**。相对 LLM summary（8/12，65.0M tokens）：recency
   与 artifact-aware 也是 8/12，但 token 升到 73.8M / 85.9M；pre-submit audit
   为 6/12。数字不进 Python-200 主表。见
   [archive/methods/METHOD_ARTIFACT_AWARE.md](archive/methods/METHOD_ARTIFACT_AWARE.md) 与
   [archive/methods/METHOD_PRE_SUBMIT_AUDIT.md](archive/methods/METHOD_PRE_SUBMIT_AUDIT.md)。
4. RQ6 n=12 已冻结，不要扩到 Python-200。Hidden provenance Flash-33 初标已落盘
   （AI 辅助，非 gold）：Explicit 11 / Recoverable 4 / Ambiguous 0 /
   Underdetermined 18。按 [顶会投稿就绪路线图](paper/07_top_conference_readiness_plan.md)
   完成双 Agent consensus 和 sensitivity 后再写进论文 RQ4。见
   [HIDDEN_CONTRACT_PROVENANCE.md](HIDDEN_CONTRACT_PROVENANCE.md)。
   可写卷宗；新主表 RRES 拆 150 / Hard-50。不要叠 Entrypoint-Hint。数字不进主表。
5. 不要把 Rescue+、Frozen 45 步信封、V2、Core-12、RQ6 Flash-12、Spec-adversarial
   Hidden-4，或 DeepSeek Harness / Codex runtime 通过率写进论文主表。
   旧 150+E50 的 72% 同样不进新主表。
6. Token utility 论文稿已写（RQ3/RQ5）。不要写 stop 规则；不要把 Phase 0
   `last_write_frac` 当 utility。分析底稿 [TOKEN_UTILITY.md](TOKEN_UTILITY.md)。
7. 可选 runtime ablation（DeepSeek Harness / Codex）可在 Core-12 上与
   OpenHands+Flash 成对，见 [METHOD_AGENT_RUNTIME.md](METHOD_AGENT_RUNTIME.md)。
8. External-50：2026-08-27 **合同升格已完成**（50/50 validate、无模板句）。
   copy-all / 独立 freeze 仍按
   [PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md](PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md)，
   不并进 Python-150，也不进新主表。
9. Hard-50 已在上文 Paper main suite：release 齐；收到包原始记录为 29/50=58%，但
   其中 16 题被离线依赖失败混杂，不能据此做新的 split 难度结论。独立的 29/50
   校准仍是设计证据。不得把旧 E50 90%–94% 写进新主表。计划见
   [PLAN_HARD50_EXPANSION.md](PLAN_HARD50_EXPANSION.md)。

运行入口见 [RUN.md](../RUN.md)，实验与结果规范见 [EVALUATION.md](EVALUATION.md)。
