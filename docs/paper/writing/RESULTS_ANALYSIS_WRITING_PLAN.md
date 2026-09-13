# 实验结果的解释与正文写法

## 1. 结论与证据范围

实验部分应围绕一个问题组织：**源仓库中的已有能力，能否在新的包边界下保持行为？**

现有结果支持三条主要发现：

1. 当前配置能够完成相当一部分 lifting 任务，但仍存在多个配置共同未解决的任务。
2. 较强配置可靠地交付包，行为覆盖仍然是主要失败环节；其他配置还暴露出不同程度的交付和构建问题。
3. 在同一任务上都成功时，产物的大小与直接源代码重合度仍有系统差异；通过率不能完整描述产物。

这三条足以构成 benchmark 的基线和诊断分析。不能扩展成“已全面揭示模型内部推理策略”“多数失败是定位后的依赖闭包错误”或“低重合度代表更好的重构能力”。

范围：200 题 benchmark；六配置共同的 150 题主比较；五配置另有 50 题扩展结果。本文档的条件比例和成功集合分析均使用主比较的 900 条实际记录。Source ablation 的预测占位没有进入任何计算。

来源：

- 当前输入声明：`docs/paper/paper_sources.json`。
- 任务级记录：`reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv`。
- 已有配对统计：`reports/paper_analysis/python150_paper_analysis_final/json/stats.json`。
- 当前正文的 RQ1–RQ4 与第五章案例分析。
- 新增描述性复算：`docs/paper/writing/analyze_results_narrative.py`；输出 `results_narrative_evidence.json`，含输入 SHA-256。

复算命令：`python -B docs/paper/writing/analyze_results_narrative.py`。脚本确认 900 个不重复配置–任务对、每配置同一组 150 题，以及主通过数和 solve frequency 一致；不运行 agent 或 evaluator。

## 2. RQ1：能力水平与共同未解决的任务

### 应当解释什么

六配置通过率为 76.7%、72.0%、68.0%、45.3%、42.0%、24.0%。保留完整主表，但正文不逐格复述 footprint 和效率；那些数字在后续问题中解释。

比最高通过率更有解释力的集合关系：

- Pro 通过 115 题；六配置成功集合的并集为 122 题（81.3%），仅增加 7 题（4.7 个百分点）。
- Pro 的 35 道失败题中，28 道也被其余五配置全部失败，即 80.0%。
- Pro/Flash/Luna 的成功并集为 121 题。这个细节可放分析记录，不必再挤进主文。
- 28 题全失败、17 题全成功、105 题结果混合，说明同时存在共同未解决的任务和配置间差异。

因此可以写“单纯在这六个已运行配置之间进行事后选择，只能覆盖有限的额外任务”。不能写“多模型协作没有用”，因为没有执行协作、选择或额外重试实验。并集不是一个实测系统的通过率，也不构成未来模型上限。

配对检验保留 Pro/Flash 的 10 对 3 独占成功（p=0.0923），避免把点估计排序当作已确立的严格能力排序。Pro/Luna 的 p=0.0106 是未校正值，若强调多模型显著性需统一多重比较策略；当前无需增加这种主张。

### 英文正文建议

> Across the six configurations, functional pass rates range from 24.0% to 76.7% on the same 150 tasks. DeepSeek V4 Pro achieves the highest observed rate, followed by DeepSeek V4 Flash and GPT-5.6 Luna. The differences are not a strict statistical ranking: Pro and Flash have ten and three exclusive successes, respectively, and their exact paired comparison does not establish a significant difference (p=0.0923).
>
> The remaining failures are substantially shared. Taking the union of all six configurations' recorded successes covers 122 tasks (81.3%), only seven more than Pro alone. Of Pro's 35 failed tasks, 28 are failed by every configuration. Thus, the evaluated configurations leave a common set of unresolved tasks, alongside task-specific differences in success. This union is a retrospective coverage calculation, not the measured performance of a selection or ensemble system.

段落重点：**已有显著能力，但当前配置共同留下未解决范围。** 不把全失败等同于任务不可解或固有难度。

## 3. RQ2：分开交付可靠性与行为覆盖

### 从任务级记录复算的条件比例

