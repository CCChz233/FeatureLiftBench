# FeatureLiftBench 现有实验的严格失败归因

**审计对象：** 550 条冻结 Python OpenHands run，150 个任务，4 个模型；Core-100 400 条、Hard50 150 条。  
**结论状态：** 可用于提出有边界的观察性结论；不能用于宣称动态代码理解或上下文压缩的因果效应。

## A. 一页结论

### 最主要的三个 Agent 瓶颈

| 排名 | 最早关键失败阶段 | 数量 | 占 263 条非基础设施失败 | median tokens | 证据强度 | 判断 |
|---:|---|---:|---:|---:|---|---|
| 1 | 静态 dependency/API closure 识别 | 85 | 32.3% | 1.86M | **强** | 大量 hidden collection/API 错误直接显示缺少导出、成员或普通依赖；不是定位问题。 |
| 2 | 普通实现/语义实现 | 80 | 30.4% | 1.37M | **中** | 已定位、已产出、通常也验证过，但边界行为、异常、顺序或数据语义不正确；其中仍可能混有未标注的闭包遗漏。 |
| 3 | 动态语义候选 | 43 | 16.3% | 1.26M | **中到弱** | 失败行为与预先定义的动态机制相符，但 runtime-state gold 未完成；37 条仍无法区分“动态推断能力”与普通实现错误。 |

另有 32 条预算/轨迹终止（12.2%，median 3.41M）和 15 条边界恢复失败（5.7%）。62 条 dependency-install/evaluator 错误被保留在总分母，但不计作 Agent 瓶颈。

### 对四个研究问题的回答

1. **主要瓶颈发生在“找到代码之后、完成可靠语义闭包之前”。** 95.1% 的轨迹可直接观察到正确入口文件，72.9% public pass，但只有 41.5% hidden pass。最大的损失不是 localization，而是 API/dependency closure 与行为实现。
2. **“无法识别动态运行时依赖”是可观察的真实子问题，但目前不是已证明的独立主要瓶颈。** 主定义下动态任务 pass 41.2%，相对静态任务 39.8%；public pass 后 hidden fail 分别为 43.3% 与 42.7%。差异接近零。
3. **上下文/token 管理与动态理解都不像总体根因。** 动态语义候选 43 条，明确预算/上下文/工作流截断 32 条；二者都少于 closure 和 implementation。上下文问题更明确地表现为效率与少数终止机制，动态问题则存在少量强案例但总体效应未建立。
4. **当前只能得到相关性和高置信度错误机制计数。** 动态标签、condensation、repeated reads、token 都没有随机化。调整模型的动态成功 OR 为 1.16（95% CI 0.54–2.48）；condensation OR 0.70（0.37–1.32），重复不变文件读取 OR 0.97（0.55–1.74）。这些不是因果估计。

### 对论文创新点的含义

现有证据更支持把方法创新表述为：**用可执行证据维护 dependency/API/behavior closure，并在预算内选择能最大幅度降低 hidden-risk 的 probe**。只做“动态分析器”或只做“token 压缩器”都过窄。最值得验证的是三种正交干预：closure hint、runtime trace、evidence-pinned memory；比较谁真正提升 hidden/formal pass。

### Agent 模块改进优先级与价值

“理论上限”是该模块对应的最早失败全部被修复时，相对 550 runs 的最大绝对通过率增量；它不是收益预测。“20% recovery”只是统一的 PoC 筛选门槛，用于比较量级，不是由观察数据估计出的因果效应。

