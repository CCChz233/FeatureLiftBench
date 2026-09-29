# 软件工程主线修订计划

> **Status: archived · Historical paper record**

日期：2026-09-18。版本：v2，按作者意见收缩为四个里程碑。状态：40 条 pilot 已冻结；161 条扩展案例已分析，201 条候选本轮分析完成。作者已确认原 90 条疑点经人工复核有效。合并后 176 条行为语义违反、22 条 API 缺失、1 条产物约束问题、2 条证据不足，0 条待处理；Fig.6/Table 5、RQ3 及全文相关数字已更新。没有新增模型实验。

本计划落实作者确认的方向：以 agent-mediated behavior-preserving software reuse
为研究中心，围绕新包边界上的行为义务组织论文。六个配置是观察这一能力的实验系统；
结论限于本基准与这些配置，不外推到人工复用或所有软件项目。

正文入口是 [main.tex](../../../paper/main.tex)。本计划规定本轮论证与分析工作顺序；
旧图形布局、冻结结果和正式资产在有证据支持的替换前继续保留。

## 1. 研究主张与证据边界

工作 thesis：

> Feature lifting requires preserving behavioral obligations whose implementation
> may depend on relationships beyond the apparent entrypoint.

待检验的核心问题：哪些行为义务未被保留，它们依赖哪些支撑关系，提交如何改变了这些关系？

正文使用 behavioral obligations and their supporting relationships，
不把 behavioral closure 引入 Introduction/Abstract 作为中心术语或正式测量对象。
如 Discussion 最终使用该词，只作概括，不声称完整闭合、最小切片或 reference 定义了 closure。

研究链条：repository evidence → observed source exposure → behavioral violation
→ supporting software relationship → implications for cross-boundary reuse。
箭头表示叙述和证据组织顺序，不表示已经识别的因果链。

本轮只完成下文四个里程碑。不默认增加模型、扩题、因果分析、全基准属性机会标注或复杂统计模型。

| 层次 | 当前可支持的内容 | 还不能支持的内容 |
| --- | --- | --- |
| Repository evidence | Full Source 与 Contract Only 的配对差异 | 单独隔离源码文本的因果作用；Pro 差异全来自语义重建 |
| Observed source exposure | 241/303 次行为首败已有入口关联文件内容的确认读取 | 完整定位、理解、依赖追踪已完成；定位问题已解决 |
| Behavioral preservation | 冻结分类与已有逐例观察 | 状态或交互最脆弱；所有 drift 都是边界闭合问题 |
| Verification / termination | 首次观察到通过之后仍有执行 | 浪费比例；agent 不知道已完成；可安全提前终止 |
| Implementation footprint | 成功产物的大小与文本重合度 | 有意识的 reuse strategy；维护性；语义优越性 |

既有主表保持为冻结协议的结果。新的有效性裁决若确认影响结论，需另行提供
受影响任务/配置清单和敏感性结果，并评估主表是否需要显式修订；不得静默改标签或选择性删分母。

## 2. 本轮已实施的低风险改写

- Introduction 的核心问题改为跨包边界的行为保留问题，明确通过 coding agents 研究。
- 第三项贡献改为 agent-mediated, behavior-preserving software reuse 的实证研究。
- RQ1 加入 reuse structures；用已有 Table 2 解释 changing/composing capability boundaries 的描述性关联。
- RQ2 明确 observed behavioral sufficiency 的有限含义，保留 token 与响应的真实观测口径。
- RQ3 改为 behavioral obligations / supporting relationships，并加入平台路径、嵌套诊断、资源遍历三个成功／失败对照。
- Discussion 据此讨论支撑关系，以及保留上游行为与满足新增适配义务之间的区别。

当前新增了可追溯的 L1 语义案例与 codebook 草案，尚无经第三方审核的新属性构成结果。
此处为早期进度记录；2026-09-19 已完成 Fig.6/Table 5、Abstract/Conclusion 更新，正文不再使用旧 201/228 结论。

## 3. 里程碑一：建立 SE taxonomy

### 3.1 为新分析建立可分析集合

输入：

- [失败细分首轮记录](../../../paper-workbench/data/failure_subtypes_20260918/README.md)及其 summary/annotations。
- [失败分析协议](../../../FAILURE_ANALYSIS_PROTOCOL.md)和 [SOP](../../../FAILURE_ANALYSIS_SOP.md)。
- 冻结逐题结果、公开契约、pinned source、提交和失败日志。

