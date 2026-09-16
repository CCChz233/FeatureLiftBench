# 论文代码与数据工作流

> **Status: current · Last verified: 2026-09-16**

唯一输入入口是 [paper_sources.json](paper_sources.json)：固定 150 个任务身份、900 条逐题结果、分类数据、消融与暴露分析，以及正式文件清单。目录名称中的历史 200 题标识不改变这个范围。

```text
150 题身份 + 900 主比较结果 + 240 消融结果 + 暴露分析
                          ↓
                  paper_sources.json
                          ↓
          数值计算 / 表格模板 / 独立绘图脚本
                          ↓
          main.tex + 文献 + 模板 + 九个图片文件
                          ↓
              featureliftbench_overleaf.zip
```

## 日常命令（项目根目录）

| 命令 | 作用 |
| --- | --- |
| `python -B scripts/paper.py check` | 只读核对范围、数值、现有原始 profile、引用与图形清单 |
| `python -B scripts/paper.py audit` | 在 check 基础上要求 900 个原始 profile；当前缺 593 个，会失败 |
| `python -B scripts/paper.py tables` | 更新六张生成表；保留 Table 7 文献表，核对任务结构统计 |
| `python -B docs/paper/figures/scripts/redraw_figures.py --output-dir /tmp/flb-preview` | 生成统计图预览及派生数据，不覆盖正式资产 |
| `python -B scripts/paper.py figures` | 只重画新 Fig. 4–7；覆盖对应五个 PDF，前三图不动 |
| `python -B scripts/paper.py package` | 检查后打包正文、bib、模板/许可等六项及九个图片文件 |

绘图与表格统计需要 Python、NumPy、Matplotlib、SciPy。本机可用 `/Users/chz/anaconda3/bin/python`。以上入口不调用模型，不运行 benchmark，不编译论文。

编译需本地 TeX Live，以下命令在 `docs/paper/` 执行：

```bash
latexmk -pdf -pdflatex='pdflatex -no-shell-escape %O %S' -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

## 修改职责

[writing/update_tables.py](writing/update_tables.py) 处理生成标记区域；主表和源码暴露表的版式来自 [templates](writing/templates/README.md)。修改表头、间距、列结构时须同时核对模板和对应行生成器。作者撰写的 task-comparison 文献表不由数值脚本重写。

[writing/update_structure_results.py](writing/update_structure_results.py) 核对 Table 2 的任务类别、分母和通过率。
[figures/scripts/README.md](figures/scripts/README.md) 列出每张图的独立源码。正文打包只选择九个图形文件；旧文件名在 [archive/paper_workspace_20260914](../../archive/paper_workspace_20260914/README.md)。当前 Fig. 1/2 没有精确对应的 Python renderer，旧附录分类图只有导入 PDF；正式使用这些导入资产。`figures/output/` 是本地重画草稿，默认不进版本库。

FSE.zip 内源码消融图（现 Fig. 6） 的 PNG 与 PDF 不是同一版；本次以正文实际引用的 PDF 为准。已修正本地 renderer 缺失的标题、Pro 标记及边缘刻度留白，但重画布局不保证与导入 PDF 完全相同。替换正式图前应看预览。

## 核验与保留

源证据要求原 SHA-256 匹配；若因 Windows / macOS 换行不同，只允许 LF/CRLF 转换后精确匹配记录的原哈希。已迁移证据只在确定的归档根目录寻找。脚本不会重写 freeze、历史哈希或原始运行。

普通检查基于保留证据，只对本地找回的 307 个 profile 核对配置。完整审计需要补齐原始包。参考执行 450/450 是历史记录复算，本轮没有重跑。导入源包、修改前文件和本次清单见 [同步快照](../archive/snapshots/fse_sync_20260914/README.md)。

当前为正文 7 图、7 表，无附录。结构结果仅保留在 Table 2；footprint 保留柱状图。表格由 `writing/results_tables.py` 等生成器计算，统计分析不变。`paper.py tables/check/package` 已支持全部生成区域；不执行 LaTeX。完整映射见 [实施计划](RESULTS_VISUAL_PLAN.md)。