| 优先级 | 模块 | 直接对应失败 | 理论上限 | 20% recovery 对应 | 主要价值 | 证据判断 |
|---:|---|---:|---:|---:|---|---|
| 1 | Semantic closure planner | 85 | +15.5 pp | +3.1 pp | formal/hidden pass | **最高优先级。** 在实现前维护 API、类型、资源、环境与未决依赖的证据账本。 |
| 2 | Implementation & repair loop | 80 | +14.5 pp | +2.9 pp | formal/hidden pass | **最高优先级。** 用小型差分 probe 和反例驱动修复，避免只反复跑宽泛测试。 |
| 3 | Budgeted exploration scheduler | 32 | +5.8 pp | +1.2 pp | token、完成率 | **高效率价值。** 预算失败 median 3.41M token；应按阶段配额、信息增益和停止/换路条件调度。 |
| 4 | Targeted runtime semantics engine | 43 | +7.8 pp | +1.6 pp | 特定动态任务 pass | **中等且待验证。** 只有 4 条明确属于没有选择正确 probe；应按动态风险触发，不应默认全量运行。 |
| 5 | Boundary & packaging planner | 15 | +2.7 pp | +0.5 pp | isolation、extraction ratio | **中等价值。** 联合优化最小语义切片、forbidden import、资源打包与 extraction ratio。 |
| 6 | Verification state machine | 2 条直接失败 | +0.4 pp 直接上限 | +0.1 pp | 防止假完成、提高可诊断性 | **直接 uplift 小，基础设施价值高。** 每次 edit 后使旧验证失效，并强制 final public、针对性 probe、isolation 与 clean install。 |
| 7 | Evidence memory/condenser | 2 条严格 memory 候选 | +0.4 pp 可观察上限 | +0.1 pp | token、稳定性 | **不应作为首要 pass 项目。** 将 closure ledger、失败 probe、未决假设和 verification hash 独立于对话摘要固定保存。 |
| 8 | Localization | 5 | +0.9 pp | +0.2 pp | 少数早期失败 | **低优先级。** 95.1% run 已观察到正确入口，继续优化检索的边际价值有限。 |

此外，62 条 evaluator/dependency-install 失败占全部 runs 的 11.3%。它们不是 Agent 能力提升空间，但修复 evaluator、增加真实 wheel/venv clean-install 和统一依赖环境，对实验可信度属于 **P0 级价值**。

推荐的整体控制流是：`localize → closure ledger → risk-triggered probes → boundary decision → implement/repair → fresh isolation verification → finish`。证据账本应作为各阶段共享的持久状态，不能只存在于可被压缩的自然语言历史中。

### 冷启动诊断：导航冷启动很轻，语义状态冷启动存在

当前 OpenHands prompt 只告诉 Agent 源码、public tests 和 submission 的目录契约，没有提供 repo map、符号索引、AST closure 或跨 run 的语义缓存，因此每条 run 在架构上都是冷启动。但两种冷启动需要分开：

- **定位冷启动不是主要正确率瓶颈。** 523/550 条轨迹有直接证据表明读到了正确入口；其中首次正确入口读取的中位数是第 3 个 Agent 操作，90.8% 在 5 个操作内。只有 5 条非通过轨迹被归为 localization 最早失败。
- **语义闭包冷启动是真实的效率与可靠性问题。** 显式 closure plan 只出现在 62/550（11.3%）条轨迹；每个模型都要重新发现 API、依赖、动态风险、资源和验证状态。非通过轨迹的 unchanged repeated reads 中位数为 2，通过轨迹为 1，但这仍然只是相关性。
- **没有证据证明“更晚找到入口”单调降低成功率。** 超过 5 个操作才读到入口的只有 48 条，pass rate 37.5%；5 个操作内为 42.1%，差异样本小且各 action band 的 pass rate 不单调，不能解释为因果。

因此最值得解决的不是预热一个更大的自然语言上下文，而是提供可复用的 `repo/symbol index + AST closure graph + persistent evidence ledger`。索引解决早期重复探索，ledger 解决发现后仍无法形成稳定闭包的问题。

## B. 失败漏斗

### 直接 evaluator 漏斗（权威结果口径）

| 阶段 | runs | 相对 550 |
|---|---:|---:|
| 全部 run | 550 | 100.0% |
| evaluator 结果可用 | 533 | 96.9% |
| build pass | 443 | 80.5% |
| public pass | 401 | 72.9% |
| hidden pass | 228 | 41.5% |
| formal pass | 225 | 40.9% |

