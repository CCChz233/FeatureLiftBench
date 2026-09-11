# FeatureLiftBench 论文大纲与图表方案

> **Documentation status: current · Last verified: 2026-09-11**
>
> 当前实现以 [main.tex](main.tex) 为准，数据与代码入口见 [WORKFLOW.md](WORKFLOW.md)。Benchmark 为 200 题、176 个仓库、182 个快照；主比较为相同 150 题上的六配置结果，五配置额外覆盖其余 50 题。
>
> 当前正文采用八章结构、七张表和五张定稿图。Fig. 1 为通用 motivation，Fig. 2 为构建与验证，Fig. 3 为任务组成，Fig. 4 为功能结果和通过频次，Fig. 5 为共同成功产物差异。RQ3 使用通过频次与构建批次控制分析，分类表放在附录。
>
> 2026-09-11 已按最终实验范围重写评测协议、内部有效性和复现附录，开发历史不再作为当前实验问题展开。正文保留实际配置、评分规则与统计限制。此前大纲全文见 [历史快照](../archive/snapshots/paper_final_scope_20260911/README.md)。
>
> 下文保留早期结构论证和文献阅读笔记，供理解设计选择；其中旧图号、占位安排和阶段性状态不覆盖上述当前实现。

## 1. 先确定我们要讲的故事

**论文定位：一篇提出明确评测任务、构建 benchmark 并进行实证分析的论文。**

核心问题是：**当目标功能的完整实现已经存在于仓库中，coding agent 能否恢复其规定行为，将其重构为脱离原仓库也能执行的独立产物？通过之后，产物的抽取规模又如何？**

建议贯穿全文的论点：

> Feature lifting requires recovering the declared behavior of an existing capability across a new package boundary. FeatureLiftBench makes this task executable and measurable, and its results show why functional correctness and extraction footprint must be evaluated separately.

中文叙事链：

```text
真实的软件复用需求：把已有功能从宿主仓库中取出来
    ↓
评测边界：完整源仓库是证据，最终提交是独立产物
    ↓
基准设计：公开契约、固定源快照、受保护测试、无源仓库的评测环境
    ↓
能力测量：现有 model–harness 配置能够完成一部分任务，仍有明显失败
    ↓
进一步分析：失败落在哪些环节？哪些任务更难？通过的产物是否紧凑？
    ↓
研究启示：行为保留与产物构建应分别测量；契约恢复值得进一步研究
```

标题建议：**FeatureLiftBench: Benchmarking Behavior-Preserving Feature Lifting from Real Repositories**。

三项贡献的工作表述：

1. **任务与数据。** 将 repository-level feature lifting 定义为有明确输入、输出及行为边界的 agent 任务，提供冻结的 Python benchmark。
2. **评测协议。** 控制源仓库和测试的可见性，在 source-free 环境中检查功能，并独立报告通过产物的 reference-relative footprint。
3. **实证发现。** 基于已有六配置结果分析功能能力、失败阶段、任务难度和同题抽取差异，另以探索性案例解释部分行为失败。

“真实”首先由来源和任务边界支撑；“困难”由结果分布支撑；“可信”由已完成的验证证据及其局限支撑。不要仅把这些形容词写进贡献句。

## 2. 四篇参照论文：学它们的论证结构

这组参考是合理的。下面是根据原文目录、方法段落和图注整理的**结构借鉴**，不复制原文措辞，也不假定我们完成了相同的实验或审查。

