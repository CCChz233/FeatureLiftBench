## 当前正文图片（定稿接入）

| 图 | 正文文件 | 作用与来源 |
| --- | --- | --- |
| Fig. 1 | `fig01_motivation.png` | Introduction 中的通用 motivation 与任务示意；来自用户确认的 `design_references/fig1_generic_motivation_v1.png` |
| Fig. 2 | `fig02_construction_validation.png` | Section 2 的构建与验证；来自用户最新导出的桌面 `fig2.png` |
| Fig. 3 | `figA_task_coverage.pdf` | 左：完整 200 题的功能族与提取类型；右：共同 150 题的缠绕机制覆盖 |
| Fig. 4 | `figB_functional_results.pdf` | 功能结果与通过频次 |
| Fig. 5 | `figC_paired_footprint.pdf` | 共同成功任务的配对产物差异 |

图 1/2 按定稿原文件复制并直接引用；旧版 PNG/PDF 仍保留。`scripts/draw_schematics.py` 仅重现历史示意图，不更新当前定稿图 1/2。三张统计图由 `scripts/redraw_figures.py` 生成并同步正文 PDF。当前标签为 Public/Hidden，两组 evaluator tests 均不向智能体公开；作者复核范围以当前正文的全部 200 个保留任务为准。

本轮没有编译或渲染论文。图片来源、文件哈希与静态检查见 `../writing/figure_integration_check.json`。上传文件清单见 `../README.md`。

## Fig. 3 定稿（2026-09-11）

最终选择：**左侧堆叠条形图 + 右侧热力图**，正文引用 `figA_task_coverage.pdf`。该版保留功能族与提取类型的交叉组成，长标签也便于阅读。圆环对照 `output/fig3_round_comparison.png` 仅作为设计备选，不进入正文或 Overleaf 包。用户已授权选定版本，当前 LaTeX 与上传包均已核对使用该版。

两面板的范围明确区分：左图完整 200 题，三类提取总数为 68 / 100 / 32；右图保留完整归一化机制记录的共同 150 题。额外 50 题的原始机制标签已与任务 metadata 对齐，但旧 ledger 未派生静态传递依赖、动态加载等字段，本地源码为归档指针，因此不将缺失标签补零后混入热力图。此数据字段范围不改变作者已复核全部 200 题的陈述。

- [PNG 预览](output/figA_task_coverage.png) / [正文 PDF](figA_task_coverage.pdf)
- [逐任务分类索引](data/figA_task_index.csv)：全部 200 行；额外 50 题的四个归一化机制列为空，`mechanism_coverage_available=False`。
- [绘图数据](data/figA_task_coverage.json)：功能族 × 提取类型计数、150 题机制分母、全部来源哈希。
- [核对记录](data/fig3_update_validation.json)：数据、PDF 和 LaTeX 静态检查。

只重画 Fig. 3（项目根目录）：

```powershell
& D:/Anaconda3/python.exe -c "import sys; sys.path.insert(0, 'docs/paper/figures/scripts'); from redraw_figures import apply_paper_style, draw_coverage; apply_paper_style(); draw_coverage()"
```

本次更新只渲染了独立统计图用于检查，没有编译或渲染整篇论文。

## Fig. 4/5 排版整理（2026-09-11）

Fig. 4 保留六配置首个结果和逐任务通过频次，移除大标题与重复说明，图例采用 `No submission`；小于十的段保留但不挤入数字，精确值见附录表。图下保留 Pro/Flash 的 76/77 行为关卡失败结果。

Fig. 5 保留全部逐题差值、配对任务数、中位数和 IQR。图面明确差值相对于 DeepSeek V4 Pro，并在坐标轴标明对称对数/线性；caption 区分 Pro 比较基准与 RRES 中的 reference implementation，说明 IQR 不属于置信区间。

两张图的输入 JSON、Fig. 1/2/3 和七个生成数据块保持原样。独立 PDF 与 PNG 已检查；更新核对见 `data/fig45_update_validation.json`。只重画这两张图：

```powershell
& D:/Anaconda3/python.exe -c "import sys; sys.path.insert(0, 'docs/paper/figures/scripts'); from redraw_figures import apply_paper_style, draw_functional, draw_footprint; apply_paper_style(); draw_functional(); draw_footprint()"
```

## 历史绘图记录

以下保留历次绘图过程与旧版命名；历史审核范围、占位符和图 1/2 脚本说明不覆盖上面的当前定稿状态。

# 论文绘图

新版“分类覆盖、功能结果、配对产物”三张图已按[图片重新评估](FIGURE_REASSESSMENT.md)导出。A/B/C 是文件代号；图 C 已升级为以 Pro 为参照的五组配对差值图，并接入 LaTeX 的 `fig:paired-copy`。图 A/B 也已接入正文，分别使用 `fig:coverage` 和 `fig:failures`；B 同时承担通过频次展示。正文使用本目录根层的三张 PDF，原始输出保留在 `output/`，重画后自动同步根层 PDF 副本。未编译论文。

## 新版三图

图 B/C 已统一使用完整模型名，并为长名称调整左侧布局。名称依据正文 §3.1 的配置列表，内部数据键保留原值。

