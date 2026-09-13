# 论文图片

> **Status: current · Last verified: 2026-09-13**

当前正文五图、附录两图如下。旧版图片、圆环对照和 AI 草图保留作设计记录，不参与正文打包。

| 图 | 正文文件 | 内容 |
| --- | --- | --- |
| Fig. 1 | `fig1.png` | 用户确认的通用 motivation 与任务示意 |
| Fig. 2 | `fig2.png` | 沿用定稿构图；2026-09-12 明确 source-independent reference 与 validated tasks |
| Fig. 3 | `fig3.pdf` | 两侧均为完整 150 题：功能族 × 提取类型 / 缠绕机制 |
| Fig. 4 | `fig4.pdf` | 六配置首个结果与逐任务通过频次 |
| Fig. 5 | `fig5.pdf` | 40 题源码消融：通过率与配对增益置信区间 |
| 附录 Fig. 6 | `fig6.pdf` | 原 Fig. 3：功能族 × 提取类型，以及各提取类型内的机制覆盖热力图；150 题版 |
| 附录 Fig. 7 | `fig7.pdf` | 五配置分别相对 Pro 的同题产物差值 |

原分类交叉图和原产物差异图均保留在论文附录中，等待最终取舍；200 题旧稿只保留为本地历史文件，不放入当前论文。交叉图采用此前已核对的 150 题 PDF，常规绘图命令保留该文件。

## 正式入口

全局数据路径与模型名称来自 [paper_sources.json](../paper_sources.json)，工作流见 [WORKFLOW.md](../WORKFLOW.md)。从项目根目录运行：

```powershell
python -B scripts/paper.py check
& D:/Anaconda3/python.exe -B scripts/paper.py figures
```

绘图命令重画 Fig. 3–5 和附录产物图。Fig. 1/2 采用内置图像编辑工具修改范围数字，沿用原构图，旧 PNG 保留。`scripts/redraw_data.py` 生成 A/B/C/D 数据，`scripts/redraw_figures.py` 绘图，`scripts/paper_style.py` 管理样式。PNG/PDF 输出到 output/，正式 PDF 同步到本目录根层。

2026-09-12 的 Fig. 2 仅对正式 PNG 更新两处文字，并采用白色页面背景；其它同名 PDF 和 output/ 旧图仍为历史版本，不参与正文打包。原 PNG 保存在 [修改前快照](../../archive/snapshots/paper_methods_results_20260912/README.md)。AI 编辑提示词与检查说明见 [修改记录](../writing/METHODS_RESULTS_REVISION_20260912.md)。

2026-09-13：图 1/2 数字统一为 150 / 126 / 132，图 2 参考执行为 450/450；新文件名见上表。提示词与核对记录见 [范围修订记录](../writing/PYTHON150_SCOPE_REVISION_20260913.md)。

## 阅读口径

本轮测试名称统一为 Primary / Extended，图 3/4 重新生成并采用新文件名。当前修改与图像编辑提示词见 [术语与范围修订](../writing/SCOPE_TERMINOLOGY_REVISION_20260913.md)。

- Fig. 3 左侧为功能族 × 提取类型，右侧为机制边际覆盖条形图。两侧均为 150 题；Direct / Adapted / Composite 为 56 / 76 / 18；四类机制覆盖 139 / 127 / 71 / 49 题，non-exclusive。
- Fig. 4 两组 Primary / Extended 测试均不向 agent 开放；首败阶段不等于因果根因。精确计数保留在附录。
- Fig. 5 左侧为 Contract Only → Full Source 的功能通过率；右侧为配对增益及 95% task-bootstrap 区间（100,000 次重采样），不是两个独立通过率区间。Pro 的 18 次 Contract-only 空提交有 timeout，图中标注；所有空提交保留为失败。
- 附录产物图蓝点为逐题差值，菱形为中位数，横线为 IQR。差值为对应配置减 Pro；RRES 用对称对数轴，Copy 用线性轴。五组配对任务数为 105 / 97 / 67 / 63 / 33。
- 模型全名与顺序共用论文配置。RRES 和 Copy 不组成单一质量排名。

[Fig. 3 预览](output/fig3.png) · [Fig. 4 预览](output/fig4.png) · [Fig. 5 预览](output/fig5.png) · [附录产物图](output/fig7.png)

逐任务索引：`data/figA_task_index.csv`。历次核对见 `data/fig3_update_validation.json` 与 `data/fig45_update_validation.json`，这些记录描述当时的图和脚本。

本轮来源核对、正文与附录安排见 [图表叙事调整](../writing/FIGURE_STORY_REVISION_20260913.md)。

## 设计历史

`scripts/draw_schematics.py` 和旧版 `fig03/04/05` 脚本是历史入口。`output/fig3_round_comparison.png` 是未采用的圆形备选。`figures4papers/` 为参考仓库，使用说明见 [FIGURES4PAPERS_ADOPTION.md](FIGURES4PAPERS_ADOPTION.md)。

整理前的完整 README 保存在 [历史快照](../../archive/snapshots/paper_workflow_20260911/README.md)。
