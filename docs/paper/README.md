# 当前论文

> **Status: current · Last verified: 2026-09-29**

这里是论文正文的唯一正式目录。2026-09-29 已从作者提供的 ZIP 导入最新版 [main.tex](main.tex) 和图片；[references.bib](references.bib) 与此前相同。正文引用的 13 个图片文件都在 [figures/](figures/) 中，当前正文为 8 张图、6 张表。导入前的文件和原始 ZIP 保存在 [导入归档](../archive/paper_import_20260929/)。

| 想做什么 | 入口 |
| --- | --- |
| 修改正文、图注或表格文字 | [main.tex](main.tex) |
| 逐张调整图形外观 | [独立绘图脚本](../paper-workbench/figures/standalone/README.md)；其中 Fig. 4 脚本仍是旧 40 题版 |
| 从保存的实验数据重画已有统计图 | [绘图流程](../paper-workbench/figures/scripts/README.md)；暂不能核验新版 150 题 RQ2 图 |
| 核对数字和数据路径 | [论文输入清单](../paper-workbench/paper_sources.json) |
| 查看本地 150 题 RQ2 试画代码 | [RQ2 试画说明](../paper-workbench/figures/drafts/rq2_150/README.md)；论文图以本目录导入的 PDF 为准 |

在仓库根目录运行：

```bash
python -B scripts/paper.py check      # 检查本地可用数据、引用和图片；不核验新增的 150 题 RQ2 结果
python -B scripts/paper.py figures    # 旧 Fig. 4 绘图代码仍用 40 题，不用于更新当前论文
python -B scripts/paper.py build      # 编译 docs/paper/main.pdf
python -B scripts/paper.py package    # 生成 Overleaf ZIP
```

单张图脚本默认把 PDF/PNG 写入自己的 `output/` 目录，不自动覆盖正式图片。Fig. 1、Fig. 2 和 Fig. 6 使用作者提供的 PNG。新版论文把 RQ2 扩展到 150 题；本地尚无对应逐题实验结果，因此本目录保存的是作者提供的正式图，旧 40 题绘图流程不能作为这些图的数据核验。

历史图、旧论文包和写作记录见 [清理归档](../archive/paper_cleanup_20260929/README.md)。不要从旧 40 题脚本或试画代码覆盖当前正式图片。