当前 201 条原 behavior-drift 记录中：74 条首轮已赋子类且未记录疑点，
86 条为候选子类并有契约/解释疑问，41 条需复核父类别。
74 条也只是旧版初步分析；127 条待复核并不等于 127 个基准缺陷。

这组数字用于安排已有问题的核查，不意味着重新审计整个 benchmark，也不要求先重判全部旧 taxonomy。
每条候选按下列顺序处理：

1. failure 是否确实违反冻结的 public behavioral obligation；
2. 能否确定 violated behavioral property；
3. 能否识别 supporting relationship；
4. submission 如何偏离该义务及支撑关系；
5. 只有出现直接证据表明旧 coarse primary 不适用时，才提出父类别修订。

保留 original_primary；revised_primary 默认空，只有实际提出修订时填写。
性质可判定但关系不清的案例仍可进入属性构成，relationship 标 unresolved；
契约违背本身尚不可判定的案例留在候选流转表，不进入已确认属性分布。
明确区分契约/评测疑点、证据不足、未知属性与未决关系，不一概当作 benchmark 缺陷。
核对既有 241 → 228 的 13 条排除原因，避免与新疑点集合混淆或重复扣除。

范围设计：默认候选池为既有 201 条 behavior-drift 记录，结论明确限定这个来源及其可分析子集。
其余 27 条旧类别不设为全量重审任务；仅在 pilot 暴露明确漏项，或需要构造支撑关系案例时定向检查，
并另记来源和分母。未确认源码暴露的失败不自动纳入。

交付：带 case/run/task 身份、原判定、新判定、证据指针、裁决理由和复核状态的 ledger；
从候选集合到可分析集合的可复算流程表。

无需等待 201 条全部裁决才开始 pilot。开发时保留疑难案例来检验边界，
统计时对未决项单列，不为了完整图形强行归类。

### 3.2 40-case pilot 与 codebook

已准备[pilot 材料](../../../../reports/paper_analysis/se_obligations_pilot_20260918/README.md)：
40 条来自 40 个独立任务，30 条 development、10 条 rule check；覆盖全部六配置、
十个功能族和三种 lift type（Direct 10、Adapted 19、Composite 11）。
选择清单与两份无预填标签的独立标注表保持原样。另存的初步分析已完成 30 条 development：
8 条 L1 暂确认公开义务违背（其中 1 条建议 API completion），21 条契约解释未决、1 条证据不足。
这是有目的的规则开发样本，不用于估计总体比例；未决不等于缺陷。
见 [readout](../../../../reports/paper_analysis/se_obligations_pilot_20260918/DEVELOPMENT_READOUT.md)、
[codebook v0.1](../../../../reports/paper_analysis/se_obligations_pilot_20260918/CODEBOOK_v0.1.md) 与
[三个对照案例](../../../../reports/paper_analysis/se_obligations_pilot_20260918/PAIRED_CASES.md)。

建议第一轮 40 条：约 30 条用于类别开发、10 条用于冻结草案后的新案例检验。
优先覆盖不同任务，再兼顾 lift type、配置、功能族及已有复核状态。
开发集可以有意纳入边界案例，不用其比例估计总体分布。
新案例检验若导致规则变更，标记为第二轮开发，并保留规则版本与重标记录，
不得仍称未见过的验证集。试标前冻结 case ID、选择理由和阶段身份。

两位作者独立标注时不看对方标签；证据准备与独立复核是不同步骤。
按现有协议报告裁决前一致性及类别混淆；互斥 primary 用 κ/α，多标签逐标签报告，
不把达成共识后的标签拿去计算独立一致性。
避免用一个阈值代替边界分析；若主要类别反复混淆，修订定义后重标受影响案例。

### 3.3 三类信息分开记录

| 信息 | 问题 | 标注原则 |
| --- | --- | --- |
| 既有 primary cause | 旧粗分类是否存在明显需修订之处？ | 保留原值；只在必要时提出修订，不作为每条主任务 |
| Behavioral property | 什么公开可观察义务未被保留？ | 一个主要属性，可加 secondary tags |
| Supporting mechanism | 上游靠什么关系实现此义务？提交如何处理？ | 必须有源码/提交证据；允许多标签与 unresolved |

行为属性候选定义（不是预设最终分类，更不是已有计数）：

