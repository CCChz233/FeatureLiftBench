# Token 与执行开销：论文整合计划

2026-09-17。状态：已实施首版，新 RQ2、Fig.4、Table 3 及 LaTeX 已更新。沿用不编译 LaTeX、无附录、前三张图完全保留的要求。

## 1. 推荐位置：总体能力之后，作为新的 RQ2

不把 token 分析固定为最后一个 RQ5。推荐形成如下结果结构：

| 顺序 | 主题 | 要回答的问题 | 证据 |
|---|---|---|---|
| RQ1 | Functional capability | 能不能完成 feature lifting，表现随任务结构如何变化？ | 现 Table 1、Table 2 |
| **RQ2（新增）** | **Execution effort** | **运行花费多少执行开销，开销发生在什么阶段？** | **新增结果分组表、双 panel 图** |
| RQ3（原 RQ2） | Failure diagnosis | 失败首先在哪里出现，看到源码后为什么仍会失败？ | 原失败阶段图、源码暴露表、failure taxonomy 图表 |
| RQ4（原 RQ3） | Source-evidence ablation | 仓库证据能否改善行为重建？ | 原 paired ablation 图表 |
| RQ5（原 RQ4） | Successful-artifact footprint | 同题成功时，不同配置交付的实现有何差异？ | 原 task-adjusted footprint 图表 |

推荐英文标题：

> RQ2: How Much Execution Effort Do Agents Expend on Feature Lifting?

这里的 effort 是观测到的 token 与调用开销，不是完成任务所必需的最小预算，不定义新的综合效率分数。分析对象仍为 model–harness configurations。

叙事顺序为：**能力 → 开销 → 失败诊断 → 证据作用 → 成功产物**。原失败诊断与源码消融仍相邻，不在二者之间插入 token 分析。

### 为什么不直接并入 RQ1

RQ1 已经承载总体结果和任务结构结果。首次通过状态回放需要独立的方法与分母；塞进 RQ1 会把一个清晰的能力问题扩成多个问题。因此，独立 RQ2 是首选。

降级方案：若修正后只有按 outcome 的用量统计可靠，而首次通过分析不足以支持独立发现，就在 RQ1 末尾增加 `Execution effort by outcome` 段落与一张表，仍保持四个 RQ。不因已经规划图号而强留独立 RQ。

## 2. 新 RQ 的故事：多少开销，以及开销发生在何时

开场承接 RQ1：最终 pass rate 描述能力，但不反映成功和失败运行各自的开销，也不反映合格产物何时已在轨迹中出现。

新 RQ 分成两部分，不能用同一套纳入条件混算：

1. **Effort by outcome**：在每个配置内部，比较最终 pass/fail 运行的 token 分布。只需要可靠逐运行总量，不要求恢复精确 T*；这是不同任务集合的描述性比较，不作因果归因或控制了任务组成的排名。
2. **Execution after first sufficiency**：仅在最终成功、可恢复且符合相应测量要求的轨迹上，定位首次满足完整 evaluator 的产物，观察此后的 token 与模型调用。不能把“没有恢复到 T*”填成零后续开销。

可在方法确认后使用的英文衔接句：

> Final pass rates characterize whether a run succeeds, but do not reveal how execution effort is distributed across outcomes or when a sufficient artifact first appears.

预期结果段落按“样本与方法 → 结果分组表 → 首次通过图 → 一个解释性案例”组织。不得预填报告包中尚未修正的数字，不预设 pass 比 fail 更贵或相反。

后续操作若以测试和检查为主，可以写 `continued verification after first sufficiency`。没有动作分类证据时，只写 `post-sufficiency execution`，不要写 idle loops、wasted computation 或 safe token savings。

## 3. 一张表：按最终 outcome 拆分用量

候选 label：`tab:execution-effort`。在新 RQ2 中首次引用。

| Configuration | Pass: usable n/N | Pass tokens, median [IQR] | Fail: usable n/N | Fail tokens, median [IQR] |
|---|---|---|---|---|
| Pro / Flash / Luna / GLM / Qwen / OSS | 实算 | 实算或 -- | 实算 | 实算或 -- |

- N 为正式成功或失败数；n 为该 outcome 下用量可用于本表的运行数。六行都保留，可用性不全时显示 -- 和实际 n/N。
- 统一使用可验证的 input+output total（包含缓存输入），并明确量纲；按实际数值选择统一的 10^3 或 10^6 单位。
- 不把已确认的 Table 1 汇总值按成功/失败或调用拆分。若没有可靠逐运行总量，则相应单元格不可用。
- Table 1 保留原有总体统计和计量口径。新表新增 outcome 条件分布；因为 Pro/Flash 的 Table 1 为 uncached input+output，新表在设置段明确口径不同，避免把二者数值当作矛盾。
- 不再增加“总体 token 排名柱状图”，也不把 Pass/Fail 表原样再画一遍。

