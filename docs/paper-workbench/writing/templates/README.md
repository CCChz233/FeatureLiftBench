# 生成表格的版式模板

> **Status: current · Last verified: 2026-09-14**

[main_table.tex](main_table.tex) 和 [source_exposure_table.tex](source_exposure_table.tex) 保留 FSE 表头、列宽、字号和注释。压缩稿目前只生成主表；源码暴露表模板仍保留，供需要附录时插入。`@@ROWS@@` 是唯一行插槽。

主表行生成：[comprehensive_table.py](../comprehensive_table.py)。源码暴露表行生成：[update_tables.py](../update_tables.py)。修改排版应改模板，然后从项目根运行 `python -B scripts/paper.py tables` 和 `check`，再编译检查溢出。模板本身不直接被 LaTeX 引入。