| 图 | 文件 | 内容 |
| --- | --- | --- |
| A | [PNG](output/figA_task_coverage.png) / [PDF](output/figA_task_coverage.pdf) | 三类提取任务 × 四类缠绕机制，3×4 热力图，类内覆盖率与去重计数 |
| B | [PNG](output/figB_functional_results.png) / [PDF](output/figB_functional_results.pdf) | 六配置互斥首个结果 + 0–6 配置通过的任务频次 |
| C | [PNG](output/figC_paired_footprint.png) / [PDF](output/figC_paired_footprint.pdf) | Flash/Luna/GLM/Qwen/OSS 分别与 Pro 比较，RRES 与 Copy 的任务内差值；共同通过数 105/97/67/63/33 |

在本目录的 Conda 终端一键重画：

```powershell
python scripts/redraw_figures.py
```

若默认 Python 缺少 Matplotlib，使用本机已有环境：

```powershell
& D:/Anaconda3/python.exe scripts/redraw_figures.py
```

绘图脚本为 `scripts/redraw_figures.py`，数据整理为 `scripts/redraw_data.py`。三个同名 JSON 位于 `data/`，保留任务级数据、分母、来源和哈希；新版核对记录为 `data/redraw_validation.json`。只读取本地材料，不执行 agent、oracle 或 LaTeX。

只重画正文图 C（从项目根目录运行）：

```powershell
& D:/Anaconda3/python.exe -c "import sys; sys.path.insert(0, 'docs/paper/figures/scripts'); from redraw_figures import apply_paper_style, draw_footprint; apply_paper_style(); draw_footprint()"
```

图 C 的差值统一为“对应配置 − Pro”。蓝点为逐题差值、菱形为中位数、横线为四分位区间。RRES 为对称对数轴（±0.1 内线性），Copy 为线性轴，所有点均保留。各行任务集合不同，不据行间位置推导统一任务集上的模型排名。原 Pro/Luna 配对散点仍保留在旧版 `fig05_paired_footprint` 文件中。

图 A 展示**已有历史标注**，不声称已重新审核冻结源码：150 个任务身份、公开契约与声明对齐冻结记录，原始机制标签与当前 metadata 一致；44 条历史源码身份字符串与冻结记录不同，派生机制的语义适用性尚未重审。图面和数据文件均保留此范围说明。图 B/C 使用现有实验结果，不受这次分类归并影响。

## 旧版图与参考仓库

以下保留旧图 3–5 的脚本和输出，便于比较与复用。不制作旧图 1、2。

已加入的 `figures4papers/` 是本地克隆的参考仓库。
阅读 [借鉴与落地指南](FIGURES4PAPERS_ADOPTION.md)，了解如何将其示例应用到三张结果图。
我们的公共样式模块是 [`scripts/paper_style.py`](scripts/paper_style.py)。

```text
figures/
├── scripts/   Python 绘图脚本
├── data/      从已有结果导出的绘图数据（不要修改原始实验结果）
└── output/    导出的 PDF、SVG 或 PNG
```

## 图片与脚本命名

| 图片 | 建议脚本名 | 论文标签 | 内容 |
| --- | --- | --- | --- |
| Fig. 3 | `fig03_failures.py` | `fig:failures` | 互斥首败阶段与非互斥 gate 失败标记，分面呈现 |
| Fig. 4 | `fig04_difficulty.py` | `fig:difficulty` | 0–6 个配置通过的任务分布，全部任务统一展示 |
| Fig. 5 | `fig05_paired_footprint.py` | `fig:paired-copy` | Pro/Luna 共同通过的 97 题：RRES 与 Copy 分面比较 |

三个脚本已创建，首版 PNG/PDF 已导出至 `output/`，绘图数据与源文件哈希位于 `data/`。
具体图形规格见 [CHART_CONTRACTS.md](CHART_CONTRACTS.md)。Fig. 3 右面板汇总全部 829 个已交付产物的 gate 标记，不是逐后端曲线。
沿用现有编号和标签，正文占位符尚未替换。

在当前 `figures/` 目录的 Conda `(base)` 终端运行：

```powershell
python scripts/fig03_failures.py
python scripts/fig04_difficulty.py
python scripts/fig05_paired_footprint.py
```

本次使用 `D:/Anaconda3/python.exe`（Matplotlib 3.8.0、NumPy 1.26.2）。
如果终端默认 Python 指向其他环境，可将上述 `python` 替换为 `& D:/Anaconda3/python.exe`。
脚本从自身路径定位数据，与当前工作目录无关，重复执行会更新同名图片和绘图数据。

## 现有数据与口径

以下路径相对于项目根目录 `E:/FeatureLiftBench`：

- 逐任务结果：`reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv`
- 汇总统计：`reports/paper_analysis/python150_paper_analysis_final/json/stats.json`
- 表格生成及核对逻辑：`docs/paper/writing/update_tables.py`
- 图的内容与图注：`docs/paper/main.tex`
- 故事与图表规划：`docs/paper/PAPER_OUTLINE.md`

论文统一称 FeatureLiftBench：共发布 200 个任务，六配置共同评测其中 150 个任务。
实验目录名称和临时分组不作为正式 benchmark 名称或难度标签。
首败阶段互斥，独立 gate 标记可重叠，后者以已交付产物为分母。
配对图按任务 ID 取共同通过集合，不能把两组不同任务的结果直接配对。
RRES 与 Copy 分别表示大小和源代码重叠，较高或较低均不直接代表质量更好。

优先导出矢量 PDF 供 LaTeX 引用，可额外导出 PNG 用于预览。
当前已有公共样式模块和三张图的可运行脚本；未安装新依赖或重跑实验。
图片已导出并逐张检查 PNG；未编译论文，正文图片占位符保留。
