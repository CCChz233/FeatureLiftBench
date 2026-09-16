# 2026-09-16 补实验交付审查与论文修改建议

> 后续作者澄清：本页保留交付包初审结论。作者随后确认所有实验最大步数为 120、Pro 消融无上下文压缩且长上下文无法完成、Luna/GLM 表中数值为实际 token 汇总。当前稿采用这些作者确认；来源及与旧记录的差异保存在 `author_result_clarifications_20260916.json`。因此下文关于主表暂留 NA 和步数待确认的建议已被后续作者说明取代；作者又补充说明多位共同作者已经审核失败分析；下文“人工复核为 0”仅描述交付包记录，不能用于否认包外已经完成的作者审核。实际流程、范围及最终标签版本待补充，不能推定必须重新审核。

对象：`experiments/failure_analysis_delivery_20260916T013305Z.tar.gz`。

结论：**可以更新 Pro 的阶段性消融结果；不宜直接采用交付包的 token 主表补值和 failure-analysis 定量结论。** 不是三项工作均已达到定稿要求。本文只作核验与修改建议，没有改 `main.tex`、执行交付脚本、运行实验或编译论文。

## 1. 本地核验范围

- 压缩包成功完整读取并隔离解包：7,362 个成员，解包内容约 217 MB；文件未覆盖项目原输入。
- 本地审查位置：`reports/paper_analysis/server_delivery_review_20260916/failure_analysis_delivery_20260916T013305Z/`。
- 归档 SHA-256：`4122532015056a24631ca4ffd8ac8296365a45405df42baf031e8a14752ac622`。
- 包内 `SHA256SUMS` 指向另两个未包含的原 split tarball，不能用它验证本次合并包；上述本地 hash 只是本次接收版本的身份记录。
- 对照了新旧 240 条消融结果、6 条恢复产物的 evaluator gate、原始配对计数、exact McNemar p 值、241 条标注、分类/复核代码、300 条 token 汇总与估算代码，查看了交付 PNG。
- 未宣称对 241 份提交完成新的逐案语义复核，也未独立重跑 bootstrap。下文区间取交付统计；计数、McNemar 和 token 描述统计进行了独立计算。

## 2. 三项交付的采用判断

| 模块 | 实际结果 | 论文处理 |
| --- | --- | --- |
| Pro Contract-Only | 18 题各新增 1 次 attempt；6 题恢复，12 题仍未解决；恢复的 6 题中 1 题通过、5 题行为失败 | 可以版本化更新 RQ3、消融图和 Table 4，保留服务中断限制 |
| Luna / GLM token | 300 条均无实测 usage；现有数值是累计可见事件历史的 proxy | 暂不填入 Table 1；先修估算方法和统计口径 |
| Failure analysis | 241 候选，包内归为 228 有效、13 缺陷候选；201/228 被标 behavior drift | 可作为待审标注集；不直接采用 88.2% 作为完成精读的主文结论 |

## 3. RQ3：可采用的数值与必须保留的解释

### 3.1 更新数字

新旧 240 行逐行对照：只有 Pro / Contract-Only 的 6 个 cell 发生变化；另外 22 个 Contract cell、原 12 个仍未解决 cell、Pro Full 和 Luna/Qwen 均不变。6 个新增可评测产物中，1 个通过、4 个 Primary-first、1 个 Extended-first；不是恢复后全部成功。

| Pro 指标 | 当前论文 | 本次保留结果 |
| --- | ---: | ---: |
| Full Source pass | 25/40 | 25/40 |
| Contract-Only pass | 6/40（15.0%） | 7/40（17.5%） |
| Full-only | 20 | 19 |
| Contract-only | 1 | 1 |
| Full − Contract | +47.5 pp | +45.0 pp |
| 配对 bootstrap 95% CI | [30.0, 65.0] | [27.5, 62.5] |
| exact McNemar p | 旧版值 | 0.0000400543 |
| 三模型 Holm-adjusted p | 0.0000629 | 0.000120163 |
| timeout + no submission 未解决 | 18 | 12 |

Luna 23/40 vs 9/40、Qwen 12/40 vs 1/40 保持不变；本次重算后的 Holm p 仍均为 0.005153656。

建议修改位置：

1. `main.tex` 的 `sec:rq3` Pro 结果句。
2. `fig:source-evidence` 两面板数据、caption 和 accessibility description。
3. `tab:paired-ablation` Pro 行与表下注释。
4. Evaluation Protocol 的 recovery policy 简述；Threats 的服务中断与晚运行时间说明。
5. 分析输入 manifest 和生成器应切换到新的版本化数据，不能只手工替换 LaTeX 数字。

当前表注中「无中断 22 对，11 vs 6，p=0.125」也不能原样保留为新版敏感性结果。新版排除未解决服务错误后为 **28 对，Full 15、Contract 7，未校正 p=0.021484375**。这是选择后的子集，不替代 40-task 分母，也不能作为新的主要显著性结论。

### 3.2 建议正文替换句

