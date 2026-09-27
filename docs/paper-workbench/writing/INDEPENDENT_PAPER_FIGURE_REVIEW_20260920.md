# 当前论文与全部正文图表审阅

> **后续作者确认：** 作者已确认最终冻结 benchmark 无确认的 contract–evaluator mismatch；本文关于历史中间标记的证据链接建议不表示最终 benchmark 有缺陷。后续按作者确认的“全量 AI 初筛 → 人工复核 flagged cases → 抽检 unflagged cases → 最终作者裁决”修订正文。本文以下内容保留为修改前的历史审阅快照；当前实施记录见 `AUTHOR_DIRECTED_REVISION_20260920.md`，图表编号已因主线重排而变化。

审阅日期：2026-09-20。入口：`docs/paper/main.tex`；本报告只审阅，不改正文、任务、图表或分数。工作区已有作者修订全部保留。

**总体判断：有明确的 SE 研究对象和可成立的 benchmark/实证贡献，但当前稿尚未达到可以放心提交的状态。主要障碍是有效性证据闭环、核心证据的解释强度、主次分析失衡和版式，而不是缺少更多模型。** Benchmark 贡献本身可以是 SE contribution；不需要为了摆脱“benchmark paper”而临时发明一个方法。需要让读者看清它测量的是哪种软件复用能力、为什么现有设置不能直接替代、以及得到了什么可迁移的工程认识。

审阅范围：全文、8 张正文图、5 张正文表、补充材料源文件、主要数据入口、900 行主结果、源码暴露记录、消融统计、40-case 主题映射及相关审阅历史。重新编译并目视检查全部正文图表所在页；另在 `/tmp` 做了临时 sigconf 双栏试排。没有重跑 agent、150 题完整 evaluator、450 次 reference replay；没有逐条重新认证所有契约或全部文献，不能据本报告声称完成独立 benchmark certification。

本轮单栏 PDF：`/tmp/flb-review-20260920/main.pdf`，22 页；Conclusion 在第 20 页，Data Availability 与 References 从第 21 页开始。数值检查 `python -B scripts/paper.py check` 通过；最终单栏编译无未解析引用、无 overfull，有 underfull 提示。历史 PDF `output/pdf/featureliftbench_se_revision_draft.pdf` 日期为 9 月 18 日，不作为本次排版依据。

## 1. 优先级最高的问题

### P0：正文超过首次投稿篇幅