| 配置 | 成功/150 | 可用提交 | 成功/可用提交 | Build、Public 均通过 | 其中 Hidden 失败 |
|---|---:|---:|---:|---:|---:|
| DeepSeek V4 Pro | 115 | 150 | 76.7% | 125 | 10/125（8.0%） |
| DeepSeek V4 Flash | 108 | 150 | 72.0% | 124 | 15/124（12.1%） |
| GPT-5.6 Luna | 102 | 144 | 70.8% | 114 | 12/114（10.5%） |
| GLM-5.3-Flash | 68 | 112 | 60.7% | 78 | 8/78（10.3%） |
| Qwen3.6-35B-A3B-FP8 | 63 | 125 | 50.4% | 84 | 21/84（25.0%） |
| GPT-OSS 120B | 36 | 148 | 24.3% | 60 | 23/60（38.3%） |

这些比例用于诊断，不替换以 150 为分母的主分数。每个配置的条件集合不同，不是校正后的模型排名。“若解决未交付即可达到条件通过率”也不是这些数据支持的反事实结论。

### 应当形成的解释

**交付和行为是两类不同问题。** GLM 的 38 次未交付明显影响总分；即使在 112 份可用产物中，也有 44 份未成功。OSS 只缺交 2 份，却只有 36 份成功；主要问题不能归结为没有完成交付。

**强配置仍主要在行为环节失分。** Pro/Flash 的 77 次失败中，51 次首先失败于 Public，25 次首先失败于 Hidden，1 次首先失败于 Isolation。合计 76/77=98.7% 的首次失败位于行为门槛。77 是配置–任务失败结果数，不是 77 道不同任务。

**Hidden 检查提供额外区分。** Pro/Flash 中已经通过 Build 与 Public 的 249 份产物，仍有 25 份失败于 Hidden（10.0%）。这比“隐藏测试失败很多”更准确，因为排除了更早已失败的产物。Qwen 和 OSS 对应条件比例为 25.0% 和 38.3%。两组 benchmark 测试均被保护，因此不要使用“对公开测试过拟合”的解释。

**Isolation 单独决定分数较少，不代表独立运行约束无用。** source-free 环境已经可能在 Build 或行为测试阶段暴露依赖问题。没有 source-present evaluator 对照，不能判断取消隔离会有多少额外成功。

### 英文正文建议

> Failure profiles separate delivery reliability from behavioral correctness. DeepSeek V4 Pro and DeepSeek V4 Flash submit usable packages for all 150 tasks and have no Build-first failures. Nevertheless, 76 of their 77 combined failures first occur at Public or Hidden behavioral gates. In contrast, GLM-5.3-Flash and Qwen3.6-35B-A3B-FP8 produce no usable submission on 38 and 25 tasks, respectively. GPT-OSS 120B usually delivers an artifact, but 18 Build-first and 93 Public/Hidden-first failures limit its overall success. Different configurations therefore lose performance at different observable boundaries.
>
> Passing the earlier checks does not ensure complete behavioral coverage. Among the 249 Pro/Flash artifacts that pass both Build and Public, 25 (10.0%) fail Hidden. The corresponding conditional failure rates are 25.0% for Qwen and 38.3% for OSS. These results show the additional discrimination provided by the Hidden checks after the preceding gates have passed. Because both benchmark test groups are withheld, they do not demonstrate overfitting to agent-visible benchmark tests. Gate outcomes identify where correctness is lost; the artifact cases in Section 5 examine how particular mismatches arise.

建议保留现有 Fig4，不为上述比例新增一张正文表。两段分析即可提高现有图的信息价值。

## 4. RQ3：描述任务差异，不把构建标签当作失败原因

当前最明确的结果是：28 题全失败，105 题混合，17 题全成功；全失败中的 22 题集中在共同 150 题内部的一个 50 题构建批次。这个内部批次不是扩展评测的另外 50 题。

构建批次的回归 OR=0.149，说明在已纳入协变量后仍有关联，不说明“构建批次导致困难”。控制模型和批次后 Composite 对 Direct 的 OR=0.655、p=0.486，意味着当前分析没有建立独立关联；不是证明两个类别等难。

主文顺序建议：solve frequency → 与构建组成的关联 → 为什么不把三类提取当成难度等级。四类缠绕机制保持组成描述，不能用覆盖高度重叠的类别通过率给机制难度排序。

