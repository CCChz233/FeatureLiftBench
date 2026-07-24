# ICLR 方法创新路线图

> **SUPERSEDED（2026-07-23）**  
> 本文以 **ECSM** 为主创新候选，该路线**已废弃**。  
> 当前入口与方向：[../CURRENT_RESEARCH.md](../CURRENT_RESEARCH.md)（通用 RSG 工具 + 模型自主决策）。  
> 下文仅历史存档。

## 1. 与仓库现状的边界

仓库已有 `harness/featureliftbench/featurelift_agent.py`，会生成 `closure_plan.md`、`dependency_manifest.json`、`hidden_boundary_check.md`、`prune_log.md` 和 `final_checklist.md`，并支持 `closure_plan/extraction_plan/final_checklist/repair_plan` 阶段。当前没有正式 experiment 使用该 controller；这些文件大多是计划文本或空 manifest，不构成可执行 closure 方法。

因此，不能把“增加 closure plan/checklist”包装成新贡献。潜在 ICLR 贡献必须来自：状态的形式化、执行证据驱动的更新、expand/prune 决策、可证伪停止条件，以及对 hidden/compactness 双目标的因果实验。

## 2. 候选创新

### 2.1 Executable Closure State Machine（ECSM）

**解决的机制问题**：Agent 不知道当前提交覆盖了哪些行为义务、哪些只是猜测，因此 public pass 后错误停止。

**核心技术**：维护三部图：`obligation`（API/行为/状态/资源）—`artifact`（文件/符号/资源）—`evidence`（import probe、行为 probe、runtime trace、deletion result）。每个节点有 `unseen/hypothesized/executed/satisfied/contradicted` 状态和置信度；控制器只在未解决风险低于阈值时允许 stop。

**为什么不是普通 prompt/RAG/依赖图/multi-agent**：不是给更多文本，而是让环境执行改变状态；不仅表示静态边，还表示异常、注册、资源和顺序义务；相同模型可被状态机约束。

**最小原型**：在现有 `dependency_manifest.json` 上新增 obligation/evidence schema；拦截 inspect/copy/test/finish action；每次 action 后更新 `closure_state.json`。

**关键实验**：E0/E1/E3/E4/ECSM 配对比较；A/B/C 分层。

**必要消融**：去掉 evidence、去掉状态置信度、只保留静态 graph、允许 public pass 直接 stop。

**最大风险**：obligation extractor 不可靠；状态可能只是复杂 checklist。

**ICLR 创新潜力**：9/10。前提是展示跨动态依赖类型的因果收益，并证明不是 prompt token 增加。

**集成位置**：`featurelift_agent.py`、新 `closure_state.py`、`openhands_runner.py` finish gate、`agent_runner.py` condition logging。

### 2.2 Evidence-Calibrated Expand–Prune Controller

**解决的机制问题**：under-extraction 与 over-extraction 的边界选择不稳定。

**核心技术**：把过程拆成 recall-first expand 和 evidence-first prune。Expand 选择最大 expected hidden-risk reduction 的 artifact；Prune 选择最小 predicted risk increase 的 artifact。两个阶段共享 ECSM 状态，而不是固定轮数。

**区别**：不是“先 copy 再删”的脚本；每一步由 obligation uncertainty 和执行反馈决定，优化 hidden-risk/footprint Pareto frontier。

**最小原型**：启发式 utility：`risk_covered / added_LOC` 与 `LOC_saved / evidence_loss`；不训练模型。

**关键实验**：under cohort 的 hidden recall、copy-heavy cohort 的 ratio；同 budget 对比一次性 extraction。

**必要消融**：expand-only、prune-only、固定 top-k、随机删除。

**最大风险**：public-derived evidence 不足，导致 prune 破坏 hidden behavior。

**ICLR 创新潜力**：8.5/10。

**集成位置**：`featurelift_agent.py` phase scheduler；新 `expand_prune.py`。

### 2.3 Counterfactual Dependency Necessity Verifier（CDNV）

**解决的机制问题**：静态图能给 reachability，却不能判断一个 artifact 对目标行为是否必要。

**核心技术**：在隔离副本中删除/替换候选文件、symbol、resource 或 registry initialization，运行 obligation probes，用差分结果生成 necessity edge；缓存构建与 probe 结果。