| 候选属性 | 操作定义 | 与邻类的边界 |
| --- | --- | --- |
| Call compatibility | 已存在 API 对公开参数、绑定或输入形式的接受方式不兼容 | API 本身缺失记为例外并按需提出父类别修订 |
| Value / representation | 返回值、结构、解析或序列化结果违反公开约定 | 可加 parsing/formatting 领域标签；不作为剩余错误桶 |
| Validation / exceptions | 输入接受/拒绝、警告或异常类型与条件不兼容 | 异常只是症状时不要自动归此类 |
| Defaults / precedence | 缺省值、配置覆盖或选择优先级违反约定 | 与结果错误重叠时用更具体义务为主 |
| Ordering / identity | 顺序、对象身份、别名或相等协议是被违反的义务 | 数据值相同但 identity 不同可属于本类 |
| State / lifecycle | 随调用变化的状态、清理、重置、对象寿命违反约定 | 如已存在显式状态义务，以此为主，交互可作 secondary |
| Cross-API interaction | 公开要求的多个操作组合不兼容，不能只凭接口存在判断完成 | 必须有关系证据；不声称各 API 单独通过，除非实际验证 |

上述候选包含重叠，pilot 要验证 primary 决策顺序；不能为了互斥强迫未知案例归类。
支撑机制沿用四大类，但区分 task-level entanglement 与 case-specific mechanism：
任务带 Data/state 标签，不代表该次失败由状态造成。Framework/resources 不与异常等行为属性并列成一个互斥轴。

### 3.4 案例证据与轻量记录

1. 冻结的公开 clause ID 与其语义；
2. pinned source 中支撑此语义的实现关系及定位；
3. 提交中对应实现及具体差异；
4. 评测中可观察到的契约违背；
5. 差异是否涉及义务遗漏/关系改变、只是局部实现不一致，或无法确定；
6. 可提出的验证建议及其证据限制。

支撑关系证据用于能识别的案例；不能识别时填 unresolved，不阻塞已确认的属性分析。
详细三方实现对照集中在 3–5 个案例，不要求全量案例都达到同等叙述深度。
第五步描述输出与实现关系，不断言边界变化在因果意义上造成 bug。
若要解释 agent 为什么遗漏，必须另查轨迹，不能从提交反推心理过程。
最小修复或验证 probe 若未实际执行，只能标为建议。

建议新增字段（扩展 sidecar，保留现有 CSV 必需字段和冻结文件）：

`case_id`, `task_id`, `model`, `suite_id`, `original_primary`, `revised_primary`,
`validity_status`, `review_stage`, `codebook_version`, `contract_clause_ids`,
`behavior_primary`, `behavior_secondary`, `task_entanglement`, `case_mechanisms`,
`source_relation_evidence`, `submission_difference_evidence`, `failure_evidence`,
`boundary_relation_status`, `reviewer_1_label`, `reviewer_2_label`, `adjudication_reason`,
`independent_human_review`。

私有证据引用和公开脱敏摘要分开；不在论文或公开附件导出隐藏测试名、输入与断言。

## 4. 里程碑二：完成核心分析

codebook 稳定后覆盖确定范围内全部可分析案例，pending/unknown 独立保留。
既有人工复核不自动等于对新 codebook 的复核。
按现有 Protocol §9 完成第三方抽样与全部 unknown/缺陷候选/Hidden-only 的审核，
记录真实覆盖；AI 多次检查不写作第三方审核。

另建立 3–5 个可追溯的同任务成功/失败对照：

- 在已标注机制中选择证据最完整的若干不同任务，覆盖不同机制，不按效果大小挑选。
- 阅读成功提交如何满足同一个契约义务，不以 reference 替代 agent 成功提交而不声明。
- 固定契约，比较上游、失败提交、成功提交三者的支撑关系。
- 若没有合适成功对照，明确其为单个失败案例，不制造配对。
- 解释可观察实现差异，不宣称配对消除了配置差异或识别了因果效应。

交付：全量标注、裁决前一致性、裁决日志、分母流程表、脱敏案例卡。

## 5. 里程碑三：重做 RQ3

最终目标标题：

> RQ3: Which behavioral obligations fail to survive feature lifting, and what
> software relationships support them?

只有关系分析与案例完成后，才将该标题接入主稿。
Fig.5 = failure boundary；Table 4 = source exposure；Fig.6 = behavioral obligations；
Table 5 = taxonomy definitions/counts；案例解释 supporting relationships。

默认主指标：reviewed failure composition，计数同时报告 runs 与 distinct tasks。
若只检查首个失败，则图名、表注与结论明确是 first-observed violation，不表示所有错误全貌。

