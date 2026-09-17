# 当前论文绘图源码

最终决定：正文 8 图 + 8 表，无附录。文件名保留历史数字，印刷号由 LaTeX 决定。

| 图号 | 源码 | LaTeX 资产 | 状态 |
|---|---|---|---|
| Fig.1 | legacy/fig1_motivation.py | fig1.png | 锁定；历史代码不能精确复现当前 PNG |
| Fig.2 | legacy/fig2_construction.py | fig2.png | 锁定；保留现有 PNG |
| Fig.3 | fig3_composition.py | fig3a_families.pdf / fig3b_entanglement.pdf | 完全锁定，不重绘 |
| Fig.4 | fig_execution_effort.py | fig_execution_effort.pdf | 首个重建通过版本后的 token 比例与调用次数；Table 3 给成功/失败用量 |
| Fig.5 | fig4_functional_results.py | fig4.pdf | 首次失败阶段 |
| Fig.6 | fig8_failure_analysis.py | fig8_failure_analysis.pdf | 配置内类别占比，行标签给样本数；Table 5 给总体计数与定义 |
| Fig.7 | fig5_source_ablation.py | fig5a_pass_rate.pdf / fig5b_paired_gain.pdf | 配对源码消融 |
| Fig.8 | fig7_matched_footprint.py | fig7_matched_footprint.pdf | 保留竖向柱状图；Table 7 给精确值 |

`redraw_figures.py` 默认只重画 execution-effort / functional / failure-analysis / ablation / footprint，不触碰前三图。指定 `--output-dir` 仅生成预览；未指定时同步相应正式 PDF。

当前失败分类图预览：`../output/final_failure_composition_preview/`。本轮只修改其行标签中的分母，类别计数和比例不变。

探索方案保留独立源码，均不纳入正文：

- `fig4_structure.py`：结构分组柱状图。
- `fig4_task_success_matrix.py`：150 × 6 pass/fail matrix，默认仅预览。
- `fig7_footprint_forest_preview.py`：forest plot 探索版本；`preview_results.py` 用于这些探索图的几何检查。

Footprint 统计实现：`fig7_adjusted_analysis.py`。115 题、485 个成功产物；log2(RRES) 与 Copy 均控制 task fixed effects，配置效应 sum-to-zero。主 task bootstrap、task-equal-weight bootstrap、repository bootstrap 均保留既有结果。

图内只保留必要标签、轴、图例、基线和关键数字。caption 介绍展示内容；结果解释、方法和限制放正文。未编译 LaTeX。