| 参照论文 | 原文组织与图表作用 | 对我们的具体用途 | 不照搬的部分 |
| --- | --- | --- | --- |
| [SWE-bench](https://arxiv.org/html/2310.06770) | §2 交代构建、任务形式与数据特征；§4–5 交代设置和结果。Fig. 1 展示一个任务的输入、输出和验证，Fig. 2 展示筛选过程。原文还包含单独的 SWE-Llama 训练章节。 | **作为整体骨架的主要参照。** 首图解释任务，第二张图解释任务如何构成可信数据，之后才看 baseline。 | 不需要为了模仿其模型训练章节而新增方法贡献；真实仓库来源也不等于我们的每道任务均来自真实用户 issue。 |
| [SWE-Bench Pro](https://arxiv.org/html/2509.16941) | §3–4 将数据集特征与制作过程分开，§5 主结果之后接 §6 分析；§6.3 使用模型辅助轨迹失败判断，并披露分析做法。 | 学习**主结果与解释性分析分层**；用任务范围、公开要求和运行环境解释评测质量。 | 不借用其人工增补、商业仓库、抗污染或专家耗时结论。我们没有对应证据时，不宣称企业代表性或专家级长程工作量。 |
| [Terminal-Bench 2.0 论文](https://arxiv.org/html/2601.11868) | §2 依次讲任务、构建、验证、构成；§3 设置后接 §4 结果。Fig. 2 展示执行边界，Fig. 3 展示审核流程；§4.3 区分预估难度与实际表现。 | 学习**任务定义—构建—验证—构成**的展开顺序，以及“设计标签不等于经验难度”。 | 其多轮专家审查、对抗检查和重复运行是其完成的工作，不能画成我们的流程。其首页排行榜服务于该论文，我们的首图更应解释 feature lifting。 |
| [OSWorld](https://arxiv.org/html/2404.07972) | §2 先讲环境与交互、初始化和执行评测；§3 再讲任务、质控、统计与人类表现。Fig. 1 是场景概览，Fig. 2 是环境生命周期。 | 学习**环境保证与任务质量分开写**：评测环境可复现，不等于每个测试期望都公平。 | 不复制人类基线或完整人工质控声明；我们的环境机制可放在 benchmark 及评测章节内，不必写成庞大平台贡献。 |

阅读版本：SWE-bench HTML 标识 v3，SWE-Bench Pro HTML 标识 v2；Terminal-Bench 和 OSWorld 采用本次可访问原文。上表只借鉴结构与图表用途，不引用它们的动态排行榜成绩，也不将这些论文一概标为某个已核实的会议版本。

**组合建议：用 SWE-bench / Terminal-Bench 的总体顺序，吸收 OSWorld 对环境和质控的区分，以及 SWE-Bench Pro 对结果和分析的分层。**

还有一个定位上的必要补充：这些论文是写作参照，不全是我们最接近的工作。[FeatureBench §3.1](https://arxiv.org/html/2602.10975v1#S3.SS1)已经包含增量开发和从零构建功能；[Automated Software Transplantation](https://crest.cs.ucl.ac.uk/autotransplantation/downloads/autotransplantation.pdf)已经研究抽取并移植可执行功能。因此不能把“功能级任务”或“独立模块”本身写成首次提出。我们的区别应落在**完整 donor 仓库仍可见、按公开范围恢复已有行为、跨越新的 package 边界、source-free 评测以及独立 footprint 测量**这一组合上。

## 3. 建议采用的完整目录

```text
1. Introduction

2. The FeatureLiftBench Benchmark
   2.1 Task Formulation and a Running Example
   2.2 Task Construction and Source Provenance
   2.3 Validation Evidence and Quality Boundaries
   2.4 Dataset Composition

3. Evaluation Protocol and Experimental Setup
   3.1 Information Boundary and Agent Configurations
   3.2 Functional Evaluation and Extraction Metrics
   3.3 Result Assembly and Statistical Protocol

4. Benchmark Results
   4.1 RQ1: Overall Functional Capability
   4.2 RQ2: Where Do Submissions Fail?
   4.3 RQ3: How Does Success Vary across Tasks?
   4.4 RQ4: How Compact Are Common Successes?

5. Diagnostic Analysis and Discussion
   5.1 Contract Defects and Sensitivity
   5.2 Exploratory Evidence on Behavioral-Contract Recovery
   5.3 Implications for Feature-Lifting Agents

6. Threats to Validity
7. Related Work
8. Conclusion

Appendices
A. Full Task Inventory, Provenance and Validation Records
B. Supplementary Release Results
C. Complete Gate, Paired and Statistical Results
D. Provisional Failure Annotations and Cases
E. Run Identity, Profiles, Recovery and Reproduction
```

相关工作暂放靠后，让读者先理解新任务；引言仍需引用并比较最接近的工作。若后续投稿模板更适合提前放 Related Work，可以整体移动这一节，不改变论证顺序。此处不预设具体会议的页数或格式规则。

### 1. Introduction：为什么值得单独测量？

**读者应带走：** 这是一个清楚的软件复用任务，而不只是换了题目的代码生成榜单。

建议六段：

1. 从复用场景进入：信号分发、缓存或配置功能存在于仓库中，需要迁到独立组件。
2. 难点来自行为跨越 package 边界：helper、异常、状态、资源与依赖不能随意丢掉。
3. 和 issue repair、feature implementation、软件移植比较，准确说明我们的输入与交付边界。
4. 概述 benchmark：完整仓库和公开契约可见，源位置提示和 benchmark tests 不可见，提交进入 source-free evaluator。
5. 用两三项主要发现预告结果；先讲功能能力，再讲同题产物差异。探索性归因不放成摘要级硬结论。
6. 三项贡献。

**配置图表：Fig. 1。** 不在引言罗列 freeze 哈希、历史版本和全部负结果。

### 2. The Benchmark：任务如何定义、构建并被验证？

**2.1 任务与例子。** 定义 `repository + public contract → independent artifact`。用一例讲清功能范围、合法策略和运行时禁止依赖原仓库。建议使用 [blinker 信号注册任务](../../benchmark/tasks/blinker__signal_registry_core__001/TASK.md)：sender filtering、弱引用清理、Namespace 身份保持都在公开契约中，非专业读者也容易理解。正式绘图前从冻结记录核对使用的契约版本；不要把当前工作树路径自动当作冻结输入。

**2.2 构建与溯源。** 仓库快照与来源记录 → 功能候选和范围 → API/行为契约 → 测试与参考证据 → 版本化题包。写清哪些是脚本检查、哪些是 AI 辅助工作、哪些有维护者裁决。不编造候选池总量、筛掉比例或全量人工筛选历史。

**2.3 验证证据。** 依次回答：源身份是否固定、参考实现是否可执行、测试是否来自公开义务、是否控制了源仓库访问。分别列出“已通过的机械/执行检查”和“尚不能声称完成的语义公平性审查”。现有记录支持 200 task checks、200 source mappings、oracle 600/600 与 200 stable tasks；不能据此推出每条隐藏期望都合理。

**2.4 构成。** 用覆盖范围解释 200 个发布任务与 150 个共同评测任务。后者六配置均有结果，并具备所需产物统计；其余 50 题的五配置结果放附录。功能类别说明覆盖面，任务结构则分两维介绍：

- **提取任务的性质（单标签）：** Direct、Adapted、Composite，分别说明与上游主体能力的行为对应、显式转换和多能力组合；保留 56/76/18 的段落统计与案例。
- **缠绕机制（多标签）：** 代码依赖、数据与状态、框架机制、环境与资源。解释独立提取时需要处理的依赖，用 Blinker 说明 Direct 也可能涉及多个缠绕机制。

附录记录原有十个机制标签到四类的映射及按任务去重的规则。这是对已有标签的展示归并，不宣称完成新一轮语义标注，不据实验目录名称划分难度，也不把机制标签直接当成失败原因或新增分组性能结论。

**构建图：Fig. 2；构成统计用段落说明。** Construction 描述如何产出题包，Protocol 描述如何评价 agent，两者不要重复画成同一流水线。

### 3. Protocol and Setup：这些分数究竟测量了什么？

**3.1 信息边界与配置。** 明确 Main 下 Public/Hidden benchmark tests 都不可见；upstream tests/docs 可见。列出六 backend、OpenHands、名义步数/上下文/超时、condenser 与 provider 差异。称为 model–harness configurations，不写成只改变 base model 的纯控制实验。

**3.2 评测和指标。** 主分数是 `Build ∧ Public ∧ Hidden ∧ Isolation`，空卷计失败。说明 Build 的实际 loading/install fallback；Isolation residual 是 gate 层面的操作化统计。RRES 与 detected copy fraction 只分析通过包；模型差异使用共同通过题。不要把复制比例当成质量总分。

**3.3 结果组装和统计。** 解释结果纳入、preflight/recovery 与 freeze 继承。报告 Wilson CI、成对 McNemar、总体通过频次和 common-pass 产物比较。单次结果不估计重复运行方差；未调整的探索性 p 值不支持完整模型排序。

**实验设置用段落说明。** 取消重复设置表；精确哈希和全套 profile 留附录，正文保留足以评估可比性的信息。

### 4. Results：四个问题，各回答一次

| 小节 | 要回答的问题 | 核心证据 | 可写的结论 | 图表 |
| --- | --- | --- | --- | --- |
| 4.1 Capability | 当前配置完成多少任务？ | 六配置 150 题 through-gate counts、Wilson CI、selected paired outcomes | 记录中有较大的性能范围，且现有配置未全部解决该集合 | 功能主结果表；不再画一张相同的排行榜 |
| 4.2 Failure stages | 已交包或未交包的任务在哪里失败？ | 首败阶段；有包样本的非互斥 gate flags | 强配置失败主要落在行为测试；单独 Isolation gate 的最终残余较少 | Fig. 3 |
| 4.3 Task variation | 不同任务的成功覆盖有何差异？ | 各题被 0–6 个配置通过的总体分布 | 28 题无人通过、17 题全部通过、105 题表现混合；这不是固有难度标签 | Fig. 4 |
| 4.4 Extraction footprint | 同样通过的任务，交付物有何差别？ | Pro–Luna 共过 97 题；Flash–Luna 共过 92 题；paired RRES/copy | 功能通过与抽取规模是不同维度；同题成功产物仍可有明显差异 | 配对产物表 + Fig. 5 |

每节按“先回答 → 给证据 → 解释适用范围”组织。不要重复正文中的全部表格数字，不把 gate 阶段叫作语义根因。

### 5. Diagnostics and Discussion：能从失败中理解什么？

**5.1 先交代缺陷和分母。** 正文主表保留原 150；七个任务被既有 AI 初审标记为潜在 contract/evaluator defects。将同一七题从所有配置中排除，给出 post hoc 143 题敏感性。既有离线汇总显示分子均不变，最强 115/143=80.4%，六家全败从 28 降至 21。它不是经过重新验证的新 leaderboard，也不证明剩余题无缺陷。六配置敏感性结果用附录短段落呈现，正文保留主要影响和引用。

**5.2 再做探索性解释。** Pro/Flash 有包失败 77 条，剔除 14 个相关行后为 63 条。展示一两个由公开契约支持的实例，解释“接口看起来在，但异常、默认值或状态行为仍未恢复”。Contract closure 在此是工作假说/症状描述。L1 归因计数放附录并标为 assistant first pass，不制作主文全六模型根因饼图。读过仓库不能证明定位充分。

**5.3 写启示。** agent 可以更明确地追踪行为义务与源码/实现证据；评测应同时保留行为正确和抽取 footprint。写成后续研究方向，不宣称已有方法改善了分数。旧方法 pilot 不占用本节主线。

### 6. Threats to Validity：精准解释结论边界

按四类写，避免泛泛的免责声明：

- **Construct：** 有限测试、潜在契约冲突、Build path fallback、RRES 参考不保证最小、copy 检测为语法代理。
- **Internal：** 版本继承、配置/端点与 condenser 差异、recovery、source-free 环境和依赖可用性。
- **External/statistical：** curated Python 集合、仓库间重复来源、单次结果与小样本分类、训练污染未测、非工业随机样本。
- **Annotation：** L1 非独立人工金标；强配置 census 和其他配置抽样不可混成一个根因分布。

### 7. Related Work：回答最接近工作中的区别

三组即可：

1. slicing、feature location、软件重用与 transplantation；
2. SWE-bench / SWE-Bench Pro、FeatureBench / FeatBench 等可执行编码评测；
3. Terminal-Bench、OSWorld、OpenHands 等执行环境与 agent 测量。

写“输入证据、输出边界、验证对象、质量维度”的具体差别。不要写“以前都是修 bug”“以前没有独立模块”“我们首次做软件抽取”。结构参照论文不必占相关工作的最大篇幅。

已新增正文 `tab:positioning`：HumanEval、SWE-bench/Pro、FeatBench、FeatureBench L1、FeatureBench L2、software transplantation、FeatureLiftBench 共七行，比较输入证据、要求的交付物和评测对象。该表说明评测问题的不同，不比较跨 benchmark 分数，也不使用未经证明的“此前不支持”勾叉矩阵。

### 8. Conclusion：收回三项贡献

回到 feature lifting 这一任务、可执行 benchmark 和关键经验发现。结尾强调正确性和产物 footprint 的区分。不新增方法承诺，不把探索性 contract-closure 比例升级为已证明机制。

## 4. 正文图表计划与接入状态

**当前正文有四张图占位、一张已接入的配对产物差值图和三张表。** 新版 A/B/C 已生成，图 C 已覆盖六个配置并替换原图 5；A/B 尚未接入。旧图 1–2 仍不制作，后续正文编号随最终图组合调整。下表保留原图的对应关系，最新绘制规格见 `figures/CHART_CONTRACTS.md`。

| 编号 | 内容 | 位置 | 读者看完应理解 | 当前状态 |
| --- | --- | --- | --- | --- |
| Fig. 1 | 一道真实 feature-lifting 任务与产物边界 | Introduction / 2.1 | 我们要求 agent 交付什么，为什么跨边界会丢行为 | 需新画矢量图 |
| Fig. 2 | 题包构建、验证证据与可见性分层 | 2.2–2.3 | 数据怎么来；检查能保证什么 | 需新画矢量图 |
| Fig. 3 | 首败构成 + Isolation residual 的明确分母 | 4.2 | 失败集中在哪里，过程失败与交付物失败有何不同 | 已有统计与漏斗图，可重排 |
| Fig. 4 | 0/6–6/6 总体通过频次 | 4.3 | 在同一任务集合内展示观测差异 | 已生成单面板图 |
| Fig. 5 | 同题通过的 RRES 与 copy 配对分布 | 4.4 | 正确性相同不代表抽取 footprint 相同 | 已有 paired-copy 图，补上 paired RRES |
| Table 1 | 六配置总体通过数（率）及 Wilson CI | 4.1 | 能力规模与估计区间 | 已填入 |
| Table 2 | 同题 RRES/Copy 中位数、差值和方向计数 | 4.4 | 同样通过后的产物差异 | 已填入 |
| Table 3 | 文献任务接口对照 | §7 | 输入、交付物、验证对象的区别 | 已填入 |

### Fig. 1：优先画，先让人理解任务

**布局：横向三部分，用一个例子贯穿。**

```text
[公开契约 + 完整 donor 仓库]   →   [Agent 提交 featurelifted]   →   [移除 donor 后评测]
 Signal / Namespace                 恢复所需功能                 可加载 + 规定行为 + 隔离
 sender 分发、weak 清理、身份保持      允许抽取/改写/重新实现          通过后测量 RRES / copy

     源码中的相关逻辑与支持关系                  ↑                     源仓库不可见
     用少量节点表示，不画整个文件树          新的 package 边界
```

- 使用公开 blinker 任务做 running example，帮助理解“边界之外仍需要保留的行为”。
- 区分必需功能与范围外功能；只需 3–5 个语义节点。若没有核对真实 import/call graph，标为概念示意，不画成已证明的源码依赖图。
- 将 source-free boundary 画得比模型图标更突出；模型节点只写 Agent。
- 结果只画功能检查与静态 footprint 两路，不画“正确率越高就越紧凑”的隐含箭头。
- 不展示 hidden 测试断言；不将合法大规模复制直接标红为失败。

建议图注：

> A feature-lifting task exposes an intact source repository and a public contract. The agent reconstructs the declared capability behind a new package boundary; only the submitted artifact enters source-free evaluation. Extraction footprint is measured separately from functional success.

### Fig. 2：构建证据图，不画未经完成的理想审核系统

**布局：上下两层，上层生产题包，下层展示验证证据。**

```text
Pinned source → Feature scope → Public API / behavior clauses → Tests + reference evidence → Frozen task
     │                                │                              │                     │
 source identity                surface / mapping checks       oracle replay          revision / hash

Agent-visible: source + public contract       Evaluator-only: benchmark tests + oracle/reference
```

- 上层表示构建的产物，下层表示可核查记录。Oracle 600/600 等数量保留在验证段落，图中避免密密麻麻的数字。
- 明确：公开契约到测试的映射是需审查的关系，不是“语义公平性已证明”的绿勾。
- 不加入全量 Validator-Agent / 双人审核 / adversarial audit 节点，除非本项目有对应已完成记录。
- 图注区分机械通过与语义审查，语义限制用一行中性说明即可。

建议图注：

> Construction links pinned source evidence, public obligations, executable checks, and a frozen task identity. Recorded mechanical and oracle checks support integrity and feasibility; they do not certify complete semantic fairness of the evaluation.

### Fig. 3：失败阶段，用条形图替代装饰性漏斗

**Panel A：六条水平堆叠条，每条 150 题。** 类别固定为 Pass、Missing、Build、Public、Hidden、Isolation，直接显示数量或百分比。使用相同模型顺序，不按每张图重新排序。

**Panel B：有包样本的 non-exclusive gate flags / Isolation residual。** 采用简洁 dot/bar panel，明确分母 829。若画每模型，分母为各自 delivered n。突出“只有4个产物其他三门通过但Isolation失败”这一窄结论。

注意：非互斥 flags 不能堆叠成总失败原因比例；未执行/连带置失败也不能等同于测试真的运行并产生独立缺陷。根据分析脚本的具体语义标注。

数据源：[funnel.csv](../../reports/paper_analysis/python150_prime_v2_analysis_20260905/funnel.csv)、[independent_gates.csv](../../reports/paper_analysis/python150_paper_analysis_final/csv/independent_gates.csv)。已有视觉底稿：[failure_stage_funnel.png](../../reports/paper_analysis/python150_paper_analysis_final/fig/fig_failure_stage_funnel.png)。

建议图注：

> First outcomes over all assigned tasks (left) and non-exclusive gate flags among delivered artifacts (right). Isolation residual denotes a failure of the separate Isolation gate after Build, Public, and Hidden pass; it does not count every source-dependency error.

### Fig. 4：总体任务通过频次

单面板柱图：横轴为通过的配置数 0–6，纵轴为任务数。七个计数为 28、7、9、22、36、31、17，合计 150。使用单色，不按实验批次或临时标签堆叠。28 题全部失败、17 题全部成功，其余 105 题表现混合。

这张图描述六个已评测配置上的观测结果；不把未通过任务一律解释成有效难题，保留七题敏感性的引用。依赖临时分组的比较和回归退出论文，既有分析文件保留。

数据源为既有逐任务结果，绘图脚本是 `figures/scripts/fig04_difficulty.py`。

建议图注：

> Observed solve frequency on 150 FeatureLiftBench tasks. Bars count tasks passed by 0–6 configurations. These campaign outcomes do not define fixed difficulty tiers.

### Fig. 5：共同成功任务的产物差异

当前正文已接入 `figures/output/figC_paired_footprint.pdf`，保留 `fig:paired-copy` 标签。它以本次通过任务最多的 Pro 为参照，覆盖 Flash、Luna、GLM、Qwen、OSS，五组共同通过任务数分别为 105、97、67、63、33。

两个面板分别展示逐题 RRES 和 Copy 差值，统一定义为“对应配置 − Pro”。蓝点是任务，菱形为中位数，横线为第 25–75 百分位区间。RRES 采用对称对数坐标（±0.1 内线性）保留长尾和零值；Copy 保持线性坐标。各行配对集合不同，不能据跨行差异建立统一任务集上的 footprint 排名。

这张图支持“功能通过后，产物大小与源码重叠仍不同，且两者不能互相替代”。正文保留 Pro/Luna 与 Flash/Luna 的精确配对表，并用 Pro/Qwen 的大小与复制方向对比说明两项指标的区别。该图不增加显著性结论或可维护性主张。

原 Pro/Luna 散点保留为旧版输出。新版复现入口：`figures/scripts/redraw_figures.py`，数据：`figures/data/figC_paired_footprint.json`；不运行新实验或编译论文。

### 暂不放正文的图

- 六配置根因饼图：标注覆盖和审核级别不支持。
- 全模型token/美元成本Pareto图：provider账目口径不齐，Luna/GLM缺可靠token字段。
- 176仓库的大饼图、logo墙、150题密集热力图：不直接回答正文问题；完整inventory放附录。
- 参考代码、模型大小、RRES、token混在一个雷达图：这些量不同义，容易制造误读。
- 旧freeze与新freeze分数的“改进曲线”：不能解释成模型或方法改善。

## 5. 现有证据与图文的一一对应

| 论文用途 | 优先使用的本地证据 | 备注 |
| --- | --- | --- |
| 发布身份、来源、Oracle覆盖 | [current_benchmark_freeze.json](../../artifacts/research_analysis/python200_prime/current_benchmark_freeze.json) | release facts；不自动证明每次run的身份一致 |
| 六配置功能和分层 | [final summary](../../reports/paper_analysis/python150_paper_analysis_final/summary_final.md)、[task_results.csv](../../reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv) | 逐题记录优先于手写状态页 |
| 200题扩展结果 | [python200 v2 results](../../reports/paper_analysis/python200_prime_v2_results_20260905/README.md) | 只用确认过的functional分子；空卷数存在旧口径，需从逐题重取 |
| F3探索性归因 | [annotation summary](../../reports/paper_analysis/python150_prime_v2_analysis_20260905/f3_annotation_summary.json)、[SOP](../FAILURE_ANALYSIS_SOP.md) | Pro+Flash 63，L1非金标；不重标注、不混分母 |
| 同七题排除敏感性 | [known_defect_sensitivity.json](writing/known_defect_sensitivity.json)、[离线脚本](writing/known_defect_sensitivity.py) | post hoc，900键无重复，已对账原始gates；不是新实验 |
| 相关工作定位 | [来源核查笔记](writing/sources.md) | 学术定位使用原始论文，不使用排行榜宣传语 |

## 6. 定稿前需处理的事实口径：离线对账，不新增实验

这些问题不改变大纲，但决定正文可以写得多强。先把结论边界写对，再做图表定稿。

| 项目 | 本轮看到的事实 | 写作处理 |
| --- | --- | --- |
| 150题仓库数 | 按freeze内canonical `source_repo_id`去重为126；按source名称去重会得到127，dateutil / python-dateutil是别名 | 正文写150题/126个canonical仓库；200题为176。同步旧稿的127 |
| 配置是否只有模型不同 | Pro/Flash记录token condenser；其余四家记录default模式 | 共有名义资源信封，但不是完整context policy都相同；实验设置段落明确披露 |
| run freeze身份 | 现有900行中522为v2 ID，378保留前任ID；Flash/Luna/Qwen各有126条前任记录 | 查既有继承/补跑台账及逐题内容等价证据。未核清前称“合并campaign记录”，不宣称900次全是统一v2新运行。现有数值表是已记录结果，跨配置严格可比结论须受此限定 |
| 独立可安装性 | 冻结evaluator允许package path/PYTHONPATH加载和fallback | 任务目标可称独立包；结果称满足当前loading/build策略，不能声称全部wheel或干净安装验证 |
| 7个题缺陷 | 标签是AI初审的invalid candidate，非独立人工最终裁定 | 主表不暗改；敏感性段落对所有配置排除同一组题，说明选择由失败分析得到，非穷尽 |
| 全量语义验证 | 600/600 Oracle支持可行性；没有全量独立human L2审查 | Fig. 2区分执行证据与语义可信性；去掉“全量Validator-Agent已审完” |
| 主结论强度 | Pro–Flash p≈.092、GLM–Qwen p≈.568；Composite all6 p≈.486 | 不作相邻显著排序，不把strong3 p≈.554误写成all6结果 |

以上计数与配置可从冻结manifest、既有suite.json和敏感性JSON复读。核对结果继承所需的是已有文件及内容身份，不要求启动新的agent评测。

## 7. 篇幅与落笔顺序

在尚未固定会议格式时，用正文内容比例控制：Introduction 12%，Benchmark 27%，Protocol/Setup 12%，Results 28%，Diagnostics/Discussion 7%，Threats 5%，Related Work 7%，Conclusion 2%。摘要、参考文献、附录单算。它是写作预算，不是正式页数规定。

**制作顺序：**

1. 先画 Fig. 1 的简单草图：读者能否一句话说明我们测什么。
2. 再画 Fig. 2：流程上的每个框都能对应真实产物或已完成检查。
3. 将功能主结果表与 Fig. 5 做成第一批结果图表：功能成绩和产物差异是论文最重要的两个观察。
4. 完成 Fig. 3、Fig. 4：补足失败与难度解释；敏感性用文字报告。
5. 按这些图表写 Benchmark、Protocol、Results，最后回写 Introduction、Abstract、Conclusion。

**图形实现约定：** 流程图用可编辑SVG/TikZ；数据图用可复现脚本输出矢量PDF和预览PNG，不使用生成式图像制作科学图表。统一模型顺序及指标配色，保证缩到实际栏宽仍可读。所有图保存数据路径、分母、计算规则；每张图注说明适用样本。

大纲完成的判断标准是：每个章节都回答一个必要问题，每个主要结论都对应证据，每张正文图都推动故事。下一阶段按这一大纲制作草图和段落，不再沿旧稿中的历史版本和方法探索展开。
