# 论文图片

> **Status: current · Last verified: 2026-09-11**

当前五张正式图如下。旧版图片、圆环对照和 AI 草图保留作设计记录，不参与正文打包。

| 图 | 正文文件 | 内容 |
| --- | --- | --- |
| Fig. 1 | `fig01_motivation.png` | 用户确认的通用 motivation 与任务示意 |
| Fig. 2 | `fig02_construction_validation.png` | 用户定稿的构建与验证流程 |
| Fig. 3 | `figA_task_coverage.pdf` | 左：完整 200 题功能族 × 提取类型；右：共同 150 题缠绕机制 |
| Fig. 4 | `figB_functional_results.pdf` | 六配置首个结果与逐任务通过频次 |
| Fig. 5 | `figC_paired_footprint.pdf` | 五配置分别相对 Pro 的同题产物差值 |

## 正式入口

全局数据路径与模型名称来自 [paper_sources.json](../paper_sources.json)，工作流见 [WORKFLOW.md](../WORKFLOW.md)。从项目根目录运行：

```powershell
python -B scripts/paper.py check
& D:/Anaconda3/python.exe -B scripts/paper.py figures
```

绘图命令仅重画 Fig. 3–5。Fig. 1/2 保留用户定稿原图。`scripts/redraw_data.py` 生成 A/B/C 数据，`scripts/redraw_figures.py` 绘图，`scripts/paper_style.py` 管理样式。PNG/PDF 输出到 output/，正式 PDF 同步到本目录根层。

## 阅读口径

- Fig. 3 采用堆叠条形图 + 热力图。额外 50 题缺少同口径归一化机制字段，不补零混入右图；该范围不改变 200 题总数或全量作者复核陈述。
- Fig. 4 两组 Public / Hidden 测试均不向 agent 开放；首败阶段不等于因果根因。精确计数保留在附录。
- Fig. 5 蓝点为逐题差值，菱形为中位数，横线为 IQR。差值为对应配置减 Pro；RRES 用对称对数轴，Copy 用线性轴。五组配对任务数为 105 / 97 / 67 / 63 / 33。
- 模型全名与顺序共用论文配置。RRES 和 Copy 不组成单一质量排名。

[Fig. 3 预览](output/figA_task_coverage.png) · [Fig. 4 预览](output/figB_functional_results.png) · [Fig. 5 预览](output/figC_paired_footprint.png)

逐任务索引：`data/figA_task_index.csv`。历次核对见 `data/fig3_update_validation.json` 与 `data/fig45_update_validation.json`，这些记录描述当时的图和脚本。

## 设计历史

`scripts/draw_schematics.py` 和旧版 `fig03/04/05` 脚本是历史入口。`output/fig3_round_comparison.png` 是未采用的圆形备选。`figures4papers/` 为参考仓库，使用说明见 [FIGURES4PAPERS_ADOPTION.md](FIGURES4PAPERS_ADOPTION.md)。

整理前的完整 README 保存在 [历史快照](../../archive/snapshots/paper_workflow_20260911/README.md)。
