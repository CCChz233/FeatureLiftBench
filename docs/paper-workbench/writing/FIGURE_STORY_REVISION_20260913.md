# 图表叙事调整：覆盖 → 表现 → 源码证据

2026-09-13。当前正文五张图依次回答：任务是什么、如何构建和验证、覆盖什么、表现与失败边界如何、完整源码是否有帮助。

## 采用的修改

- Fig. 1/2 保留当前版本。
- Fig. 3 左侧保留功能族 × 提取类型，右侧改成四类机制的边际覆盖。新文件 `figA_benchmark_coverage_150.pdf` 从逐题清单重新生成。150 题中，Code dependencies 139（92.7%）、Data and state 127（84.7%）、Framework mechanisms 71（47.3%）、Environment and resources 49（32.7%）。按任务在每个机制内去重，机制间允许重叠。左侧提取类型仍为 56 / 76 / 18。
- Fig. 4 保留结构，标题为 Outcomes and first failed gates；图内与 caption 明确首败门控是观察到的评测边界，不是因果根因。名称为 Primary / Extended。
- 正文 Fig. 5 改为 `figD_source_evidence.pdf`：左侧哑铃图展示两臂通过率，右侧展示同题配对增益和 95% CI，并附 Full-only / Contract-only 成功数。
- 原产物差异图保持原 PDF，移至定量附录。配对产物表和完整消融统计表一起移至附录。正文保留关键结果及解释，避免重复占据图表空间。

## 消融图的统计口径

图直接使用已经从原始运行核实的 240 条保留结果、120 个配对和统计文件，未使用预测结果。绘图数据入口再次逐行检查两臂 outcome 与配对表一致，重算成功数、单边成功数和配对差值，并用原随机种子及 100,000 次重采样复现原来的配对 bootstrap 区间。

| 配置 | Contract Only → Full Source | 增益，95% CI（百分点） | Full-only / Contract-only |
|---|---|---|---|
| GPT-5.6 Luna | 22.5% → 57.5% | +35.0 [15.0, 55.0] | 17 / 3 |
| DeepSeek V4 Pro | 15.0% → 62.5% | +47.5 [30.0, 65.0] | 20 / 1 |
| Qwen3.6-35B-A3B-FP8 | 2.5% → 30.0% | +27.5 [12.5, 42.5] | 12 / 1 |

区间属于 Full-minus-Contract-only 的配对差值，不是两个独立通过率区间；也不估计重复运行随机性。Pro 的 18 个 Contract-only 空提交均记录 LLMTimeoutError，图内以灰底、虚线和脚注标记，保留为失败。区间不能消除该混杂；无此错误的 22 对为 11 vs 6，p=0.125，保留在附录。

Luna/Qwen 的 Full-only 对应 Contract-only 产物均已交付但行为失败，因此它们的收益不只是交包率变化。正文仍保留“源码有帮助，但行为保持仍不完整”的结论，未将全部模型差值解释为纯粹的能力因果效应。

## 核对与交付

新图导出矢量 PDF 与 PNG，PNG 已视觉检查；当前文件引用、caption、无障碍描述、表格生成器和 Overleaf 打包清单同步更新。正文为五图两表，附录为一图六表。生成器使用原始存储字段，不更改任务或实验结果。

最终一致性记录：`figure_story_validation.json`。复现绘图使用 `python -B scripts/paper.py figures`，只生成新图 3/4/5 可用 `python -B docs/paper/figures/scripts/redraw_figures.py --only coverage functional ablation`。未运行新实验，未编译或渲染整篇论文。

## 后续决定：暂时保留原图

用户要求旧图也进入附录，最后再决定去留。原 Fig. 3 的 150 题交叉热力图以 `figA_task_coverage_python150.pdf` 加入分类说明附录（图 6），原产物差异图继续保留在定量附录（图 7）。当前为正文五图、附录两图，打包七个图文件。主文的五图结构不变；没有删除原图，也没有重新引入 200 题统计。
