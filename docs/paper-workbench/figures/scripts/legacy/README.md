# 历史绘图源码与试画版本

本目录用于保留探索过程，不是当前论文的默认绘图入口。当前图号和正式源码以 [上一级索引](../README.md) 为准。

| 文件 | 作用 |
|---|---|
| `fig1_motivation.py`、`fig2_construction.py` | Fig.1、Fig.2 早期示意图源码；不能完全重建后期编辑过的定稿 PNG |
| `schematic_helpers.py`、`draw_schematics.py` | 早期示意图的共用工具与入口 |
| `draw_fig1_task_value.py`、`draw_fig1_evidence.py` | Fig.1 其他设计草稿 |
| `preview_fig3_round.py` | Fig.3 早期试画 |
| `fig03_failures.py`、`fig04_difficulty.py`、`fig05_paired_footprint.py` | 早期 Results 图，文件中的数字是当时图号 |
| `fig4_structure.py` | 后来删除的结构分组柱状图 |
| `fig4_task_success_matrix.py` | 后来删除的 150 × 6 pass/fail matrix |
| `fig7_paired_footprint.py` | 旧 Pro–Luna 配对图 |
| `fig7_footprint_forest_preview.py` | 未采用的六配置 forest plot |
| `preview_results.py` | 结构柱状图与 forest plot 的预览、几何检查入口 |
| `FIGURE_TEXT_AUDIT.md` | 历史文本清理记录，其中状态不代表当前论文 |

移动后的试画脚本仍复用上一级的样式和数据模块。需要试画时显式指定独立输出目录，例如：

```bash
python -B preview_results.py --output-dir /tmp/flb-legacy-preview
python -B fig4_task_success_matrix.py --output-dir /tmp/flb-matrix-preview
```

部分早期脚本仍使用旧的默认导出方式，不要通过它们更新正式论文图片。
