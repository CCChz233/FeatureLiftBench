# Fig. 1/2 定稿后的正文配图方案

日期：2026-09-11。本文记录配图方案与执行状态。
Fig. 1/2 已定稿并接入 `main.tex`；Fig. 3 已完成重画和正文同步。
比较圆环方案后，最终选定 **堆叠条形图 + 热力图**，正文与 Overleaf 包均采用 `figA_task_coverage.pdf`。圆环图仅保留为设计对照。
未运行实验或编译论文。

执行更新：同日已完成 Fig. 3 的两面板重画并同步 LaTeX。左图为完整 200 题功能族的堆叠条形图，颜色表示提取类型（68 / 100 / 32）；右图为共同 150 题机制热力图。额外 50 题的本地源码只有归档指针，无法补齐与 v2 一致的源码派生标签，因此未将它们混入热力图。两个统计范围在图中分别注明；200 行分类索引保留机制字段缺失状态。以下为执行前的方案记录，目标全量机制热力图尚未实现，当前状态以本段及 `README.md` 顶部为准。

## 正文维持五张图

| 图 | 回答的问题 | 内容与统计范围 | 下一步 |
| --- | --- | --- | --- |
| Fig. 1 | 为什么需要 feature lifting，任务是什么？ | 复用需求、跨包边界重建、source-free evaluation | 已定稿，保留 |
| Fig. 2 | 任务如何构建并验证？ | Construction、validation、200-task release | 已定稿，保留 |
| Fig. 3 | 这套 benchmark 覆盖哪些功能和任务结构？ | 左：完整 200 题的功能族与提取类型；右：共同 150 题的机制热力图 | 已定稿并同步正文；圆环方案保留为备选记录 |
| Fig. 4 | 功能失败集中在哪些评测关卡，任务通过频次如何分布？ | 六配置共同 150 题；首个结果分布 + 0–6 配置通过的任务频次 | 已整理字号、留白和图例，保留原始数据 |
| Fig. 5 | 同样通过的任务，产物实现有何差异？ | 各配置与 DeepSeek V4 Pro 的共同成功任务；配对 RRES/Copy 差值 | 已整理图注与参照术语，保留全部配对差值 |

图序对应：任务价值 → 构建可信度 → 数据覆盖 → 功能表现 → 成功产物差异。
综合主表已经容纳 Steps/Tokens；目前不需要再做一张重复各模型效率汇总的柱状图。
Section 5 的案例可继续使用紧凑文字/表格，暂不增加第六张正文图。

## 可以借鉴的论文画法

