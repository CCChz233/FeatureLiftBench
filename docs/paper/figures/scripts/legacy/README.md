# 历史绘图源码

这些文件不参与当前 `paper.py figures`。其中的旧图号、200 题范围和历史描述均保持原意，不应直接用于当前论文。当前图入口见 [上级索引](../README.md)。

| 文件 | 原始来源与用途 |
| --- | --- |
| [fig1_motivation.py](fig1_motivation.py) | 原 `draw_schematics.py` 的 `task()`，历史 Fig. 1 的完整绘图函数 |
| [fig2_construction.py](fig2_construction.py) | 原 `draw_schematics.py` 的 `construction()`，历史 Fig. 2 的完整绘图函数 |
| [schematic_helpers.py](schematic_helpers.py) | 上述两图共享的方框、箭头、画布和导出方法 |
| [draw_schematics.py](draw_schematics.py) | 历史两图的批量入口 |
| [draw_fig1_task_value.py](draw_fig1_task_value.py) | Fig. 1 任务定位备选设计 |
| [draw_fig1_evidence.py](draw_fig1_evidence.py) | Fig. 1 源码证据备选设计 |
| [fig03_failures.py](fig03_failures.py) | 旧 Fig. 3：首败阶段及非互斥 gate flags |
| [fig04_difficulty.py](fig04_difficulty.py) | 旧 Fig. 4：独立的通过频次图 |
| [fig05_paired_footprint.py](fig05_paired_footprint.py) | 旧 Fig. 5：Pro/Luna 同题产物散点图 |
| [preview_fig3_round.py](preview_fig3_round.py) | 旧 200 题堆叠图/圆环备选，不能使用当前 150 题数据直接运行 |

迁移时只调整导入和输出路径；历史绘图函数未改写。Fig. 1/2 当前采用 AI 编辑 PNG；这些历史代码不等于当前定稿的完整生成源码。定稿编辑过程见 `archive/paper_workspace_20260914/design_references/` 与 `docs/paper/writing/` 中的范围及方法修订记录。