| 统计目标 | 所需分母与证据 | 当前默认 |
| --- | --- | --- |
| 已复核失败构成 | 明确范围内可分析失败；pending/unknown 单列 | 是 |
| 带属性任务的整体失败率 | 所有相关任务先做不依赖结果的属性标注，包含成功运行 | 可选，不等于属性自身失败率 |
| 属性级失败率 | 属性存在、可评测机会、通过/失败/未观察状态；处理首败阻断 | 暂不承诺 |

默认 finding 形式：Among reviewed source-exposed behavioral failures in the stated
analysis set, the violated obligations most commonly involve X, Y, and Z。
X/Y/Z 必须由最终数据产生，不预填。缺少属性机会分母不阻碍这类构成性结论。
只在已有数据可低成本给出独立且适当分母时考虑升级；不为“X 最难”重标全部 150 tasks。

Fig.6 的必须项与可选项：

- Panel a 必做：Behavioral properties in reviewed source-exposed failures；标明分析集合、分母、未决数量和独立任务数。
- mechanism heatmap 可选：仅当交叉关系体现非平凡模式，且跨独立任务有足够证据时采用；不以显著性或视觉好看为选择标准。
- 不因“state 行对应 data/state 列”就宣称新 insight；检查同义反复、稀疏单元和多标签重复计数。
- 默认的关系解释用对照案例；Fig.6 右侧可呈现三个精简案例，其余放正文/材料。不强制双 panel，也不强制 7×4 热图。
- 配置分组是敏感性/补充视角，主视觉不回到六模型排名。

Table 5：最终属性定义、纳入/排除边界、脱敏表现、n/N；注明 primary 或多标签规则。
完整 codebook、争议案例与复核过程放复现材料。

不为显著性增加复杂模型。若需要区间，考虑同任务跨配置重复，按任务聚类，
必要时检查仓库聚类；这些区间不消除选择偏差，也不创造未观察属性的分母。

允许的结论强度随证据递进：

1. 在 reviewed failures 中出现哪些属性；
2. 在若干独立任务中，哪些支撑关系与具体不一致对应；
3. 只有有适当属性机会分母与可比观察时，才比较属性级脆弱性。

若多数案例只是一般局部实现不一致，应如实收窄 thesis；不能强制所有案例解释成跨边界关系丢失。
验收标准：遮住配置名字，Fig.6 仍能说明哪些义务被违反，以及经验证案例中支撑关系如何被处理。

## 6. 里程碑四：全文换主语并收口

| 位置 | 修改任务 | 前置条件 |
| --- | --- | --- |
| RQ3 | 采用上文英文标题；依次讲边界、暴露、属性、案例 | 完成里程碑二/三，不预写状态最脆弱 |
| Discussion | 用已验证关系给出行为边界、源码证据、契约验证的具体启示 | 区分观测发现与未测试工具建议 |
| RQ1 | 保留 Table 1；Table 2 强调改变/组合能力边界的描述性关联 | 不将分类当因果难度 |
| RQ2 | Observed behavioral sufficiency and run termination can be substantially separated；Discussion 再提出 verification/stopping 方向 | 不推断浪费、completion belief 或缺少可靠信号 |
| RQ4 | source as reuse evidence；连接 RQ3 的具体义务 | 保留 Pro 非完成、补跑及整仓干预限制 |
| RQ5 | successful implementation footprint，缩减叙事比重 | 不从 Copy 推断策略或质量 |
| Introduction / Contributions | 以最终结果概括 SE 问题与经验认识 | 第一轮 framing 已做，最终再对齐 |
| Abstract / Conclusion | 选最有支撑的语义发现替换泛化 drift 数字 | 数字、范围、复核状态确认后最后改 |
| Captions / Threats / Artifact | 统一样本、首败、标签重叠、抽样与泛化边界 | 全文结果冻结后 |

最终验收：

- 每条主要 SE 结论能追溯到公开义务、源码、提交、评测和明确样本范围。
- 不以源码暴露证明完整定位，不以时间间隔证明无可靠停止信号，不以 footprint 证明策略。
- 不混用原 201、228、241、303 与裁决后的新集合；主表影响有显式评估。
- 生成表、图形数据和正文一致，静态引用检查通过，之后单独完成 PDF 排版验收。
- Data Availability 与实际匿名材料一致，公开内容经过隐藏测试与身份信息检查。

## 7. 职责与当前进度

当前写作口径：正文统一描述“我们分析了案例”；台账用已分析、未决、待处理表示状态，不按人工或 AI 分类。独立双人复核只按实际完成的范围描述，原始 A/B 记录保留。历史初审记录不因措辞统一而升级为已核实结果。