### 英文正文建议

> Task outcomes span shared success, shared failure, and configuration-specific success: 17 tasks are passed by all six configurations, 28 by none, and 105 have mixed outcomes. The all-fail group is concentrated in a 50-task construction cohort within the common comparison, which accounts for 22 of the 28 tasks. This association motivates examining task composition rather than treating aggregate scores as uniform across the benchmark.
>
> Lift types do not establish an independent difficulty ordering in the current analysis. Fifteen of the 18 Composite tasks belong to this cohort, whereas 53 of the 56 Direct tasks belong to the other 100-task cohort. After controlling for configuration and construction cohort, the Composite–Direct association is not statistically established (OR=0.655, p=0.486). We therefore use lift types to describe task structure and retain category-wise results as descriptive evidence, rather than assigning intrinsic difficulty levels.

将 RQ1 的并集结果和 RQ3 的频率谱各讲一次，不重复铺陈。RQ3 不需要再升级为摘要的 headline finding。

## 5. RQ4：相同功能成功下的产物差异

### 核心证据

总体成功集合的中位数：Pro/Flash 的 Copy 大于 0.95，Luna 为 0.164。这个比较直观，但各模型成功题不同，只能作为引入。

真正的主要证据是 Pro/Luna 共同通过的 97 题：

- RRES 中位数 0.993 vs 0.697；Pro 在 85 题上更大。
- Copy 中位数 0.966 vs 0.191；Pro 在 76 题上更高。
- Copy 配对 Wilcoxon p=1.18×10^-13，rank-biserial r=0.881。
- 逐题 Copy 差值的中位数为 0.213；不能用 0.966−0.191=0.775 冒充它。
- Flash/Luna 的 92 个共同成功也具有相同方向，支持这个结果不只出现于单一配对。

还有一个可独立保留的发现：在 Pro/Qwen 的 63 个共同成功中，Pro 的 Copy 在 50 题上更高，但大小差异为 29 题更大、31 题更小、3 题相同。说明大小与重合度确实测量不同属性。

### 应当如何解释

高重合度可与正确复用并存，低重合度也可与失败并存。Luna 和 OSS 的总体成功产物 Copy 中位数都较低，但整体通过率差别很大；Pro/Flash 与 GLM 的 Copy 中位数都很高，整体成功仍明显不同。这是反对用 Copy 单独充当质量分数的描述性例证，不是任务级 Copy–成功关系的统计检验。

不能把检出重合度直接翻译成复制决策或推理策略；改名、格式和实现选择均可能影响度量。实际复用策略需要轨迹分析。

### 英文正文建议

> Functional success does not determine the structure of the resulting artifact. On the 97 tasks passed by both DeepSeek V4 Pro and GPT-5.6 Luna, median RRES is 0.993 versus 0.697, and median detected source overlap is 0.966 versus 0.191. Pro produces larger artifacts on 85 tasks and higher-overlap artifacts on 76; the paired overlap comparison has p=1.18×10^-13 and rank-biserial effect size r=0.881. Thus, the output difference persists after matching on task and functional success.
>
> Size and source overlap also capture distinct properties. On the 63 Pro/Qwen common successes, Pro has higher overlap on 50 tasks, whereas size differences are nearly balanced in direction: 29 larger, 31 smaller, and three tied. These findings support reporting both diagnostics alongside functional correctness. Neither measure establishes a quality ordering: overlap does not reveal the agent's reasoning strategy, and a smaller artifact is not necessarily easier to maintain.

这部分保留 Fig5 和配对表；不将各模型不同成功集合的均值写成因果比较，也不把六个配对各自的任务集合当成同一个全模型集合。

## 6. 效率与配置综合分析的位置

综合分析应从 RQ4 内部移到全部四个 RQ 之后，作为一个独立的结果总结段落；不要新增长篇“每个模型一个小节”。

Pro 的记录步数中位数 41.5，Flash 为 63.0，且 Pro 点估计通过率更高；可描述两者在此配置下的成功与交互量。OSS 步数中位数最少（19.0），但通过率最低，说明跨全部尝试的短轨迹本身不是效率优势。