最大的直接下降是 public→hidden：401 条 public pass 中 173 条 hidden fail，条件失败率 43.1%。

### 严格证据链漏斗（保守诊断口径）

| 阶段 | 累积 runs | 该阶段总体 unknown |
|---|---:|---:|
| 全部 run | 550 | 0 |
| 直接观察到正确入口文件 | 523 | 27 |
| 直接观察到正确符号 | 523 | 27 |
| 关键依赖被正向确认 | 314 | 216 |
| 独立实现/无原仓库依赖 | 295 | 17 |
| public pass | 231 | 107 |
| hidden pass | 107 | 107 |
| formal pass | 106 | 0 |

此漏斗不能替代 225/550 的正式结果。它要求每个前置证据都被轨迹直接观察到；216 条 dependency 状态是 **unknown**，不是 failure。符号和 runtime-state gold 尚未完成人工双审，因此 A–E 标签只能作为审计辅助。

## C. 失败类型分布

### 最早关键失败阶段

| 阶段 | failures | median tokens | 涉及模型 | 涉及任务 | 置信度主档 |
|---|---:|---:|---:|---:|---|
| dependency_discovery | 85 | 1.86M | 4 | 49 | 高 |
| implementation | 80 | 1.37M | 4 | 49 | 中 |
| evaluator_or_environment | 62 | 2.72M | 4 | 23 | 高；非 Agent |
| dynamic_semantics | 43 | 1.26M | 4 | 23 | 中/弱 |
| budget_exhaustion | 32 | 3.41M | 4 | 30 | 中 |
| boundary_recovery | 15 | 2.20M | 4 | 12 | 高 |
| localization | 5 | 0.17M | 3 | 4 | 弱 |
| verification | 2 | 3.40M | 1 | 2 | 中/高 |
| unclear | 1 | 4.98M | 1 | 1 | 弱 |

“失败阶段”的 success rate 按定义为 0，报告它会形成同义反复，不能当作风险率。可比较的成功率应按预先存在的任务类型或模型分层：

| entanglement.primary | runs | pass rate | hidden fail | public pass | median tokens |
|---|---:|---:|---:|---:|
| parser_state_coupling | 171 | 50.3% | 24.3% | 1.73M |
| data_model_coupling | 147 | 35.4% | 46.5% | 1.92M |
| framework_coupling | 94 | 28.7% | 59.1% | 1.35M |
| config_environment_coupling | 57 | 42.1% | 48.9% | 1.27M |
| resource_coupling | 47 | 23.4% | 73.2% | 1.38M |
| legacy_vibe_clutter | 24 | 95.8% | 0.0% | 0.38M |
| third_party_dependency_coupling | 10 | 20.0% | 75.0% | 1.48M |

这些 task-type 差异同时携带 subset、repo、模型覆盖和任务设计差异，仍然只是描述性关联。

### 模型分层

| 模型 | runs | passes | pass rate | median tokens |
|---|---:|---:|---:|---:|
| DeepSeek-V4-Flash | 150 | 91 | 60.7% | 1.65M |
| Qwen3-Coder-30B | 100 | 24 | 24.0% | 2.02M |
| Qwen3.6-27B | 150 | 58 | 38.7% | 1.13M |
| Qwen3.6-35B | 150 | 52 | 34.7% | 1.50M |

Qwen3-Coder 只有 Core-100 且使用 204,800 context，其余 450 条使用 131,072 context；context window 与 model 完全或高度混杂，不能从这批数据估计窗口长度效应。

## D. 动态任务对比

### 定义

主定义在看到结果之前固定：任务 taxonomy 出现 dynamic import、global/session/lifecycle state、framework lifecycle、config/environment 或 package-resource coupling 即为 dynamic-runtime。局部 parser state 本身不够。该定义得到 117 个 dynamic task / 432 runs 和 33 个相对静态 task / 118 runs。