**区别**：普通调用图是观察性、语法级；CDNV 是干预式、行为级，能捕获 dynamic import、global state 和资源。

**最小原型**：文件级 deletion + import/API/public/generated probes；随后做 symbol-level mutation。

**关键实验**：D cohort 的 ratio 降幅和 hidden retention；B cohort 的动态 edge recall。

**必要消融**：static reachability prune、unused-import prune、随机 deletion、无缓存。

**最大风险**：probe 不完备导致 false-negative necessity，或每题运行次数过多。

**ICLR 创新潜力**：8.5/10。

**集成位置**：新 `necessity_verifier.py`；复用 evaluator 的临时环境与 metrics。

### 2.4 Hidden-Risk Estimator from Unexecuted Obligations

**解决的机制问题**：Agent 对 public test 以外行为的风险没有校准，停止过早。

**核心技术**：根据 TASK obligation、source branches、未执行异常/状态路径、动态边和 evidence freshness 估计 residual hidden risk；作为 stop gate 和 action priority。

**区别**：不预测具体 hidden tests，也不读取 hidden；估计的是未覆盖义务，不是普通 self-reflection confidence。

**最小原型**：规则分数；后续可用历史轨迹训练 calibration model，但第一周不训练。

**关键实验**：风险分数对 hidden fail 的 AUROC/ECE；固定 action budget 下的 stop 改善。

**必要消融**：只用 public result、只用 metadata、只用 static graph、去掉 dynamic risk features。

**最大风险**：benchmark-specific，跨 repo 泛化不足；容易被审稿人视为 engineered heuristic。

**ICLR 创新潜力**：7.5/10。

**集成位置**：新 `hidden_risk.py`；OpenHands finish interceptor。

### 2.5 Runtime Registry and Resource Probe Synthesizer

**解决的机制问题**：plugin/registry/global state/resource 边不在静态依赖图中。

**核心技术**：从 source/metadata 自动构造状态转移 probe：注册→查询、load→cache、enable/disable→merge、resource lookup→behavior。执行前后快照对象/registry，并写入 ECSM evidence。

**区别**：不是 RAG 检索文件；生成并执行状态实验，观测动态边。

**最小原型**：为 entry points、dict/list registry、module-level cache 提供 3 类模板；先覆盖 `stevedore/pytest/jupyter/click/phonenumbers`。

**关键实验**：B cohort 对比 static hint；dynamic edge recall 和 hidden pass。

**必要消融**：无前后状态 diff、只 import trace、只模板不执行。

**最大风险**：模板覆盖面有限，可能成为手工 task-specific system。

**ICLR 创新潜力**：7.5/10。

**集成位置**：新 `probe_synthesis.py` 和 `runtime_trace.py`。

### 2.6 Executable Repository Memory

**解决的机制问题**：295/450（65.6%）轨迹至少重复读取同一路径，探索结果没有被可靠复用；该数值由 `trajectory_records.csv` 自动统计。

**核心技术**：把每次 read/search/test 归并为带 hash、claim、支持/反驳证据、依赖对象的 memory item；后续动作先查询“已知什么/为何知道”，文件变化时使证据失效。

**区别**：普通 RAG 存文本块；这里存可执行 claim 和失效规则，服务 closure state，而非扩大上下文。

**最小原型**：path+content hash cache、symbol summary、test/probe evidence index；阻止无理由重复 view。

**关键实验**：同结果下 token/tool calls/repeated views；验证是否不伤 hidden pass。

**必要消融**：只缓存文本、无 invalidation、无 claim linking。

**最大风险**：主要贡献像系统优化，单独不足以支撑 ICLR 方法论文。

**ICLR 创新潜力**：6.5/10，适合作为主方法组件和效率结果。

**集成位置**：OpenHands tool wrapper；新 `evidence_memory.py`。

### 2.7 Closure Process Supervision

**解决的机制问题**：最终 pass/fail 奖励稀疏，无法教会模型何时 expand/prune/stop。

**核心技术**：用 oracle/task construction evidence 和 counterfactual deletion 自动产生过程标签：正确发现 obligation、支持 necessity edge、错误停止、无证据复制、成功裁剪。训练或 rerank action policy。

**区别**：不是普通 chain-of-thought supervision；标签来自执行干预和 closure state transition。