1. [SWE-bench，ICLR 2024，Fig. 3](https://arxiv.org/pdf/2310.06770)：展示 12 个仓库分别贡献的任务数量，是仓库来源分布，不是每道题的语义分类。应借鉴它在结果之前交代数据覆盖的作用。
2. [SWE-Bench Pro，官方 2025 年版本，Fig. 3](https://static.scale.com/uploads/654197dc94d34f66c0f5184e/SWEAP_Eval_Scale%20%289%29.pdf)：将任务分布用于说明任务类型与多文件任务覆盖。不同版本图号可能变化，本文特指链接中的版本。

FeatureLiftBench 的 176 个仓库中，166 个各贡献一道题。按仓库画 176 扇区的饼图无法帮助比较，不建议照搬。

## Fig. 3 推荐布局：两个面板

建议标题：**Functional breadth and task-structure coverage of FeatureLiftBench**。

### 左：What capabilities are lifted?

用按数量排序的横向条形图展示现有十个功能族，直接标注任务数。
功能族沿用当前 Section 2 的 inventory，表示“提取什么功能”，不新增难度等级。
十行短标签的横向条形图可读性优于十色饼图；不需要给每类再配图标或定义框。

当前 `writing/chapter2_task_inventory.json` 的完整 200 题计数：

| 功能族 | 任务数 |
| --- | ---: |
| Registry / plugin dispatch | 38 |
| Parsing / tokenizing / decoding | 37 |
| Configuration resolution / discovery | 26 |
| Validation / normalization / construction | 22 |
| Serialization / formatting / rendering | 19 |
| Workflow / session orchestration | 14 |
| Resource / metadata loading | 14 |
| Algorithms / data structures | 11 |
| Protocol state transitions | 11 |
| Cache / retry policies | 8 |

这些是已经在正文描述的功能族。它们与“三类提取任务”和“四类缠绕机制”回答不同问题，不是再将四类机制拆回十类。

### 右：How are tasks structured?

沿用当前图有价值的 3 × 4 热力图：

- 行：Direct、Adapted、Composite；行标题标出各自任务数。
- 列：Code dependencies、Data and state、Framework mechanisms、Environment and resources。
- 单元格：属于该机制的任务数 / 该提取类型任务数，配合类内比例着色。
- 同一道任务可有多个机制；百分比不要求相加为 100%。

目标是两个面板都覆盖完整 200 题。现有完整 inventory 的提取类型为 Direct 68、Adapted 100、Composite 32；当前图的 56、76、18 仅属于共同 150 题。

绘图前的数据整理要求：

1. 按冻结任务 ID 连接全部 200 题，不能将当前 150 题热力图仅改标题后当作 200 题。
2. 全量 taxonomy CSV 的 200 个 ID 与正文 inventory 一致，200 条原始机制标签与对应任务 metadata 一致，本轮已检查。
3. 额外 50 题的派生标签目前来自 `ledger_seed`，150 题来自 `v2_full`。扩展热力图时须使用统一派生规则，避免将未派生的细标签算成“机制不存在”。这属于标签数据整理，不需要运行模型实验。
4. 功能族使用当前正文 inventory 的归一化字段；不要直接使用旧 CSV 的 `feature_family_selection`。该字段仍包含 `direct_tooling_copytrap` 等内部构建名称，与正文十个功能族不是同一口径。
5. 全量机制映射尚未统一前，当前 150 题热力图仍按原范围使用，不预先发布 200 题机制百分比。

分类图只说明覆盖与共现，不用于推出 Direct → Adapted → Composite 的固有难度排序。当前 RQ3 的控制分析已经指出该表面梯度受构建批次组成影响。

## “每道题都有分类”如何呈现

正文汇总分类分布，任务级索引保留每道题的功能族、提取类型、机制标签。
如果希望读者直接看到每道题，可在附录增加任务分类矩阵：每行一个任务、按功能族分组，提取类型作为侧栏，四个机制作为二值列。200 行应分组/分页或用短 ID 配索引，不挤入正文单幅小图。

不建议把功能族、提取类型、四类机制做成一棵旭日图：三者不是既定的父子分类层级，且机制是多标签。饼图只能用于互斥分组，不能用于四类机制的占比。

## Fig. 4/5 的小幅整理

- Fig. 4：保留完整模型名、各阶段首个结果和通过频次。大段解释移入 caption；首个失败关卡不等于因果根因。
- Fig. 5：保留每组配对任务数、逐题差值、中位数与 IQR。图中 `than the reference` 应明确写 `than DeepSeek V4 Pro`，避免与 RRES 分母中的 reference implementation 混淆。低 RRES/Copy 不自动意味着更高质量。
- 构成图使用完整 200 题；六配置主结果使用共同 150 题；配对图使用各自共同成功集合。每张图的分母在图注中明确。

## 执行状态与后续

1. 已完成：重画 Fig. 3，保存 200 行任务索引和计数检查；机制统计采用明确标注的共同 150 题。
2. 已完成：将新 Fig. 3、caption 和 Section 2 数字同步到 LaTeX，更新 Overleaf 包。
3. 已完成：比较圆环备选，选定堆叠条形图与热力图作为正文版。
4. 已完成：整理 Fig. 4/5 的文字与版式，不改变分析问题或统计数据。
5. 按用户当前要求保持不编译论文、不运行实验。