| 指标 | dynamic-runtime | relatively static | 差异方向 |
|---|---:|---:|---|
| formal pass | 41.2% | 39.8% | +1.4 pp |
| hidden fail | public pass | 43.3% | 42.7% | +0.6 pp |
| median tokens | 1.51M | 1.65M | dynamic 更低 |
| unchanged repeated-read affected | 54.2% | 61.9% | dynamic 更低 |
| 任意 runtime probe | 82.6% | 86.4% | dynamic 更低 |
| dynamic-targeted probe | 27.8% | 3.4% | dynamic 更高，符合定义 |
| fresh final verification | 80.8% | 82.2% | 接近 |
| condensation | 50.9% | 57.6% | dynamic 更低 |

按 model×subset 分层后，Core-100 中 dynamic 任务通常更低，Hard50 中 dynamic 任务反而略高，但 Hard50 两组都很低。交互项 OR=10.07，95% CI 0.75–135.86，极不精确。这是典型的异质性/小样本问题，不能从聚合均值下结论。

主调整模型：

`Pass ~ Dynamic + Model + Split + log(RepoLOC) + log(ReferenceLOC) + PublicTestCount + EntanglementCount`

- dynamic 对成功的 OR 1.16，95% CI 0.54–2.48，p=0.707；
- 加入 condensation 与 unchanged repeated-read 后，dynamic OR 1.10，95% CI 0.51–2.37；
- legacy dynamic 定义的 OR 1.26，95% CI 0.63–2.52。

结论是“不足以证明动态依赖导致整体失败”，不是“动态依赖没有影响”。

### 三种机制不能混为一谈

43 条 dynamic-semantics 候选进一步分为：

| 子类型 | runs | tasks | median tokens | 解释 |
|---|---:|---:|---:|---|
| capability_or_implementation | 37 | 21 | 1.09M | 已明确谈到机制并做过 targeted probe，但仍失败；现有日志无法再分动态推断能力与普通实现。 |
| exploration_policy | 4 | 4 | 2.57M | 有 runtime probe 条件，但没有针对失败机制的 probe，也未明确识别机制。 |
| memory_state_management | 2 | 2 | 2.03M | 动态信息出现在 condensation 前、摘要未保留、后续不再出现；仅为弱候选。 |

因此不能把 43 条全部写成“Agent 不会动态分析”。只有 4 条更接近 exploration policy failure，2 条是弱 memory 候选。

## E. 16 个代表性案例

| 任务 | 最早失败 | Agent 实际状态 | 漏掉的行为/依赖 | 最可能干预 |
|---|---|---|---|---|
| pytest fixture resolve / Qwen3-Coder | boundary | 找到入口、public pass、targeted probes、fresh verify | isolation 与 fixture lookup API 边界 | forbidden-import + clean isolation |
| responses matcher / Qwen3.6-35B | boundary | public pass、5 个 dynamic probes | 原包/边界依赖及 once/matcher 行为 | isolation audit |
| lark visitor / Qwen3.6-27B | budget | 5 次 condensation、无 probe、未建立 public contract | `Discard` 导出与完整 visitor API | 分阶段预算 + closure checklist |
| pygments lexer / Qwen3-Coder | budget | 17 个普通 probes、0 targeted、5 次 condensation | token 分类/状态行为未收敛 | 早期 probe 选择与停止规则 |
| isort settings / Qwen3.6-35B | dependency | public pass、fresh verify | `ProfileDoesNotExist` 导出 | API closure checklist |
| passlib context / Qwen3-Coder | dependency | public pass、6 probes | `CryptContext.identify` | dependency/API hint |
| pendulum / DeepSeek | dependency | public pass、15 probes、读到 78% closure | `Duration.remaining_days` | symbol/API closure hint |
| transitions / DeepSeek | dependency | public pass、16 probes | nested state `parent` 成员 | closure hint + targeted contract probe |
| celery signal / Qwen3.6-35B | dynamic-memory candidate | public pass、动态机制曾识别、1 condensation | weak receiver cleanup | evidence-pinned memory；需 A/B 验证 |
| configobj / Qwen3-Coder | dynamic-capability/implementation | 2 targeted probes、fresh verify | comment-preserving round trip | behavior-differential trace |
| dynaconf / Qwen3-Coder | dynamic-capability/implementation | 3 targeted probes、fresh verify | layered TOML environment precedence | runtime trace |
| phonenumbers / Qwen3-Coder | dynamic-exploration | 6 probes但 0 targeted | lazy region metadata/validity | targeted runtime trace |
| pygments formatter / Qwen3-Coder | implementation | public pass、fresh verify | full-document wrapper/filename semantics | targeted failing-behavior probe |
| pygments lexer / Qwen3.6-27B | implementation | public pass、20 probes | `stripall` whitespace semantics | boundary probe |
| scrapy item loader / DeepSeek | implementation | public pass、52 probes | missing-field error semantics | smaller discriminating probes |
| license-expression / Qwen3.6-35B | verification | final edit 后未 fresh verify | AND/OR precedence | mandatory post-edit verification |