## 4. 一张图：首次通过之后还剩多少执行

候选 label：`fig:execution-effort`。默认先做独立预览，不覆盖现有正式图。

- **(a) Post-sufficiency token fraction**：PSF 的任务级分布，0–100%，只纳入精确 token T* 的成功运行。
- **(b) Model calls after first sufficiency**：首次通过状态之后新增的模型请求次数分布，显示原始次数。需要完整调用与事件顺序，但不强制要求每个请求都有 token 数值。

主图优先采用竖向箱线图加低透明度任务点；横轴保持 Pro / Flash / Luna / GLM / Qwen / OSS 顺序，只为有有效数据的配置绘制分布，缺失显式注明。小样本用实际点，不用平滑曲线制造连续分布。图型可在第一轮预览后决定，不影响已锁定的 footprint 柱状图。

两 panel 的有效样本可能不同，必须分别标注 n；不能用调用次数 panel 的较大样本数给 token panel 背书。没有 token usage 的 Luna/GLM，若状态与调用记录完整，仍可能进入 (b)，但须实际验证后再纳入。

重复计入的缓存上下文会影响 (a)，所以 (b) 提供另一种可直接理解的执行开销尺度。正文可用一个真实案例解释输入/缓存输入/输出构成；不额外新增一张缓存图。

图内只留标题、轴、图例、数据和必要 n。Caption 只说明两个 panel；回放方法、CI、成功条件及解释写在正文。表格使用 booktabs，caption 在上；图 caption 在下。保持 acmart 默认浮动和间距，不编译。

## 5. 分析口径与必要修正

正式范围仍为原 150 tasks × 6 configurations = 900 个 retained runs。原成功标签不变。遵循 `experiments/TOKEN_EFFICIENCY_SERVER_RUNBOOK.md` 的回放原则，本计划补充论文组织和调用指标。

### 先修已证实的错误

最新交付 `20260917T051402Z` 的已知问题：

1. 汇总、分层和 ECDF 错用 `first_pass_fraction` 作为 PSF；统一改用 `(total-first)/total`，同步重生成候选表/CI/文字。
2. 81 条 `bounded` 调用对齐记录被纳入 exact 主样本。修映射或保留不可测；不能仅把状态改成 exact。
3. 3 条 OSS 主样本含缺用量的 HTTP 200 请求，账本仍被标为 complete。恢复真实记录或从精确 token 分析移出。
4. 将环境/依赖安装失败与 artifact 功能失败分开；统一 ever-pass-final-fail 的计数与分母。
5. 核对被 terminal 启发式跳过的操作和回放执行差异；受影响时补定向离线回放，不能仅由最终目录一致推断全过程完整。

完整核查见 `../../reports/paper_analysis/token_efficiency_review_20260917/REPORT.md`。其中重算数字只是诊断，不是正式论文输入。上述问题以已有日志处理为先，不重跑 Agent 来替换原运行。

### 新增调用指标

- `total_model_requests`：运行中的实际模型请求数；不同请求的重试保留，同一请求多条日志去重。辅助/压缩调用单独标记，默认总数包含实际发生的请求。
- `post_sufficiency_model_requests`：在首次通过工具完成边界之后发起的请求数；产生首次通过操作的那次请求不算后续请求，同一响应触发多个工具也不重复计数。
- 若请求与工具存在并发且无法定位边界，调用指标也标 bounded，不因“有 token 总量”就断言调用顺序精确。
- 保留输入、输出、缓存命中输入的前后分量；缓存是输入的一部分，不与完整输入再次相加。
- 辅助保存实际工具操作数，排除 finish、纯消息与系统事件，并记录定义。不要把已有 `original_steps` 自动当作模型调用数。

### 纳入条件与稳健性

- Effort 表、PSF panel、后续调用 panel 分别保存纳入标记和原因。
- 主 PSF 保持成功条件分析；先计算每条运行的比例，再汇总中位数和 IQR。任务 bootstrap 用于所报告的区间，不作跨供应商成本排名。
- 覆盖偏差在各配置的正式成功运行内部比较纳入/未纳入，并按 lift type 分层，避免把所有失败运行混进 excluded 组。
- 同样本比较首次通过与持续通过后的开销，识别暂时通过后又修复的影响。
- 若可恢复双账本，比较同一批运行的 total 与 main-table accounting PSF；仅交两种终态总量不算完成此项。
- 后续行为先做有限案例解释。若要写“主要用于测试/重复检查”等 prevalence 结论，须另有明确分类规则和实际标注证据，不能从两个案例推广。

