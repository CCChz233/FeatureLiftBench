# 当前论文

> **Status: current · Last verified: 2026-09-29**

这里是论文正文的唯一正式目录。编辑 [main.tex](main.tex) 和 [references.bib](references.bib)；正文引用的 12 个图片文件都在 [figures/](figures/) 中。当前正文为 8 张图、5 张表，图号以 `main.tex` 为准。

| 想做什么 | 入口 |
| --- | --- |
| 修改正文、图注或表格文字 | [main.tex](main.tex) |
| 逐张调整图形外观 | [独立绘图脚本](../paper-workbench/figures/standalone/README.md) |
| 从保存的实验数据重画当前统计图 | [可复算绘图流程](../paper-workbench/figures/scripts/README.md) |
| 核对数字和数据路径 | [论文输入清单](../paper-workbench/paper_sources.json) |
| 查看尚未入稿的 150 题 RQ2 草稿 | [RQ2 草稿说明](../paper-workbench/figures/drafts/rq2_150/README.md) |

在仓库根目录运行：

```bash
python -B scripts/paper.py check      # 检查范围、数值、引用和图片
python -B scripts/paper.py figures    # 生成当前统计图预览，不覆盖正式图片
python -B scripts/paper.py build      # 编译 docs/paper/main.pdf
python -B scripts/paper.py package    # 生成 Overleaf ZIP
```

单张图脚本默认把 PDF/PNG 写入自己的 `output/` 目录。确认修改后，再将同名文件放入这里的 `figures/`，并运行 `check`、编译论文检查版面。Fig. 1 和 Fig. 6 是编辑过的 PNG，没有能逐元素重画定稿的 Python 脚本；Fig. 2 由 `main.tex` 排版，不使用旧 PNG。

历史图、旧论文包和写作记录已与正式目录分开，见 [清理归档](../archive/paper_cleanup_20260929/README.md)。不要从归档或 RQ2 草稿覆盖当前正式图片。
