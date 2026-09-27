# 作者确认后的主线与图表修订

## 2026-09-21 方法表述更新

以下更新覆盖下方历史记录中的 flagged/unflagged 复核表述。

- §2.3 按作者最新确认改为：AI 对全量任务提供结构化辅助检查，作者随后人工复核全部 150 个保留任务，并决定最终保留与修正；引言同步。不增加复核人数、checklist 或一致性统计。
- §2.2 补充无法按协议指定、评测或验证的候选任务在冻结前排除，不引入候选池数量。
- §3.1 为 Pro 和 Flash 分别加入作者提供的 `deepseek-v4-pro-0813` 与 `deepseek-v4-flash-0731` 标识。
- §3.2 明确不要求最小代码抽取；功能正确性由目标行为与源码独立性决定，RRES 和 Copy 分别描述实现规模。
- 作者随后明确确认 Pro Contract Only 的原始结果就是 7/40 通过、12 次未交付，不存在补跑。按此确认删除 §3.4 的 fresh attempt / replacement / earliest-eligible-attempt 段落及 Threats 中“后续替换运行”的句子。Fig.4 caption 明确 12 次未交付计作失败；所有分数、配对统计与图表数据不变。此前根据历史存储标签推断重跑过程的解释不再用于论文；底层档案保留，来源说明记录作者确认，不声称已独立核实无重跑。
- 核对证据及后续作者澄清见 `PRO_ABLATION_PROVENANCE_CHECK_20260921.json`。本次未执行新的 benchmark 实验；删除错误补跑叙述后正文成功编译为 21 页，无 overfull 或未解析引用，Overleaf 包已更新。

## 2026-09-20 历史修改

本轮依据作者明确指令修改论文，不重跑实验、不调整任何分数。

- 最终验证流程：全量 AI 辅助初筛，作者逐一复核 flagged cases，并抽检 unflagged cases；最终保留与修改由作者决定。作者确认 frozen benchmark 中没有确认的 contract–evaluator mismatch。历史中间 review 标记不作为最终 benchmark 的事实，不在正文强调历史数量。
- 全文 `behavioral-first` 改为 `Primary/Extended-first`，源码读取统一为 `confirmed reads of entrypoint-associated source-file content`；摘要与结论的 79.5% 句子完全一致。
- RQ3 使用精确的文件内容读取表述；定性段落明确三个 recurring but limited patterns 仅覆盖部分案例，用于说明工程问题，不能解释总体失败人群。
- 三个核心 RQ：总体成功与结构、配对源码证据作用、确认文件读取后的契约失配。执行继续与 footprint 放到后置 secondary analyses；引言贡献段及 Results 导读同步。
- 消融图给出效应概览，消融表保留 passes、discordant pairs、CI 和 Holm-adjusted p-values。正文解释结果含义，不再重复逐个数值。
- 正文 Table 1–4 的额外 note 已移除；需要的分母/计数口径放 caption 或方法正文，主表 dagger 标记一并移除。共享生成器和模板已同步；同一生成器产生的补充 footprint 表说明也并入 caption。
- 原 Fig.4、7、8 的 caption 补样本、区间、统计量及中心定义。Fig.5 图例改为 `Primary / Extended evaluation`，只重绘这一张图。

## 当前编号

| 内容 | 原编号 | 当前编号 |
|---|---|---|
| 源码消融图 | Fig.7 | Fig.4 |
| 首败分布 | Fig.5 | Fig.5 |
| 三个配对案例 | Fig.6 | Fig.6 |
| 执行继续 | Fig.4 | Fig.7 |
| Footprint | Fig.8 | Fig.8 |
| 精确消融统计 | Table4 | Table3 |
| 源文件读取 | Table3 | Table4 |

## 验证

- 所有正文表格数值行与修改前逐项相同。
- Fig.3 两份 PDF 的 SHA-256 完全相同；Dataset Composition 整节未改。
- 论文数据检查与静态检查通过；表格生成后不会恢复旧术语或正文额外 note。
- 正文和补充材料均以 `-no-shell-escape` 成功编译，无 overfull 或未解析引用。
- 目视核对新消融图/表、源码暴露表、Fig.5 新图例、执行继续与 footprint caption，未见裁切或重叠。
- 正文 PDF 为21页，Data Availability 与 References 从第20页开始；补充材料4页。本轮未执行完整的18页压缩。