步数包含失败和提前结束，各模型的成功集合也不同。token 存在定义差异，Luna/GLM 缺少已验证总量。现阶段不写统一成本排名、性价比冠军或按总 token 直接比较所有模型。

### 英文综合段落建议

> The configurations exhibit different combinations of delivery reliability, behavioral coverage, and artifact footprint. Pro and Flash combine reliable delivery with high source overlap among successful outputs. Luna achieves substantial functional coverage while producing smaller, lower-overlap artifacts on matched successes with Pro. GLM loses substantial coverage through non-delivery, whereas OSS usually delivers an artifact but frequently fails loading or behavioral checks. Qwen exhibits both delivery losses and additional Hidden failures after Build and Public pass. These profiles characterize the evaluated model–harness–provider configurations, rather than isolating base-model effects.

## 7. 第五章：用案例连接统计现象与可观察机制

第五章的定位应是“exploratory artifact diagnosis”，而不是“完整失败根因分类”。

- poetry-core：入口存在、数据对象与递归逻辑存在，但遗漏契约要求的一种输入表示。
- tox：展开逻辑存在，但 exported API 选择了不适用于所需输入的内部路径。
- 每个任务分别有 Pro/Flash 产物，总计四个；均 Build/Isolation 通过、Public 失败。

案例应按“契约要求 → 产物实现 → 失败表现 → 可观察机制 → 启示”展开。当前内容已基本满足，主要应缩短重复 caveat 与工程建议，不需要重新写成更长的代码审计。

### 连接 RQ2 的英文段落建议

> The gate analysis identifies behavioral correctness as the dominant remaining failure boundary for Pro and Flash. The artifact cases illustrate how substantial implementations can still miss a required behavior: one parser omits an accepted input representation, while another exported API bypasses an available expansion path. We use contract-closure gap to describe these observable mismatches between the declared obligations and the reconstructed behavior. The cases explain particular failures; they do not estimate how frequently these mechanisms occur across the benchmark.

讨论建议落在“从导出 API 验证每条行为要求”和“在移除源仓库后重新执行检查”。不主张已证明定位无关、依赖恢复是唯一瓶颈，或某种 prompting 能修复这些失败。

## 8. 扩展结果与尚未完成的消融

五配置在完整 200 题上的描述性通过率为 Flash 157/200=78.5%、Luna 144/200=72.0%、GLM 98/200=49.0%、Qwen 86/200=43.0%、OSS 61/200=30.5%。额外 50 题的对应通过数为 49、42、30、23、25；当前扩展子集的观察通过率均高于各自主比较通过率。不能据此说 200 题就是与 150 题同难度的扩大样本。

这些扩展结果适合附录及正文一句覆盖说明。不要拿 Pro 的 150 题结果与其他配置的 200 题结果排名，不填写 Pro 未执行的额外 50 题结果。多个 50 题群体必须说明所属集合，避免把 RQ3 的内部构建批次与扩展任务混为一谈。

Source ablation 是独立问题：仓库证据相对契约独立实现带来什么增益。主实验的高 Copy 不能替代该对照。真实结果到来后依据同一任务的 Full-only / Contract-only-only 成功、配对区间和失败门槛变化写结论；不沿用预测数字来决定故事。

## 9. 正文修改清单

1. RQ1 加入 122 题成功并集、相对 Pro 仅多 7 题的解释；保留配对排名限制。
2. RQ2 加入交付与行为的差异，以及通过 Build/Public 后的 Hidden 条件失败比例。正文无需新增表。
3. RQ3 保留 task variation 和混杂控制；明确“不显著”不是“类别等难”，不把构建批次当根因。
4. RQ4 以共同成功任务为证据中心；明确配对差值中位数不是两个边际中位数之差。
5. 把 configuration-level synthesis 独立放到四个 RQ 之后，避免被 footprint 小节掩盖。
6. 第五章保留两个可解释机制，把普遍统计现象与案例支持范围分开。
7. 摘要的三个 headline finding 对应：能力仍不完整、行为失败占主导、共同成功产物仍不同。Source ablation 待真实数据再加入。

本轮新增分析文档和描述性复算文件；没有修改 main.tex、图表数据或实验结果，没有编译、运行新实验或 push。