暂按 FSE 2027 Research Papers 核对，因未指定年份和 track。官方要求首次投稿最多 18 页正文及图表，参考文献另加 4 页；Data Availability 不计入页限。当前正文到第 20 页，需压缩约两页，不能把 22 页总数误认为“18+4 所以合规”。模板 `acmsmall,screen,review,anonymous` 正确。依据：[FSE 2027 Research Papers CFP](https://conf.researchr.org/track/fse-2027/fse-2027-papers)。

优先压缩 RQ2、RQ5 和对应方法细节；去掉 Table 1 次要描述列、Fig. 7/Table 4 重复展示；合并反复出现的限制语。不要靠缩小字号、改边距解决。最终页数必须重新编译确认。

### P1：保留任务的语义有效性裁决没有完全连接到主结果

`data/failure_analysis_20260916/classifications.csv` 保留 241 条记录，其中 13 条标记为 `benchmark_invalid_candidate`，涉及三个任务：

| 任务 | 标记运行数 | 当前消融是否包含 |
|---|---:|---|
| flake8__plugin_options_core__hard3_001 | 5 | 是 |
| pluggy__hook_wrapper_core__hard3_001 | 5 | 是 |
| pytest__ini_markers_core__001 | 3 | 是 |

这些是**历史疑点，不是本报告新判定的 13 个无效结果**。`writing/author_review_statement.json` 记录作者已确认全部保留任务经过审阅、没有问题；但同时列出 full review ledger、reviewer counts/dates、per-task evidence/replay linkage 尚未完整链接。旧七题记录与这 13 个运行不是同一集合；不得混用，也不能用旧助手判断覆盖后来的作者裁决。

问题在于：当前稿删除了旧定量 taxonomy，但主实验及 241/303 仍使用这些结果；删去分类段落不会自动关闭 evaluator validity 问题。需要一份简洁的 task/version → 具体疑点 → 作者最终依据/裁决 → 主实验和消融影响索引。如果此前已经裁决，只需补链接与理由，无需重审全部 150 题。若仍无法裁决，报告统一任务级敏感性；若确认缺陷，再版本化修复并对受影响的所有配置一致重评。不能只删掉某模型失败的 run，也不能直接把失败改成通过。

同样，`chapter2_python150_evidence.json` 记录历史 taxonomy 仅 106/150 条 source commit 与当前冻结一致；这不是 44 条标签错误的证明，但正文声称标签与当前任务证据一致时，需要连接后续作者复核，不能只依赖按 task ID join。

### P1：Primary/Extended 首败是测量位置，不完全等于行为错误

`main.tex:850` 正确说明 first failed gate 不是 cause，但图中组名 “Behavioral preservation”、摘要和结论的 “behavioral-first failures” 仍容易被当作语义根因。

可检查实例：`benchmark/tasks/bleach__sanitize_core__001/hidden_tests/test_hidden_behavior.py:39` 使用正则扫描所有 Python 文件的 `from bleach` / `import bleach` 文本；它会匹配 docstring 中的示例。当前 40-case 映射 SE028 明确将该例记为 artifact constraint，而非运行时行为错误。这说明 Extended gate 内包含非行为断言；另有契约疑点尚需对账。

建议保持原评分不动，统一把 303 的集合称为 **Primary/Extended-first failures**，把 241/303 写成该操作性集合中的源文件内容暴露率。只有经过语义复核的案例才称为 confirmed behavioral violations。Fig. 5 的行为分区改为 “Primary/Extended tests”，或正文明确该分区含 artifact constraints。该更正不需要模型实验，但最终语义解释需要检查这些断言与公开契约的对应。

### P1：核心 79.5% claim 必须保持在 file-content exposure 层次

检测规则与正文大体一致，且处理源/提交同名文件、失败读、traceback 等问题。已保存 24 个确认运行的程序/助手核查；这不是独立人工 precision/recall 验证。

`source_exposure/diagnosis/method.json` 明确允许匹配入口所在文件中的两条相邻非注释行，片段可位于入口函数体之外；REPORT 说明 docstring 也可满足规则。因此，241/303 不证明读到了目标实现、定位完成或已理解依赖。正文多处已经限定，但 RQ3 标题 “After Relevant Source Has Been Observed” 比实际测量稍强，建议改为 “After Entrypoint-Associated File Exposure”，或在标题下立即给出 file-level 定义。

重要的遗漏：Table 3 delivery/build 的 101 个运行中，有 23 个没有 paired tool observations；51/101 是全部运行中的确认率，不是完备日志中的阅读率。正文不能引导读者把不同 outcome 的检测率当成阅读倾向比较。应在正文披露缺失观察、未解析映射和“未确认不等于没读”。不能从 79.5% 与成功组 73.8% 推断读取无效或有害。

### P1：RQ3 新主题与历史双人复核之间需要更直白的说明

当前目的性样本为 40 个不同任务；三个主题分别只有 3、2、4 例，其他 31 例为 Other/case-specific。如此小的 recurring theme 完全可以作探索性证据，但不能承担“主要失败机制”“普遍瓶颈”的 claim。

`case_theme_mapping.json` 与 README 明确：新 A/B/C 主题映射是 **assistant evidence synthesis**，未声称新一轮独立人类主题复核。正文 `main.tex:604–616` 提及原双人审阅及后续综合，但读者仍可能把最终三个主题理解为双人独立编码所得。应明确写：原作者复核针对案例/既有 coding framework；三个主题为后续 AI-assisted synthesis，由作者以何种方式核查。若作者尚未核查新映射，需核查后再把它作为研究结论；不必机械补一个 kappa。

建议正文加一句：“These themes cover nine cases in the purposive sample; the remaining 31 cases were retained as other or case-specific observations.” 这是透明报告样本覆盖，不是估计总体 prevalence。“Review of all 40 cases supports three recurring themes”可改为“Across the reviewed sample, nine cases illustrate three recurring relationships.” 保留三例成功/失败配对及非干预声明。

### P1/P2：实验设置与 token provenance 不应由文稿更正替代历史事实

当前正文使用 150 interaction steps，旧报告的“正文写 120 但 P90=127”已不适用，不应重复提出这个过时问题。但 `author_result_clarifications_20260916.json` 明确 150 来自作者更正，原 runtime metadata 保留。需要确认历史有效 budget counter 与 `process_assistant_steps` 的定义及对应关系，并给出配置来源；仅把复现参数改为 150，不能证明历史 900+240 次运行实际都采用了该上限。

Table 1 同一 Tokens 列混放 uncached prompt+completion 与 total tokens。即使附注说不可比，视觉上仍邀请读者横向比较，且 Luna/GLM 的数值保留作者确认与原交付 proxy 标签冲突，尚不能从那个确认文件声称逐次 provider usage 已独立验证。9 月 17 日恢复出的 764 份 ledger 使用另一完整性规则和可用样本，不能自动解释成全 150 题旧摘要已被替代验证。

最干净的处理是主表删除 token 列，把统一定义的可复算子集放补充材料，明示覆盖；无需新增调用。必须保留旧汇总时，正文说明 provenance 和不可比口径，避免继续用表内 dagger/note 解释。

### P2：消融的 Pro 分支包含不对称重试

配对设计、discordant pairs、exact McNemar 和 Holm correction 合理；本轮复算 raw p 值与保存值一致。但 Pro Contract Only 的 18 个 timeout 被额外尝试、6 个替换，另一臂没有同样的机会结构。虽然替换不按成败挑选，仍不能称两臂尝试机制完全相同。

原始/恢复后差异已有记录：Contract Only 6→7，效应 47.5→45.0 pp。建议在补充材料报告这一敏感性及明确的停止/保留规则。Luna/Qwen 承担主要源码作用结论；Pro 作为运行完成能力也参与的结果。`LLMTimeoutError` 与“长上下文无压缩”关联不能单独证明具体失败原因。若继续保留限定表述，不需要为 Pro 重跑全套。

## 2. SE contribution、主线与 novelty

**可以成立的主贡献**：把已有软件能力跨独立包边界的复用操作化为任务，区分 donor evidence 与 destination contract，并以无 donor 运行环境验收；提供可复现的任务集合和测量协议；用实证说明源证据有帮助但不保证目标契约符合性，并展示几种具体的假设/表示/策略不兼容关系。

目前最强证据链是：

1. **可行性及范围**：六配置同 150 题，115/108/102/68/63/36 个通过；结构分组仅作描述。
2. **源证据的增益**：Luna/Qwen 的配对消融，+35.0/+27.5 pp，Full-only 对照均能交付但在测试 gate 失败。
3. **有证据仍不足**：Primary/Extended-first 的 file exposure 描述；不能冒充定位与理解完成。
4. **工程解释**：三组可检查的义务—关系对照，明确 preserved upstream、adapted context、destination requirement。
5. **有限启示**：验证显式目标输入与底层 helper 一致性、生产者与消费者表示兼容性、以及新增目标策略。它们是工具设计启示，不是已验证的新方法。

推荐将当前 RQ 顺序从 1→2→3→4→5 改为 **总体成功 → 源证据作用 → 源暴露后的契约失配**。执行继续与 footprint 改为短 secondary analyses，详细方法/结果进 supplement。Introduction、贡献段、Results、Discussion、Conclusion 都围绕“source-backed reuse across a destination boundary”；RQ2 的停止分析不应夹在最核心两段之间。

主线仍有一处概念张力：56 Direct 之外，76 Adapted 与18 Composite 占 94/150，很多要求是新目标行为，不能都称为“原行为保留”。建议早期定义为 **preserving specified upstream behavior while satisfying explicit destination adaptations**；一例区分两类 obligation。需要两个可核验实际复用需求或清楚说明任务是作者根据真实源代码构造的场景，避免 “real repository reuse” 被理解成 150 个自然发生的真实迁移请求。

与近作的区别已比纯模型比较清楚。[FeatureBench 原文](https://arxiv.org/html/2602.10975v1) 本来就包含从零构建与独立功能输出，不能把“standalone package”单独当 novelty。[FeatBench v2](https://arxiv.org/abs/2509.22237) 强调无代码提示的自然语言需求、功能实现和回归。你的区别应落在 **完整 donor 有意可见 + 明确 destination contract + source-free runtime evaluation** 的组合，以及跨边界复用问题，而不是任务更难或首次 feature-level benchmark。Table 5 应将 donor availability 写得更显眼；不要把经典 transplantation 描述成不考虑依赖或不验证行为。

## 3. Claim—evidence 对照

| Claim | 当前证据 | 审阅判断 |
|---|---|---|
| 150 tasks / 126 repositories / 132 snapshots | membership、冻结及输入检查 | 数字一致；不等于逐题独立语义认证 |
| 450/450 reference executions passed | 保存的 reference replay 证据 | 支撑 feasibility/repeatability；不证明 oracle 完整或抗作弊 |
| 24.0%–76.7% functional pass | 900 行主结果 | 可直接报告 observed configuration outcomes；不是基础模型能力排名 |
| Pro/Flash 76/77 failures first at Primary/Extended | 主结果 first_failure_stage | gate 事实正确；不能等同 76 个确认行为错误 |
| 241/303=79.5% confirmed reads | exposure CSV 与方法 | 数字正确；仅入口关联文件内容，且不是 causal explanation |
| 三种 recurring patterns | 3/2/4 例，31 other | 支撑有限探索性主题与实例；不支撑主导机制或总体频率 |
| 源证据改善 Luna/Qwen reconstruction | 配对消融 + discordant outcomes | 核心强证据；作用对象为整个 repository evidence，非独立 source text |
| passing checkpoint 后继续执行 | 317 token /403 response samples | 描述性成立；不是可避免成本、浪费或可用在线 stopping signal |
| 配置具有不同 footprint | 485 success artifacts /115 tasks | 条件于成功的描述成立；不是 maintainability、最小性或整体质量 |
| 新的关系验证方法能提升成功率 | 没有干预实验 | 当前稿只写设计启示是正确的；若升级成方法有效性 claim 才需要补实验 |

## 4. 全部正文 Figures 逐张检查

以下图号均以本次编译 PDF 为准，不能由 `fig4.pdf` 等历史文件名推断图号。

| 图 | 数据、逻辑与 RQ | Caption / 排版 / 建议 |
|---|---|---|
| **Fig. 1，p.2，任务动机与流程** | source → package → source-free evaluation 与方法一致。可作为 SE 问题入口；前两栏“复用/上下文支持”有部分重复。 | Caption 准确，source locations illustrative / no hints 限定有用。图中文字很多、层级碎，单栏已较小。建议删重复口号与装饰，突出一个贯穿例子；不是再加一段 caption。无额外图外 note。 |
| **Fig. 2，p.5，构建验证** | 150/126/132 与 450/450 一致。图中“problematic candidates excluded before freezing”是实质历史 claim，须能对应筛选/裁决记录。流程不能给人全部验证独立于 reference/oracle 的印象。 | Caption 合理但略长；明确 semantic review 是作者审阅。任务资产/验证标签细字偏小。保留，但压缩重复文字，caption 不宣称“确保有效”。 |
| **Fig. 3，p.7，组成** | family 合计 150；lift 56/76/18；机制 139/127/71/49 非互斥。热图每行分母不同，整体 150、分组56/76/18；正文与表2一致。不是难度或失败率。 | Caption 总体准确；图内没有明确 (a)/(b) 标识。最小嵌入矢量文字约 **3.84 pt**，热图数值/列名严重偏小，不能因高分辨率而判为可读。建议热图另起一行或简化标签，百分比/计数择一并由 caption 给分母；不要塞 note。 |
| **Fig. 4，p.12，继续执行** | 左样本98/93/43/27/25/31，共317；右102/96/75/46/50/34，共403；中位数与正文一致。两图不是相同 paired run 集合。箱线/点编码合理，未见截断误导。 | Caption 太短：缺 final success/recoverable conditioning、独立样本及箱线规则。y轴“Post-pass tokens (%)”可能被理解成 completion tokens 占比，建议“Tokens after first observed pass (%)”。图内加(a)/(b)，核心字号约6 pt。可移补充；若留正文，保留清楚定义，不把它称作 waste。 |
| **Fig. 5，p.13，first failure stages** | 每条150，合计900；成功492、Primary/Extended303、delivery/build101、Isolation4。与表1/表3一致。类别按 first failure 排他，不是独立 gate 通过率；更不能把低 Isolation-first 解释成隔离问题罕见。 | Caption 应写每配置150及first-failure顺序。颜色同时有纹理，灰度友好；1–3个的小段没有数值，可让补充表给 exact counts。数字约5.63pt，需略放大。把组名“Behavioral preservation”收紧为 tests/gates。保留，是核心图。 |
| **Fig. 6，p.14，三个配对例** | platformdirs/cerberus/importlib_resources 与配对证据一致。前/后不是同一程序单点修复；当前 caption 已主动限定，正确。第三例为新增目标限制，不能说上游 security guarantee 被丢失。 | 实际插入的是 `fig6.png`，不是 README 所称 vector diagram；图像高分辨率，但细代码按版面缩小后仍难读。红/绿还有叉/勾和文字，不完全靠颜色。Caption 约一长段，承担太多限制；把安全/暴露/非单点干预限定移到正文，只留三例、同契约配对和示意性质。**核心保留，优先给字号/空间。** |
| **Fig. 7，p.15，消融** | 23/9、25/7、12/1；35.0/45.0/27.5pp 及 CI 与表4一致。配置顺序 Luna/Pro/Qwen 与主图不同但图内两面板一致，建议全稿使用固定子序。左两臂+右差值+表4重复度高。 | Caption 缺40题、paired-bootstrap 95% CI、Pro保留12次无提交。Legend “Full source + contract” 与正文“Full Source”统一。无(a)/(b)图内标识。至少保留表4的 discordant pairs 与统计；推荐正文留表4、图移补充，或只留gain面板。 |
| **Fig. 8，p.17，调整后 footprint** | 485产物/115题/97库，排除7 singleton；与补充S2一致。RRES panel 的1倍基线是 configuration-effect center，**不是 reference package size**；Copy为中心化差值不是原始百分比。0起点柱形没有截轴，但ratio更适合点区间/log axis，当前并非计算错误。 | Caption 缺样本、center和pointwise95% interval，脱离正文容易误读。标出(a)/(b)，至少把虚线含义纳入caption。核心约6pt。它回答实现差异，不回答质量；可移补充以让位Fig.6。 |

所有多面板图建议统一使用真正的 (a)/(b) panel 标识；它们属于定位标签，不是额外 footnote/note。没有必要在图内放解释性段落。Fig.1/2/6 有较多概念文本，要删减内容后放大，不要只增加图像 DPI。

## 5. 全部正文 Tables 逐张检查

| 表 | 复核结果 | 必须/建议修改 |
|---|---|---|
| **Table 1，p.10** | 6×150与通过数正确；RRES/Copy仅成功；steps所有run。12列把主要结果淹没在描述统计中。 | **存在额外 minipage note 与 dagger/double-dagger，违反本次要求。** 删除表内note，限定写caption/正文。推荐主表仅保留Pass n(%)及必要的一两项，raw footprint/effort进supplement；列名“Observed pass”比不明尝试保留规则的Pass@1更稳妥。混合token计数不要继续并列为一个可比量。 |
| **Table 2，p.11** | lift分母56/76/18及四机制139/127/71/49正确；各组率与主结果一致。正文已限制非因果，合理。 | **存在额外note**，将“n为行分母、机制重叠”移caption。Caption目前不自包含。四机制marginal pass rate不能解释各依赖机制的难度。若压缩篇幅，正文保留三lift行，机制行进supplement。 |
| **Table 3，p.13** | 492+303+101+4=900；确认363+241+51+4=659；比例及conditional medians一致。重复的Runs与n/N可略精简，但不必为省一列丢分母。 | **存在额外note**；移到caption。Read step明确为one-based tool action，不是预算step。补正文23个缺paired observations的事实。Behavioral-first行名改成Primary/Extended-first；不要暗示这是经裁决的303个语义错误。 |
| **Table 4，p.16** | discordant pairs17/3、19/1、12/1；effect/CI/Holm值与保存记录、独立p值复算一致。信息价值高。 | **存在额外note**；把Δ定义、paired CI与test移caption/方法。两个“Contract only”列分别指臂通过数和discordant count，建议后者叫“Only Contract succeeds”。“Exact paired results”容易让人误以为CI也exact，改“Paired outcomes and pass-rate differences”。推荐保留它、压缩图7。 |
| **Table 5，p.19** | 比较维度有用，未比较不同benchmark分数，避免错误难度排名。FeatureBench L2从零构建的对照有文献支持。 | 无额外note，caption简洁。SWE-Refactor和donor–host行过宽泛；行名增加对应文献或方法归属，明确所比较的具体setting。Starting point强调完整donor是否有意提供，比笼统repository更能显出novelty。 |

补充材料 S1、S2 同样还带解释性 note。如果“所有图表”一并遵循本次格式要求，也要迁移到 caption/正文；S1 的million token单位应直接写列标题或caption。正文模板及生成器都需同步，否则后续 `paper.py tables` 会恢复旧note；不能只手改 main.tex。

## 6. 可直接采用的 caption 草案

以下为英文建议，不自动改稿。限定只放 caption 或正文，不增加表内 footnote。若按上述方案删列/移图，需相应调整。

**Fig. 1** — Feature-lifting task and evaluation boundary. Agents receive an intact repository and a public behavioral contract; only the submitted package enters source-free evaluation. Highlighted source locations are illustrative and are not provided to agents.

**Fig. 2** — Construction and validation of the 150-task benchmark through source pinning, contract and test development, automated checks, author semantic review, and three source-free reference replays per task (450 executions).

**Fig. 3** — Composition of 150 tasks: (a) functional families partitioned into Direct (56), Adapted (76), and Composite (18) tasks; (b) non-exclusive entanglement mechanisms, with percentages and counts using each row's task total.

**Fig. 4** — Execution after the first reconstructed passing checkpoint among recoverable, finally successful runs: (a) fraction of input-plus-output tokens, including cached input (317 runs); (b) subsequent main-agent responses (403 runs). Panels use separate available samples; labels give configuration counts. Boxes show medians and quartiles, whiskers extend to 1.5 IQR, and points denote runs.

**Fig. 5** — Outcomes for 150 tasks per configuration. Failed runs are assigned to no usable submission or their first failed gate in Build–Primary–Extended–Isolation order.

**Fig. 6** — Three illustrative failure–success pairs from the purposive sample. Each row connects upstream evidence, a destination obligation, and schematic reconstructions under the same public contract. The examples concern platform assumptions, diagnostic representations, and destination resource policy.

Fig.6的“已确认暴露并不证明每个helper被读过”“配对不是单点干预”“不证明一般文件系统安全”保留在紧邻正文，不必全塞进caption。

**Fig. 7** — Source-evidence ablation on the same 40 tasks per configuration: (a) functional pass rates; (b) Full Source minus Contract Only differences with 95% paired task-bootstrap intervals. Pro's Contract Only results retain 12 runs without submissions as failures.

**Fig. 8** — Task-adjusted footprints of 485 successful artifacts across 115 tasks: (a) size ratios relative to the configuration-effect center; (b) centered Copy differences. Dashed lines mark the centers (1× and 0 pp); intervals are pointwise 95% task-cluster bootstrap intervals.

**Table 1（按推荐精简后的版本）** — Observed functional success on the common 150-task benchmark for six model–harness configurations. All assigned tasks, including runs without usable submissions, enter the denominator.

**Table 2** — Observed functional pass rates (%) by task structure. Each row uses its task count n as the denominator; lift types partition the 150 tasks, while entanglement groups overlap.

**Table 3** — Confirmed entrypoint-associated file-content reads across the 900 main-comparison outcomes. Read fractions use all runs in each row; first-read action-step medians use only confirmed reads.

**Table 4** — Paired outcomes and pass-rate differences on 40 tasks per configuration. Discordant pairs count tasks passed under only one condition; Δ is Full Source minus Contract Only. Intervals are 95% paired task-bootstrap intervals; p-values are exact McNemar tests adjusted across three configurations using Holm's procedure.

**Table 5** — Inputs, deliverables, and evaluation boundaries of related coding, reuse, and refactoring settings.

这些 caption 不引入“显著优于”“揭示主要原因”等新结果；统计检验的结果仍由Results解释。ACM要求和用户偏好要分开：取消额外note是本次明确要求，不应谎称ACM一律禁止table notes。

## 7. 排版、复现、匿名性与方法完整性

**单栏实测**：正文图表没有明显裁切或重叠，但“无overfull”不代表可读。嵌入PDF文本估算Fig.3最小约3.84pt，Fig.5计数约5.63pt，Fig.4/8部分标签约6pt。建议最终尺寸主要图标签至少约7–8pt，作为阅读目标而非声称ACM硬性字号条文。栅格Fig.1/2/6不能从PDF提取可靠的文字点数，目视可见细字过小。Fig.6当前为4754×2810 PNG；`fig6_final_provenance.md`确认它是作者提供的最终资产。README与paper_sources部分说明仍称vector或LaTeX绘制，需更新资产来源与绘图复现边界。

**双栏试排**：仅在临时副本把class换成sigconf，没有改正式稿。Table1产生118.74pt overfull并越过右边界；Table4/Table5也有overfull，Fig.3变得更小。这不是当前单栏投稿模板错误，而是说明不能直接转双栏；如以后需要，宽图用figure*、宽表用table*或重排。FSE当前Research Papers要求acmsmall，无需现在为了双栏牺牲单栏可读性。

**复现材料需要闭环**：准确模型endpoint/version与运行日期、采样/reasoning参数、OpenHands及镜像digest、有效budget及counter定义、task/contract/test/reference identity、每个cell的attempt selection、重试规则、原始→retained→analysis的manifest、source exposure事件证据、主题综合过程、当前fig6资产与许可、补充材料编译入口。提供“重算论文数字”和“重跑模型”两个明确入口。reference三次通过与全部保留agent运行使用同一语义evaluator，也需要身份对账支持。

检查器现有路径仅找到307/900原始profile，README又记录后续原始交付覆盖900；两者是存储/索引范围不同。本轮不能说缺少593份原始日志，也不能声称已验证全部900份历史profile。应把新交付统一接入公开manifest，而非让artifact evaluator自己寻找。

**Data Availability**：已有正确位置和节名，但仍有TODO且正文写成材料已提交的完成事实。提供可访问匿名链接或实际补充上传，并说明接受后是否公开；不能由本地有zip推断已匿名公开。补充源文件要编译交付。PDF author metadata为空，匿名作者正确；尚未审计整个匿名包的绝对路径、Git remotes、日志用户名、凭证、补充文档作者信息，不能声称匿名性完整通过。

**AI研究用途披露**：当前方法写了AI-assisted validation，但新主题综合明确由assistant完成；任务/测试/reference/数据分析实际用了哪些AI、作者怎样核查，需要对应披露。FSE当前政策将研究方法、数据、分析及相关研究资产中的AI用途与一般文字辅助区别处理；本建议针对研究用途，不要求把普通语言润色包装成额外风险。依据：[FSE 2027 CFP的AI工具政策](https://conf.researchr.org/track/fse-2027/fse-2027-papers)。

**Threats to Validity**已有良好覆盖：有限测试、作者审阅偏差、曝光测量、非代表性case、单次运行、harness差异、成功条件选择、bootstrap区间限制、Python范围与训练污染。应补强实际威胁：构造需求/适配的现实性、历史疑点裁决、23次无paired observation、新主题AI综合、runtime provenance与单臂重试。不要把尚未解决的有效性问题只放Threats里一笔带过；确认的缺陷应先处理。

## 8. 是否补实验：按必要性决定

| 工作 | 优先级 | 是否需要新agent调用 |
|---|---|---|
| 把既有争议裁决连接到契约/测试版本，并确定分数影响 | **投稿前必须** | 通常不需要；只有确认变更影响评分才重评或重跑必要部分 |
| 统一主张为gate事实/file exposure/有限qualitative themes，明确AI综合与作者复核 | **投稿前必须** | 不需要 |
| 正文压至18页、去notes、完善captions、放大关键图字 | **投稿前必须** | 不需要 |
| 配置及token provenance对账、attempt选择、匿名材料入口 | **投稿前必须** | 优先恢复记录；不能靠新跑替代历史说明 |
| 有争议任务级敏感性、Pro原始/恢复结果、已有repository bootstrap | **高价值小补充** | 可利用现有数据；无需新增模型实验 |
| 对暴露detector正例/未确认例做小规模独立人工核查，尤其docstring/通用片段 | **核心79.5%保留时值得做** | 不需要；目的是界定测量可靠性，不必强做完整recall |
| 简单copy-and-wrap/依赖闭包打包baseline，特别是Direct子集 | **可选且有针对性** | 视实现而定；用于回应“是否复制即可”，不是硬性门槛 |
| 增加模型、扩大任务、所有配置多次随机种子 | **当前非优先** | 需要成本；不能解决oracle/主线问题 |
| 增加relationship-aware方法及消融 | **仅在claim升级为方法有效时需要** | 是；当前benchmark/探索性论文无需临时增加 |
| 随机抽样全量taxonomy与总体机制频率 | **仅在要声称主导/普遍机制时需要** | 不一定调用模型，但需另行设计标注；当前收缩claim即可 |

推荐执行顺序：先证据/裁决对账；再定一条主线和三个核心RQ；随后删减次要分析及重复图表；补齐caption与方法透明性；最后完成可复算匿名包、引用逐条核验和最终单栏PDF。现有材料已经足以支持一次有分量的重写；盲目扩实验不是当前最佳投入。

## 9. 本轮验证记录与证据边界

- 主结果独立汇总900个唯一model–task cell；每配置150；通过数115/108/102/68/63/36，共492。三个lift组计数与Table2逐配置对应。
- first failure阶段汇总与Fig.5/表3一致；消融discordant pairs的exact binomial/McNemar p值复算与保存值一致。CI与图表核对使用保存的配对统计及现有检查，不宣称本轮重新实施全部bootstrap分析。
- Fig.4样本317/403及配置中位数与记录一致；Fig.8/S2的485/115/97与估计/区间一致。
- 全部正文图表在重新编译的单栏PDF中目视检查；另检查临时双栏版明显越界实例。
- 旧审阅文件含已删除的176-case比例和旧120-step问题，本报告没有将其作为当前稿事实。未改任何正式实验记录或论文正文。
