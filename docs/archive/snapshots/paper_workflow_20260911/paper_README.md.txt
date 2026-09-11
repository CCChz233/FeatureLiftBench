# FeatureLiftBench 论文工作稿

目标：FSE。入口：`main.tex`。当前包含八章正文、附录、三张正文表、四张附录表、五张正式图片，无图片占位符。本轮不运行实验，不编译或渲染论文。

## 当前叙事与实验范围

- 核心问题：完整源码可见时，目标能力能否跨越新软件包边界并保持行为？
- FeatureLiftBench：200 个 Python 任务、176 个仓库、182 个快照。
- 主比较：六配置在相同 150 题上比较；扩展评测：五配置额外覆盖 50 题。
- RQ1 功能成功；RQ2 首次失败阶段；RQ3 通过频次与构建批次控制分析；分类分组表移至附录。RQ4 比较共同成功产物。综合主表涵盖正确性、RRES/Copy 和 Steps/Tokens。
- 正文和结果图统一 Public / Hidden，两组测试都不向智能体开放。图 1 采用用户确认的通用 motivation 示意，放在 Introduction；图 2 采用用户最新导出的构建与验证图，放在 Section 2。
- 默认使用 source repository；donor / host 仅保留在 software transplantation 原工作介绍中。

## 验证与复现状态

作者最新确认已完成全部 200 个保留任务的复核。正文以此更新人工审核范围，保留有限测试和作者审核的一般性限制。按用户最新指示，不再展开七题历史争议及敏感性分析，原始记录保留，实验范围仍为 200/150。

镜像检查重新读取 900 条 run.json：所有运行共用一对 agent/evaluator ID。它们与 release/oracle 的配置 ID 不同；读取代码均使用 Docker Id，不能用字段命名解释。还查明 oracle summary 的 Python 字段来自宿主进程，freeze 的 Python 字段来自容器内查询。实际镜像层和配置未取得，内容等价性尚未确认。

叙事修改记录：`writing/STORY_ALIGNMENT_20260909.md`。最新图片接入与静态检查：`writing/figure_integration_check.json`。

## Overleaf 上传

更新 `main.tex`，把以下五张图片放在项目的 `figures/` 文件夹。图 1/2 使用定稿 PNG，图 3--5 保留 PDF：

```text
main.tex
references.bib
figures/
├── fig01_motivation.png
├── fig02_construction_validation.png
├── figA_task_coverage.pdf
├── figB_functional_results.pdf
└── figC_paired_footprint.pdf
```

保留 ACM 模板依赖 `acmart.cls`、`ACM-Reference-Format.bst` 和 `acm-jdslogo.png`。现有项目通常已有这些文件。编译器选 pdfLaTeX；路径中的下划线直接写 `_`。

`featureliftbench_overleaf.zip` 已随 2026-09-11 的 Fig. 3 定稿及 Fig. 4/5 排版整理重新打包，包含当前正文、bib、模板和上列五张图，可上传新建项目。此包是快照，后续修改后需重新打包。若当前项目有未同步的手工修改，应合并文件后上传，不要覆盖那些修改。

图 1 来自 `figures/design_references/fig1_generic_motivation_v1.png`；图 2 来自用户桌面最新的 `fig2.png`。旧版图片保留，不再由 `main.tex` 引用。两张图的 caption、无障碍描述及正文引导已同步；图 1 使用通用说明，Section 2 的 Blinker 段落保留为独立文字示例。

Fig. 3 已更新为两面板：左图展示完整 200 题的功能族与三类提取类型，右图展示共同 150 题的四类缠绕机制；两者分母在图中和 caption 中分别注明。逐任务数据和更新核对见 `figures/data/figA_task_index.csv` 与 `figures/data/fig3_update_validation.json`。

Fig. 4/5 已统一标题、图例与留白，保持原始统计数据。Fig. 5 明确 Pro 为比较基准，并区分 IQR 与置信区间；本轮核对见 `figures/data/fig45_update_validation.json`。没有编译整篇论文。

## 本地表格核对与绘图

在项目根目录只读核对已有结果：

```powershell
python docs/paper/writing/update_tables.py --check
python docs/paper/writing/update_structure_results.py --check
```

前者核对五张数据表和两个数据段落，后者核对附录分类结果表。相关工作表为手写。移除 `--check` 更新相应标记块；脚本不运行模型或 benchmark。

```powershell
& D:/Anaconda3/python.exe docs/paper/figures/scripts/redraw_figures.py
```

三张统计图的 Python 输出保存在 `figures/output/`，正文使用的 PDF 自动同步到 `figures/`。`draw_schematics.py` 保留用于历史示意图，不负责当前定稿图 1/2。当前两张定稿 PNG 直接进入正文；本轮仅核对图片路径、图编号、交叉引用和 LaTeX 结构，没有编译或渲染论文。

## 证据与复现

主比较输入：`reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv`（相对项目根目录）。RQ3 逐组任务、分子与分母见 `writing/structure_results.json`。当前论文不包含历史七题争议或其敏感性分析；150 题主分母保持不变。

运行输入、环境差异、具体版本和历史标签来源见附录及 `writing/CHAPTER2_EVIDENCE.md`，不把同任务比较等同于模型之外全部条件一致。

## 模板

当前使用 `acmart` 的 `acmsmall,screen,review,anonymous,nonacm` 工作稿选项。正式投稿模板和元数据按目标 track 的要求另行配置。