> After one recovery attempt for each of the 18 timeout-related missing submissions, six Contract-Only outcomes were replaced using the earliest eligible attempt. Pro passes 25/40 tasks with Full Source and 7/40 with Contract Only, a descriptive difference of 45.0 percentage points. Twelve Contract-Only runs remain unresolved service failures; we therefore do not interpret the Pro contrast as a clean estimate of the benefit of repository evidence.

仍建议以 Luna / Qwen 支撑正文关于 repository evidence 的主结论，Pro 作为带限定的补充结果。不能把较小的 p 值解释成服务混杂已经解决。

可在补充材料加一个透明的结果界限：若只将剩余 12 个未解决 Contract 结果视为未知，Contract 最多 19/40，因此 Full-minus-Contract 的算术范围是 **+15 至 +45 pp**。这不是置信区间，也不证明无混杂的因果效应。

原 policy 允许每题最多 3 次新增 attempt，但目前只有 1 次；「补跑已经全部完成」应改为「第一轮恢复完成，12 题仍未解决」。论文可以采用当前阶段性版本，不必假称干净结果；若继续恢复，冻结规则不变，再统一更新版本。

## 4. Table 1：现有 token 数值不宜直接采用

交付包给出 Luna Median/P90=1483.7k/11349.4k，GLM=7018.5k/18791.9k，并注明 est.。问题不只是缺少官方 tokenizer，而是估算对象尚未对齐真实请求。

证据代码：交付包 `paper/token_recovery/estimate_visible_tokens.py`，特别是第 65–84 行和第 97–102 行。

1. **把每个 `source=agent` 事件视为一次 LLM 调用。** 其 `api_calls_est` 与记录的 provider API calls 明显不一致：Luna 合计 7,255 vs 5,423（149/150 条不一致）；GLM 11,931 vs 12,198（141/150 条不一致）。事件数和调用数不同本身并不说明原日志错误，但足以说明不能假设它们一一对应。
2. **历史只增长，不处理实际上下文凝缩/截断。** 脚本将所有历史内容持续累加，在每个 agent 事件前重新计入 prompt。它不是对实际 outbound requests 的重建。偏差可来自历史重复计数，同时还漏掉 system/tool schema 等，不能笼统称为下界。
3. **completion 只取 thought 与 action 字段，尚未验证等价于响应载荷。** 工具参数、多 action、一请求多事件、失败/重试和隐藏 reasoning 的处理都未充分对齐。
4. **Median 用了顺序统计量，而不是通常的偶数样本中位数。** 150 行选择一个中间值，未平均中间两个值；P90 也与线性插值定义不同。

仅把现有 proxy 数组按通常 Median / 线性 P90 重算，得到：

| 模型 | Median (k) | P90 (k) |
| --- | ---: | ---: |
| Luna | 1486.5 | 11349.9 |
| GLM | 7125.9 | 18794.1 |

**这张表只用于证明交付统计口径需要修正，不是推荐写入论文的新 token 值。** 修分位数并不能修复请求重建偏差。

编码敏感性 1.003–1.022 只比较两个 tokenizer 在该代理文本上的差别，不覆盖事件/请求错配、上下文策略和不可见内容的误差。

建议：Table 1 继续 `—`，正文保留 lack verified usage 的真实表述。若希望保留此次分析，将其称为 *visible-transcript proxy* 放补充材料的方法审查中，先修事件分组、上下文处理、完整性与校准；不把这个 proxy 插入总 token 主列。主表缺两格比补上无法核验的百万级估算更可辩护。

## 5. Fig. 8 / Table 7：方向值得保留，当前标签不足以定稿

### 5.1 目前数字能说明什么

包内标注计算自洽：241 候选 → 13 benchmark-invalid candidates（3 个 task）→ 228 有效；其中 behavior drift 201、API completion 16、dependency closure 8、packaging 2、unknown 1。六模型有效 n 为 26/31/30/35/42/64。

这些是**交付标签的分布**。计数守恒不意味着每条标签有充分语义证据，也不能把它们立刻写成已验证的真实根因比例。

### 5.2 两个实质性方法问题

**第一轮中大量标签由规则自动生成。** `paper/scripts/classify_remaining.py` 处理 pilot 外 205 行，根据摘要中的 AssertionError / TypeError / KeyError 等字段分类；例如一般 assertion 分支直接给 behavior drift，KeyError 分支给 dependency closure。随后脚本统一设置 `close_read_tier=L1`。其中 clause helper 会回退到第一个 clause，甚至 B001，不能替代真实失败义务的映射。

现有 241 条中有 99 条使用同一句一般化摘要：「required API is present ... first observable assertion differs ...」。这不证明 99 条全部标错，但说明不能仅凭这些文本验证实际 API 存在、具体行为义务及修复边界。需要回查原提交而非直接把计数当精读成果。

**第二轮并非独立语义审查。** `paper/scripts/apply_dual_agent_review.py` 的 R2 是截取日志后应用 Python 规则；其默认分支明确把残差归为 behavior drift。它没有逐案核对提交和契约。脚本又把所有记录设为 `agent_double_reviewed` 和 `adjudicated=true`。交付的 κ≈0.96 / 0.73 最多是当前两套标签的一致性，不能作为独立人工一致性或有独立语义审查依据的质量证明。