每个案例的动态信号、Agent 已知信息、探针、condensation、遗漏可见性和证据路径见 [representative_case_dossiers.md](representative_case_dossiers.md)。

## F. 证据边界

### 当前数据可以支持

- 550 条 run 的直接 outcome、token、事件和停止原因；token 恒等式无误。
- 533 条 evaluator 结果及 62 条 infrastructure failure 的隔离。
- 直接 ImportError/AttributeError/forbidden import 所支持的 closure/boundary 失败。
- 26 条 step-limit、2 条 timeout、4 条 context violation，以及 288 条有 condensation、共 552 次 condensation。
- 动态/静态、probe、重复读取、fresh verification 与成功的描述性/调整后关联。

### 当前数据不能支持

- 动态 runtime coupling 是首要因果瓶颈；
- high token、repeated reads 或 condensation 导致失败；
- compression 造成信息遗忘：58 条全局 memory-loss heuristic candidate 只是筛选信号，进入严格 dynamic failure 的只有 2 条；
- clean install 成功率：533 条 evaluator 全部采用 path import，clean install 实际执行为 0；
- 64k/128k/256k context 的因果比较：现有 550 条没有随机窗口实验，且 204.8k 只对应一个模型；
- 精确的 dependency/runtime closure recall：216 条依赖阶段为 unknown，closure gold 的 symbol/runtime_state 仍标记 unresolved。

### 建立因果关系所需的新实验

1. **Probe 因果实验：** dynamic/static 分层任务上做 `default` vs `mandatory targeted runtime probe`，固定 model/task/seed/context/budget，检验 task-type×intervention。
2. **根因三臂实验：** `dependency closure hint` vs `runtime trace` vs `extra token`，主指标 HiddenPass@B/FormalPass@B；哪一臂提升决定更接近 closure、动态还是预算根因。
3. **记忆实验：** default condenser vs evidence-pinned memory，固定 token budget；预注册 dynamic evidence retention、invalidation、fresh verify 和 hidden pass。
4. **窗口实验：** 同模型同任务同 seed 的 64k/128k/256k 随机或配对实验；记录真实 Condensation、最大 prompt、forgotten IDs 与 context violations。
5. **安装门实验：** evaluator 增加 wheel build + 新 venv install + package-resource probe，再重估 boundary/packaging failure。
6. **人工金标：** 对至少 50 条 public-pass/hidden-fail 轨迹双人盲审 earliest stage、dynamic mechanism、发现/遗忘时序；报告一致性和冲突裁决。

## 方法与复现

主表逐条连接 trajectory、usage/context audit、evaluator result/log、metadata、oracle manifest 和 taxonomy。阶段 A–N 保存于 [trajectory_stage_labels_550.csv](trajectory_stage_labels_550.csv)。分析脚本为 [build_failure_attribution.py](build_failure_attribution.py)，已完整执行的 notebook 为 [failure_attribution_analysis.ipynb](failure_attribution_analysis.ipynb)。

符号识别、依赖闭包和动态机制标签采用保守启发式并保留 `yes/no/unclear` 与证据 ID；hidden-test 源代码不用于构造 Agent 行为特征。回归按 task 聚类稳健标准误，但仍是观察性模型。
