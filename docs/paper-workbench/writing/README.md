# 论文数值与写作证据

> **Status: current · Last verified: 2026-09-29**

当前正文以 [docs/paper/main.tex](../../paper/main.tex) 为准，输入由 [paper_sources.json](../paper_sources.json) 指定。这里的 `.py` 和数据文件用于核对或分析；过去的计划、审稿记录和旧图号说明在 [archive/notes_20260929/](archive/notes_20260929/) 中。

| 当前需要 | 入口 |
| --- | --- |
| 检查 150 题身份与来源 | [chapter2_python150_evidence.json](chapter2_python150_evidence.json)、[chapter2_python150_task_inventory.json](chapter2_python150_task_inventory.json) |
| 检查结果与统计 | [paper_sources.json](../paper_sources.json)、[主结果分析](../../../reports/paper_analysis/) |
| 查看论文全文复核记录 | [FULL_MANUSCRIPT_AUDIT_20260927.md](FULL_MANUSCRIPT_AUDIT_20260927.md) |
| 表格排版模板 | [templates/README.md](templates/README.md) |
| 查看正文省略的细节 | [Footprint](FOOTPRINT_ANALYSIS_DETAILS.md)、[执行开销](EXECUTION_ANALYSIS_DETAILS.md) |
| 了解历史构建与定性案例 | [CHAPTER2_EVIDENCE.md](CHAPTER2_EVIDENCE.md)、[CHAPTER5_CASE_EVIDENCE.md](CHAPTER5_CASE_EVIDENCE.md) |

从仓库根目录运行 `python -B scripts/paper.py check` 核对当前范围、图和适用的数值证据。当前导入的正文表格直接写在 `main.tex`，旧版 `paper.py tables` 生成区已不存在，不应用它覆盖正文。历史校对文件保留其当时口径；其中的“final”或旧图号不是现在的论文状态。