本地 [SOP §3](../../FAILURE_ANALYSIS_SOP.md) 的要求是「L2 金标：独立人工双审……才可以把根因比例写进主文」；原服务器 runbook 也明确两次 AI 检查不等于人工双审。交付包将 gate 自行写成 dual-agent-review，不改变既定要求。实际人工 reviewer 数为 0，待审并集为 134。

### 5.3 论文现在不应写的结论

- 不写「88.2% 的失败原因已确认为 behavior drift」。可以内部记录为自动辅助初审的暂定分布。
- 不写「localization=0，因此定位已解决」。交付正文自己说明没有将过程侧 wrong-region 证据作为此轮主要判断，零计数不等于不存在。
- 不把所有 behavior drift 合并为 contract closure；不因观察到源码读取就宣称模型理解了源码。
- 不报告 κ 为两位独立 reviewer 的结果；不把脚本统一写出的 L1/L2 状态当证据。

### 5.4 如何让新增证据组有真正的信息增量

保留 RQ2 的三层结构：**首败阶段 → source exposure → 产物中残留的具体契约缺口**。不用新增 RQ5，也不必扩大摘要中的数字数量。

先补逐案「公开 clause + 对应提交实现 + 首败行为 + 判定理由」证据，优先回查 99 条通用 assertion 标签、KeyError/dependency 分类、所有 defect/unknown/Hidden-only。对每个模型同题产物独立判断；完成后按原协议进行真实复核，不能只改状态字段。

视觉上，现在 Fig. 8 六根横条大半是同一个 behavior 色块，信息增量有限。修好标签后，建议保持**一个 Fig. 8 + 一个 Table 7**，但分工调整：

- Fig. 8 展示有证据支持的契约维度分布，例如参数/默认值、异常与边界、顺序/状态、解析/格式、依赖/资源。可以用配置 × 维度的小型热图；多标签时清楚说明可重叠，不能假装互斥加总。
- Table 7 给操作定义、真实计数/分母，以及少量公开 clause 对应的代表性缺口；若保留 primary 计数，则与图的 secondary 契约维度承担不同作用。

这些维度必须来自重新核对后的标注，不能把当前粗类为了好看随意拆开。如果复核后仍确实由一个类别占主导，也应如实呈现，不为增加色块改变定义。

若暂时不补标注，保留现有 7 图 + 6 表，比把这个版本包装成已完成的系统根因研究更稳。完整原始材料已经回来，补证据可以继续离线开展，不必新增模型实验。

## 6. 两处额外需要同步处理的问题

### 6.1 统一 120 steps 的表述与消融记录冲突

`main.tex` Evaluation Protocol 当前写 main 与 ablation 全部使用相同 120-step limit。但 240 行消融数据中：

- Pro 80 行：`max_steps=120`、`persisted_max_iterations=500`。
- Luna / Qwen 各 80 行：`max_steps` 空、`persisted_max_iterations=500`。

不能据此直接断言 Luna/Qwen 实际全部运行到 500 步，但它说明「所有实验统一 120」缺乏当前配置记录支持。应核对 runner 的实际限制优先级，区分 harness step override 和 OpenHands maximum iterations，分别描述 main 与 ablation；不能改写日志去适配现有正文。

### 6.2 新发现的 benchmark-invalid candidates 与主结果一致性

13 条只是 3 个任务上的候选问题，不能称为已裁决缺陷。需要核查其公开契约和 evaluator 公平性，并解释为什么 failure-analysis 暂时排除这些行，而原 150-task leaderboard 保持冻结不变。

若最终确认为任务级缺陷，补充统一的跨模型敏感性分析：对所有配置采用相同任务排除集合，报告相关 Pass@1 / RQ1 / RQ4 及消融适用范围的影响；不能只删某模型的失败行改善分数。原始冻结结果保留，修订结果版本化。当前不依据候选标签直接改 150、900 或 115/485。

## 7. 推荐修改顺序

1. **现在可做**：版本化接入 Pro 6 条恢复结果，更新 RQ3/图/Table 4/Threats 和新版敏感性注释；审查并修正 step-budget 文字。
2. **保留现状**：Table 1 的 Luna/GLM token 暂留缺失；保留原主榜和 RQ4 分母；摘要以已有 Luna/Qwen 消融与 source-exposure 结果为主。
3. **新增证据组定稿前**：修 A 的逐案证据和 review provenance，完成真实复核，再确定 Fig. 8 / Table 7 数字和形式。
4. **后续可选**：按已冻结 recovery policy 继续处理 Pro 剩余 12 题；在能恢复真实请求边界和上下文处理时再修 token proxy。

论文主线仍然成立：repository evidence 有帮助，但观察到源码读取并不足以保证行为保真。此次材料最值得投入的是把「哪里失败」推进到有逐案依据的「哪些行为义务没有保住」，而不是立即增加一个 88.2% 的粗粒度结论。
