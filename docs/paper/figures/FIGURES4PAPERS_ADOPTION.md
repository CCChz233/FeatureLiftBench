# 将 figures4papers 用于 FeatureLiftBench

当前范围：只制作 **Fig. 3、4、5** 三张结果图，Fig. 1、2 不在本轮绘图范围内。

首版三图已生成；当前实现以 [CHART_CONTRACTS.md](CHART_CONTRACTS.md) 为准，运行方式见 [README](README.md)。

参考本地 [figures4papers](figures4papers/README.md)，检查版本为
`3c181f85e82c6f24948fcaaf3be6696102b41d8d`。

这个项目提供真实论文的示例脚本和配套写图规范。`scientific-figure-making/references/api.md`
中的函数是建议实现的接口，不是已经安装好的 Python 包。我们的做法是保留原仓库作为参考，在
`scripts/` 中维护自己的代码，让已有实验数据决定图的内容。

## 最有用的示例，以及对应的论文图片

| 我们的图 | 具体参考 | 采用的技巧与改法 |
| --- | --- | --- |
| Fig. 3 失败阶段 | [Brainteaser brute force](figures4papers/figure_Brainteaser/plot_brute_force.py) | 借鉴 `bottom` 累加堆叠、纹理和共享图例。(a) 六条横向堆叠条，每条 150 题，展示 Pass/Missing/首败 gate；(b) 非互斥 gate 失败率用横向柱图，汇总全部 829 个已交付产物，明确计数和分母。后者不能堆成 100%；逐后端细节仍见论文附表。 |
| Fig. 4 通过频次 | [Brainteaser 分类柱图](figures4papers/figure_Brainteaser/plot_correctness_by_subcategory.py) | 借鉴轴线、直接标注和统一字号；改为单面板单色柱图，展示全部任务被 0–6 个配置通过的数量，不按临时实验分组拆分。 |
| Fig. 5 配对产物 | [VIGIL concept 的分面/注释](figures4papers/figure_VIGIL/plot_concept.py)、[Cflows 多指标布局](figures4papers/figure_Cflows/plot_comparison_Trajectory.py) | 借鉴布局，自行实现配对散点：左 RRES、右 Copy，横轴 Luna，纵轴 Pro，各 97 个同题点，加 `y=x` 等值线和等比例坐标。两个指标分别设尺度，每个面板的 x/y 范围一致。点透明度降低以减轻遮挡。 |

Fig. 3–5 延续 `main.tex` 的现有图意；Fig. 5 的散点是一种具体实现建议。
表格提供精确汇总，图展示失败集中位置、难度分布和同题差异。不要把所有表格单元格再标在图上。

## 借用规范时的六个调整

1. **按最终插入尺寸设字号。** 上游有 `figsize=(52, 12)`、`(96, 12)` 和 24–36 pt 字号，适用于其复杂大画布；我们先按实际论文图宽规划两面板。公共样式暂用 9 pt 字体、0.8 pt 轴线。最终图宽要与当前 LaTeX 版面核对，这些不是 FSE 官方尺寸。
2. **配色编码对象，不编码胜负。** 这篇是 benchmark 论文，没有被提议的“最佳模型”。后端和 gate 各自使用稳定映射；任务通过频次使用单色；用直接标签、点形或纹理补充颜色，避免依赖红绿辨识。
3. **柱形从零开始。** 上游部分比较柱图使用截断范围，我们不照搬。成功率图用 0–100%；首败计数用 0–150。非互斥 gate 图明确自己的交付分母。Fig. 5 的 Copy 固定在 0–1；RRES 不应裁掉超过 1 的产物，长尾明显时可显式使用对数坐标，并先核对零值。
4. **误差线必须有真实统计含义。** `plot_bars.py` 的示例使用其数据中的 `std`；我们每个 model–task cell 只有一个保留结果，不能模仿成重复实验标准差。如显示 Wilson 区间，写明任务分母和区间定义；没有对应证据就不加误差线或阴影。
5. **简化图例和标注。** 借用 `GridSpec`/共享图例，但我们的类别较少，优先在顶部或底部留一行图例。保留 Pro、Flash 等直接标签；只标支持论点的关键值，如 28 道全败题或 4 个 Isolation residual，其他精确数值查表。
6. **导出矢量文件。** PDF 用于 LaTeX，300 dpi PNG 用于预览；SVG 可用于后续编辑。DPI 主要影响位图元素，不会让矢量线条更清晰。关闭 `text.usetex`，使用 Matplotlib 数学文本，避免为了绘图启动外部 LaTeX。

## 已准备的公共模块

[`scripts/paper_style.py`](scripts/paper_style.py) 提供后端/阶段配色、统一样式、分面标号和导出函数。
它是按本项目需要编写的小模块，不依赖或导入克隆仓库。图的数据读取和绘制仍分别放在
`fig03_failures.py`、`fig04_difficulty.py`、`fig05_paired_footprint.py` 中，三个脚本现均已创建并运行。

在同目录脚本中使用：

```python
import matplotlib
matplotlib.use("Agg")  # 批量导出时在导入 pyplot 之前设置
from matplotlib import pyplot as plt
from paper_style import apply_paper_style, panel_label, save_figure

apply_paper_style()
fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.8), constrained_layout=True)
# 在这里读取现有结果、绘制真实数据；不要以示例随机数填补缺失结果。
panel_label(axes[0], "a", "First outcomes")
panel_label(axes[1], "b", "Failed gate flags")
# 完成绘制后：save_figure(fig, "fig03_failures")
```

本次使用已有的 `D:/Anaconda3/python.exe`，其中 Matplotlib 为 3.8.0、NumPy 为 1.26.2。未安装新依赖；PNG 和 PDF 已导出，绘图输入保存在 `data/`。

执行顺序：先 Fig. 3 确定全文样式，再 Fig. 4、Fig. 5。无需制作 Fig. 1–2；本轮不调整论文编号或删除占位。
每张图从原有结果生成；按任务 ID 配对，先核对汇总与论文一致，再预览图片，最后替换 LaTeX 占位符。

## 来源保留

上游 [LICENSE](figures4papers/LICENSE) 标注 **Attribution-NonCommercial 4.0 International**，不是 MIT。
克隆目录保留原始许可证；若后续直接改写、分发其中的代码或图片，应一并保留作者、来源、许可证和修改说明。
本轮没有复制上游整段示例或论文图片，也没有更改该克隆仓库、论文引用或正文图片占位符。
