# 论文数据与复现工作区

> **Status: current · Last verified: 2026-09-29**

[正式论文](../paper/README.md) 只在 `docs/paper/` 编辑；这里保存当前分析输入、绘图代码和历史证据。不要在此处维护第二份正文。

| 位置 | 用途 |
| --- | --- |
| [paper_sources.json](paper_sources.json) | 当前论文的数据路径、模型顺序和正式打包文件 |
| [paper_inputs.py](paper_inputs.py) | 输入读取、150 题范围与正文一致性检查 |
| [data/](data/) | 已保存的消融、失败分析、执行开销和案例数据 |
| [writing/](writing/README.md) | 当前核对脚本、证据材料；旧修订记录在 `writing/archive/` |
| [figures/standalone/](figures/standalone/README.md) | 一张图一个文件的当前论文绘图副本，数值冻结在脚本中 |
| [figures/scripts/](figures/scripts/README.md) | 从保存数据复算并生成 Fig. 3–8 的正式绘图流程 |
| [figures/drafts/rq2_150/](figures/drafts/rq2_150/README.md) | 150 题 RQ2 尚未入稿的草稿与本地预览 |
| [experiments/](experiments/) | 实验选择、服务器运行和分析脚本 |
| [replication/](replication/) | 题目构建证据包与说明 |

`main.tex`、参考文献、模板文件在本目录的同名入口只是指向 `docs/paper/` 的相对符号链接。正式图只保留在 `docs/paper/figures/`；工作区不再维护一批图号别名链接。

旧版计划、旧图和历史 PDF/ZIP 的位置见 [清理归档](../archive/paper_cleanup_20260929/README.md)。常用命令见 [当前工作流](WORKFLOW.md)。
