# 论文数值生成与证据

> **Status: current · Last verified: 2026-09-14**

正文入口是 [main.tex](../main.tex)，不运行历史章节组装器。当前输入由 [paper_sources.json](../paper_sources.json) 指定。

| 文件 | 职责 |
| --- | --- |
| [update_tables.py](update_tables.py) | 八张生成数据表、一段文字；900 主比较 / 240 消融 / 900 暴露记录核对 |
| [comprehensive_table.py](comprehensive_table.py) | 主比较 12 列表格数值 |
| [templates](templates/README.md) | 保存作者新版主表和源码暴露表的排版 |
| [update_structure_results.py](update_structure_results.py) | 附录任务结构通过率表 |
| [evidence_sources.py](evidence_sources.py) | 精确哈希或 LF/CRLF 等价验证；已知归档位置解析 |
| [table_validation.json](table_validation.json) | 最近生成的数值与来源核验摘要 |
| [chapter2_evidence.py](chapter2_evidence.py) | 150 题身份、参考执行、修复记录证据 |

从项目根运行 `python -B scripts/paper.py tables` 更新，再用 `python -B scripts/paper.py check` 只读核对。`audit` 另要求原始 900 个 profile 全部存在；当前仅 307 个已找回。详见 [同步记录](../FSE_SYNC_20260914.md)。

本目录其他 evidence / revision / sensitivity 文件保留各自时间和范围，不因文件名中的 final 或旧图号覆盖新版正文。历史入口原文已保存在 [导入前快照](../../archive/snapshots/fse_sync_20260914/README.md)。

证据专题：[构建核验](CHAPTER2_EVIDENCE.md) · [讨论案例](CHAPTER5_CASE_EVIDENCE.md) · [文献核对](BIBLIOGRAPHY_REVIEW.md) · [范围修订](PYTHON150_SCOPE_REVISION_20260913.md)。

## 当前 Results 新增证据

[results_visuals.py](results_visuals.py) 共享新图与新表的数据；[results_tables.py](results_tables.py) 更新结构、消融配对和配对产物三张表，源码暴露表由原生成器恢复，共补四表。当前正文 7 图、6 表。

[回归测试](test_results_visuals.py) 检查顺序不变性、重复任务拒绝、标签冲突拒绝及配对中位差/平局定义。运行 `python -B -m unittest discover -s docs/paper/writing -p test_results_visuals.py`。

[数据证据](results_visual_evidence.json) · [图形与结构检查](results_visual_validation.json) · [实施计划](../RESULTS_VISUAL_PLAN.md)。新模块需要 SciPy；不运行 LaTeX。
