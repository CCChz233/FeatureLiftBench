# 论文代码与数据工作流

> 本文件保留 2026-09-20 前后的写作过程记录，后文的旧图号、文件数和命令路径不作为当前绘图说明。用户提供的最新 PDF 中 Fig. 3–8 的对应关系及可运行入口，以 [figures/scripts/README.md](figures/scripts/README.md) 为准。`scripts/paper.py figures` 现在只生成预览；正式图片只有显式 `draw_all.py --publish` 才会更新。

> **本轮主线修订（2026-09-20）：** 三个核心 RQ 按“总体成功 → 源码证据作用 → 确认入口关联源文件内容读取后的契约失配”排列；执行继续与 footprint 为后置次要分析。现 Fig.4 为消融、Fig.5 为首败分布、Fig.6 为作者提供的 `fig6.png`、Fig.7 为执行继续、Fig.8 为 footprint；Table 3 为消融统计，Table 4 为源码暴露。Fig.3 未改，所有实验数字不变；后文旧图号/RQ编号以此为准。验证流程按2026-09-21作者最新确认为：全量 AI 辅助检查后，作者人工复核全部150个保留任务；保留与修改由作者决定。

> **投稿前口径更正（2026-09-20）：** 当前 FSE 正文与消融的最大交互步数为 **150**，取代先前的 120-step 作者说明。历史 profile、日志和已归档审阅保留原值，不能作为当前复现实验预算；复现时需显式核对并设置 150。GPT-OSS 120B、120 个配对等数值不受影响。


> **当前更新（2026-09-20 themes）：** Fig.6 已换为 `fig6_qualitative_mechanisms.pdf` 机制图；源码为 `fig06_qualitative_mechanisms.py`。40 条映射在 `data/qualitative_themes_20260920/`，补充材料纳入样本内计数与逐例解释。A/B/C 为 3/2/4 条，其余 31 条保留为 Other/case-specific；不是总体比例或新一轮独立人工标注。

> **2026-09-20 当前口径：** RQ3 为目的性多样化 40-case 定性分析；Fig.6 是 `main.tex` 中的三组案例对照，无外部图片。旧 `fig06_failure_taxonomy.py` 和属性统计为历史材料，不参与默认绘图与正式打包。当前正文 8 图、5 表，补充材料 2 表；后文旧编号/流程以此为准。

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
| `python -B scripts/paper.py tables` | 更新七张生成表；保留 Table 8 文献表，核对任务结构统计 |
| `python -B docs/paper/figures/scripts/draw_all.py --output-dir /tmp/flb-preview` | 生成统计图预览及派生数据，不覆盖正式资产 |
| `python -B scripts/paper.py figures` | 只重画 Fig. 4–8；覆盖对应六个 PDF，前三图不动 |
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

FSE.zip 内源码消融图（现 Fig. 7） 的 PNG 与 PDF 不是同一版；本次以正文实际引用的 PDF 为准。已修正本地 renderer 缺失的标题、Pro 标记及边缘刻度留白，但重画布局不保证与导入 PDF 完全相同。替换正式图前应看预览。

## 核验与保留

源证据要求原 SHA-256 匹配；若因 Windows / macOS 换行不同，只允许 LF/CRLF 转换后精确匹配记录的原哈希。已迁移证据只在确定的归档根目录寻找。脚本不会重写 freeze、历史哈希或原始运行。

普通检查基于保留证据，只对本地找回的 307 个 profile 核对配置。完整审计需要补齐原始包。参考执行 450/450 是历史记录复算，本轮没有重跑。导入源包、修改前文件和本次清单见 [同步快照](../archive/snapshots/fse_sync_20260914/README.md)。

当前为五个 RQ，正文 8 图、8 表，无附录。结构结果仅保留在 Table 2；footprint 保留柱状图。表格由 `writing/results_tables.py` 等生成器计算，统计分析不变。`paper.py tables/check/package` 已支持全部生成区域；不执行 LaTeX。完整映射见 [实施计划](RESULTS_VISUAL_PLAN.md)。

RQ2 可复现入口：`python -B docs/paper/execution_effort.py --check` 核对已存小型数据；`python -B docs/paper/figures/scripts/fig04_execution_effort.py` 仅重画执行开销图。原始包导入需显式 `--import-raw-delivery`，常规 paper check/package 不依赖服务器或本地 tarball。

当前 RQ2 使用 `execution_effort_recovered.v2`：Table 3 为 764 条完整总用量，Fig.4 token/response 两 panel 分别为 317/403 条。历史持久化用量与压缩响应已纳入；父子状态共享 response ID 去重。原始导入器为 `docs/paper/import_execution_effort.py`，用量恢复回归测试为 `python -B -m unittest discover -s docs/paper -p test_execution_effort.py`。
