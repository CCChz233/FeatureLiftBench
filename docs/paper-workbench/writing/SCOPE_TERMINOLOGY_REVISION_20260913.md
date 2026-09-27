# 150 题范围、图表与术语修订

2026-09-13。本文统一报告 150 个任务、126 个仓库、132 个源码快照；六配置主比较 900 条结果。额外 50 题仅在 Threats 的未来扩展计划中出现，不进入当前图表或成绩分母。题包与原始实验记录保留，未运行新实验。

## 正文与附录

- 正文保留综合主表、主要行为失败现象、共同未解决任务、配对产物差异和实测源码消融。
- 非互斥门控失败的计数解释移到定量附录；执行输入与核对细节集中在复现附录。
- RQ3 以通过频次、共同未解决任务和描述性结构为主；移除内部构建批次及 cohort 回归叙事。原始标识、选择程序及历史分析保留在研究档案中。
- Primary / Extended 表示主行为测试及扩展行为测试，两组均不向 agent 提供。public / hidden 原始字段映射仅在复现说明中交代，不修改评测器或结果。
- 150 题作者复核和 450/450 参考执行仍是当前验证证据。随机 30–40 题、两名未参与被审任务构建的审核者、raw agreement / Cohen's kappa / adjudication 明确属于未来独立审核计划，没有虚构已完成结果。

## 图表

Fig. 3 从固定逐题清单和原始分类重新生成，使用新文件名 `figA_task_coverage_python150.pdf`，避免旧图混用。两侧同为 150 题；Direct / Adapted / Composite = 56 / 76 / 18。十个功能族计数为 22、31、18、15、19、5、12、11、9、8。PDF 文本与 PNG 预览均核对。

Fig. 4 按原始结果重新生成，仅更换显示名称 Primary / Extended，计数未变。Fig. 1/2 用内置图像编辑工具局部修改测试名称；原构图和 150 / 126 / 132、450/450 等数字保留。Fig. 5 未修改。

当前正文引用和打包清单使用同一组新文件。未编译或渲染整篇论文；Overleaf 压缩包由 `scripts/paper.py package` 更新。最终静态核对见 `scope_terminology_validation.json`。

## 图像编辑提示词

Fig. 1:

> Edit this existing academic figure with minimal local text edits. Preserve exact layout, all icons, colors, white background, aspect ratio and every other word and number. In the evaluator at lower right, change the small box label 'Public tests' to 'Primary tests', and the next box label 'Hidden tests' to 'Extended tests'. Keep the upper 'Public behavioral contract' unchanged: it is intentionally public. Keep footer exactly 150 tasks · 126 repositories · 132 source snapshots. Do not redesign, add, delete, crop or change any other element. Export a crisp image.

Fig. 2:

> Edit this existing academic figure with only one local text substitution. In the small sentence along the bottom of the blue CONSTRUCTION band, replace 'Public and Hidden benchmark tests are both withheld from agents.' with 'Primary and Extended behavioral tests are both withheld from agents.' Preserve exactly all other text, numbers, layout, icons, white background, colors and aspect ratio. In particular keep 150 task packages, All 150 retained tasks, 450/450 passing runs, 150 Python tasks, 126 source repositories, 132 pinned snapshots. Do not redraw or add panels or alter typography elsewhere. Export a crisp image.