执行任务：证据索引、逐案例分析、统计与图表、文字改写和一致性检查。复核记录包括 40 条 A/B pilot，以及作者明确确认的原 90 条疑点复核；不推断后者的双人独立设计或一致性统计。

- [x] 第一轮有现有证据支持的 framing 调整。
- [x] 将范围收缩为四个里程碑，明确 heatmap 和属性级分母不是必做项。
- [x] 准备 40 个不同任务的 pilot 清单及独立空白标注材料（不是完成人工标注）。
- [x] 40-case pilot 工作簿：开发集裁决、`reviewer-v0.2` 冻结、人员C 检查集独立对照。
- [x] 201 条候选台账与可复算分母流程（40 条 pilot + 161 条扩展分析已导入；0 条 awaiting v0.2）。见 [se_obligations_ledger_20260918](../../../../reports/paper_analysis/se_obligations_ledger_20260918/README.md)。
- [x] 剩余 113 条按 v0.2 完成分析；合并首败阶段、真实 suite、证据摘要与可复算分母。
- [x] 原 90 条契约疑点已依据作者明确确认解除；剩余 2 条证据不足单列。
- [x] 导入作者确认的 90 条复核结论并保留旧判断；方法部分按实际复核范围描述。
- [x] 全量候选分析、unresolved 单列、runs 与不同任务数统一：176 条属性记录／68 个任务。
- [x] 对照案例收口：核对现有 3 对成功/失败证据。
- [x] 里程碑三：新 Fig.6 / Table 5 与 RQ3。
- [ ] 里程碑四：全文最终收口与排版、匿名材料验收。

### 2026-09-19 初次分析收口（复核前历史）

本轮新增 113 条并逐提交修订 RID 41、42，201 条候选均已处理。行为属性组成以 106 条为分母，不能解释为各属性失败率。旧 201/228（88.2%）不再作为本轮确认的漂移比例；另 27 条原粗分类记录没有重新审核，主实验通过率也没有重算。最新数字、逐条未决理由及复算命令统一见[台账说明](../../../../reports/paper_analysis/se_obligations_ledger_20260918/README.md)。不另建人工填写材料。

### 90 条复核通过后的当前结果

作者在会话中明确确认原 90 条疑点已通过人工复核，并要求合并。当前：176 条行为语义违反（106 + 70）、22 条 API 缺失（3 + 19）、1 条产物约束问题，共 199 条已确认失败；2 条证据不足保留。合并后的属性分布和不同任务数以[台账说明](../../../../reports/paper_analysis/se_obligations_ledger_20260918/README.md)为准。原疑点理由保存在台账 pre_resolution，A/B/C 原始记录不覆盖。下一步图表使用 176 条行为属性分母，不将 API 和产物约束问题混入该分布。

### 2026-09-19 论文集成

已完成：Fig.6 改为属性构成图；Table 5 改为 codebook 定义、run 计数及不同任务数；RQ3、方法、摘要、Discussion、Threats、Conclusion 统一分母。176 条覆盖 68 个任务；前三类 122/176=69.3%，仅表示样本构成。原 27 条其他粗分类不混入新分母，2 条证据不足保留。三组对照案例的契约、源代码、提交及保存的 gate 结果已核对，不声称因果干预或新增双人独立复核。

论文图表共用 `behavioral_obligations.py`；精简机器数据放在已有 data 目录，没有新增人工填写文档。新图单独预览后接入论文。后续是整稿排版与匿名复现包核对，不再扩充人工标注范围。

### 2026-09-19 编译与排版检查

作者已允许编译。`build/main.pdf` 编译成功，共 23 页，参考文献从第 22 页开始。已查看整稿页面，放大检查主结果表及 RQ3/RQ4 图表；修正 Table 1 模型名的两端对齐拉伸，以及 Fig.7 提前浮到 RQ3 案例中的位置。无 overfull、未解析引用或编译错误，仍有 3 条页内留白提示。数字校验通过，模板字号与边距未改。页数上限尚未按目标投稿年份/track 核验；正文压缩属于后续内容编辑。

### 作者参考版表格排版（2026-09-19）

仅迁入作者提供的表格样式：主表固定名称列、两位小数及 10^4 token 单位；其他结果表使用分组表头、明确列宽和 small 字号。新 Table 5 保留 176 条属性分析，Table 8 保留当前四列内容，仅调整样式。生成器已同步，避免重新生成覆盖排版。正文（除浮动控制）、统计数据与结论均未改；数值显示精度和单位换算已检查。编译 24 页，参考文献从第 22 页开始，无 overfull 或 underfull hbox；页数仍超首次投稿限制，本轮未做内容压缩。