## 6. 实施顺序与交付

| 阶段 | 工作 | 交付 |
|---|---|---|
| A | 修后处理、账本完整性、调用对齐及回放判定，重算三套纳入范围 | 新版本 run_metrics、calls、timeline、coverage、verification；保留原包 |
| B | 生成 outcome 用量表、PSF 与后续调用分布、同样本敏感性 | 可复算汇总与逐点数据、候选 LaTeX 表、两个 panel 预览 |
| C | 审阅结果是否形成独立发现，选择说明性案例 | 简短英文方法/结果草稿及数据定位，不预设显著性 |
| D | 按本计划整合新 RQ2，调整后续 RQ 与交叉引用 | 最终 LaTeX 源码及更新后的打包清单；静态检查，不编译 |

已实现绘图入口 `figures/scripts/fig_execution_effort.py` 和表格生成器 `writing/execution_effort_tables.py`。审查材料保留在 reports，正式可复算数据位于 `data/token_efficiency_20260917/`，新图已纳入正文与 Overleaf 包。

阶段 B 的交付数据最少包括：

- outcome_effort：configuration/outcome、assigned_n、usable_n、token median/Q1/Q3、accounting basis。
- post_sufficiency：run_id、configuration、task_id、两 panel 的纳入标记、T*、total、PSF、后续请求数、stable 对照、缺失原因。
- token_components：每运行的前/后 input、output、cache-hit input，与 token 总量可对账。
- candidate_table.tex、图的 PNG/PDF、绘图与生成表格的 Python、简短 methods/results、每个关键数字的行级出处。

## 7. 正文与编号的最终改动范围

本次已整合为 **5 个 RQ、8 图 + 8 表**；这是对原 7 图 + 7 表方案的一项明确增补。

| 当前编号/主题 | 插入新 RQ2 后 |
|---|---|
| Fig.1–3 benchmark | 完全保留 |
| 新 execution effort 图 | Fig.4 |
| 现 Fig.4 failure boundary | Fig.5 |
| 现 Fig.5 failure composition | Fig.6 |
| 现 Fig.6 ablation | Fig.7 |
| 现 Fig.7 footprint（柱状图） | Fig.8，图型不变 |
| Table 1–2 capability/structure | 保留 |
| 新 outcome effort 表 | Table 3 |
| 现 Table 3–7 | 顺延为 Table 4–8 |

LaTeX 通过 label/ref 自动编号，不因为印刷号变化重命名已有图片。现有脚本中的 RQ2/RQ3/RQ4 标题断言、7 图/7 表检查、图表清单和 Overleaf 打包范围同步更新，先改语义再检查数字，不能为了让检查通过直接删除检查。

实验设置增加一段中间产物回放及两个分析分母；Results 导语从四问改为五问。Discussion 增加停止决策与验证策略的含义。Threats 简短说明可恢复性、成功条件与离线成功信号的限制。

Introduction、贡献和 Conclusion 仅在结果定稿后各酌情补一句，不让效率分析取代论文关于行为保持与源码证据的主线。不增加 appendix，不重复说明最大 steps，不更改作者确认的 Table 1 token 值。


## 8. 本地实施记录（2026-09-17）

- 修正了服务端工具的 PSF 字段、bounded 映射误升 exact、缺调用用量误判 complete、失败历史分母和依赖安装错误分类；增加回归测试。旧 v1 metrics 不再被 v2 静默复用。
- 未重新跑 Agent 或 Docker。已交付快照被视为重建观测，不能保证覆盖全部瞬时状态；正文方法与 Threats 明确限定这一口径。
- 新导入器按源包 SHA256 保留出处，从调用、状态、评测三份记录重新核对；两 panel 使用同一保守联合样本 89/75/0/0/5/25，共 194 条。它不是完成原始全量回放修复的声明。
- outcome 表保留完整用量的 590 条运行；两个指标使用不同分母。Luna/GLM 原 Table 1 已确认的汇总保持原样。
- 已保存可离线复算的小型输入和分析文件；无需读取大型 tarball 即可重画图和更新表格。
- 新图使用箱线＋任务点，小样本 Qwen 只画点与中位数。正文增加候选结果与同样本持续通过、uncached accounting 对照。
- 后续如服务器能可靠恢复 bounded 调用映射或遗漏状态，可追加更新覆盖；本版不会把这些记录当作精确数据纳入。

- 最终检查：17 项 token 工具测试通过；正文图表数字、标签、括号与环境静态检查通过；前三图、原 footprint 图、Table 1/2 与模板保持不变。已生成 16 文件 Overleaf 包，未编译论文，也未验证编译后的分页。