**最小原型**：先不训练，收集 `closure_events.jsonl` 并用规则 reranker；下一阶段再做 SFT/RL。

**关键实验**：rule policy vs learned policy；跨 repo held-out；process label ablation。

**必要消融**：只用最终 reward、只用 oracle file labels、无 counterfactual labels。

**最大风险**：训练数据规模小、oracle leakage、标注偏向 benchmark。

**ICLR 创新潜力**：8/10（长期），但不是下一周首做方向。

**集成位置**：ECSM event logger；未来训练 pipeline。

## 3. Top 3

### Top 1：ECSM + Evidence-Calibrated Expand–Prune

**一句话论文主张**：Repository feature extraction 的核心瓶颈不是定位，而是在不可见行为下恢复并压缩可执行闭包；显式 closure state 与证据驱动 expand–prune 能同时提高 hidden correctness 和 compactness。

**方法框架**：TASK obligations → candidate artifacts → executable evidence → residual risk → expand/prune/stop。

**最小代码改动**：扩展现有 FeatureLiftAgent manifest schema；增加状态更新器、finish gate、启发式 controller；OpenHands 仍作为底层执行 Agent。

**最小实验矩阵**：先执行已冻结的 10 题 × 7 arm pilot；只有通过 `PILOT_DECISION_RULES.md` 的 go gate 后，再增加 ECSM state/prune/stopping 消融与 seeds。

**审稿人质疑**：只是复杂 checklist；使用 oracle 信息；只对本 benchmark 有效；更多工具调用带来收益。

**回应**：用相同 prompt token/tool budget；无 oracle 的 ECSM 主结果；Oracle arms 仅做机制诊断；去掉 executable evidence 的 checklist ablation；动态/静态/行为分层；报告效率。

### Top 2：Counterfactual Dependency Necessity Verifier

**一句话论文主张**：对候选依赖做可执行删除干预，可以学习静态依赖图无法提供的行为 necessity，并把 copy-heavy 功能通过转化为紧凑闭包。

**方法框架**：candidate artifact → isolated deletion → obligation probes → necessity edge → safe prune。

**最小代码改动**：临时 clone、文件级 deletion、probe runner、缓存、evidence JSONL。

**最小实验矩阵**：6 个 copy-heavy pass × static prune / random prune / CDNV；另加 4 个 dynamic state task。

**审稿人质疑**：删除测试昂贵；public probes 不代表 hidden；delta debugging 已有。

**回应**：缓存和分层删除的成本曲线；hidden retention 作为外部验证；与 delta debugging/unused-code/static reachability 直接比较；强调目标是多类型闭包而非最小失败输入。

### Top 3：Hidden-Risk + Runtime Probe Synthesis

**一句话论文主张**：从未执行的行为义务而非模型自信估计 hidden risk，并自动执行 registry/resource 状态 probe，可减少 public-test 诱导的错误停止。

**方法框架**：obligation extraction → unexecuted branch/state detection → probe synthesis → calibrated stop risk。

**最小代码改动**：规则 obligation extractor、三类 runtime probe 模板、finish risk score。

**最小实验矩阵**：6 behavior + 6 dynamic tasks，Standard / checklist / risk-only / risk+probe。

**审稿人质疑**：probe 模板手工、任务泄漏、只是 test generation。

**回应**：模板只依赖通用 Python constructs；held-out repo；与普通 test-generation prompt 对比；展示 state edge recall 而非只报 pass。

## 4. 最终推荐

优先做 **Executable Closure State Machine + Expand–Prune**，把 Counterfactual Necessity Verifier 作为其 prune 证据引擎。

原因：

1. 它能统一解释 under-extraction、over-extraction、复制很多仍漏依赖、public-pass 过早停止和重复探索。
2. 仓库已有 FeatureLiftAgent scaffold，可低成本升级，不需要训练新模型。
3. 它有清晰的因果对照：strong prompt、Oracle Locate、Oracle Closure、static hint、reflection。
4. 论文贡献不是“更长 prompt”或“更大依赖图”，而是**执行反馈如何改变闭包 belief state 与 stop policy**。

Go benchmark 暂不扩展；先在 Python 的静态、动态、行为、copy-heavy 四类任务上证实机制，再谈跨语言泛化。
