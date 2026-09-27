# Results 图表并排候选

当前状态：已生成候选与可编辑 LaTeX 片段，未替换正文，未编译论文。入口是 `preview_evidence_pairs.py`。

## A：Fig.5 + Table 4

- 宽度为正文的 52% / 45%，余量留作两列间隔。
- Fig.5 在目标宽约 7.23 cm 下重新绘制；模型简称、两列图例，最小字为 7.5 pt。仅保留较大分段的计数，全部分段仍参与堆叠。
- Table 4 去掉与 `n/N` 分母重复的 Runs 列，保留所有分母、confirmed-read 计数、百分比和首读步数。数值来自原 source-exposure 汇总。
- 图 caption 在下，表 caption 在上。表格为 HTML 文本预览 / LaTeX `tabularx`，不并入图片。
- 预览判断：适合优先采用，图表高度接近且信息互补。

## B：Fig.6 + Table 5

- 宽度为正文的 40% / 57%。Fig.6 在目标宽约 5.56 cm 下重画，保留每个配置的 n；字号不随图片缩小。
- Table 5 保留六类的完整定义、总体计数与百分比，未改统计口径。
- HTML 中未发生文本溢出，但表格需要更多换行，阅读密度高于上下排列。
- 预览判断：可以作为紧凑候选；是否采用取决于对紧凑程度与定义易读性的取舍，不应只看节省高度。

## C：第二组上下排列对照

使用现有 Fig.6 绘图方法，在独立预览目录生成图，下面配完整 Table 5。用于与 B 比较，正式图未覆盖。

## 交付物

位于 `../output/evidence_pairs_preview/`：

- `index.html`：三个布局的对比预览。
- `fig5_compact.{pdf,svg,png}`、`fig6_compact.{pdf,svg,png}`：仅含图的素材。
- `pair_fig5_table4.tex`、`pair_fig6_table5.tex`：图表配对候选片段。
- `preview_data.json`：数据与绘图检查；`browser_layout_checks.json`：本次浏览器预览检查。

LaTeX 片段使用原图表 label，采用时应替换原图和原表，而非追加。保留 `acmart` 默认 caption 与浮动间距，未加入负间距或整体缩放表格。当前表格生成器仍服务原稿，正式采纳候选时需要同步更新对应生成器与打包清单。

## 检查范围

- 图内文本均在画布范围内，紧凑图最小字号为 7.5 pt。
- 三个 HTML 预览均无单元格或左右容器横向溢出。
- 图表数据复用当前分析模块；原稿与顶层正式图像的 SHA-256 在生成前后相同。
- HTML 是布局示意，不能证明 LaTeX 的精确换行、浮动位置或最终省页数。
