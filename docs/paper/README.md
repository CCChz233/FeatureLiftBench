# FeatureLiftBench — LaTeX 论文工作稿

> **Status: current LaTeX draft · Last updated: 2026-09-08 · Target: FSE**

本目录是根据已确定大纲撰写的 **ACM `acmart` 单文件英文论文工作稿**。
当前包括八章正文、附录、4 张正文数据表、1 张相关工作对照表、8 张附录数据表，以及 5 个待替换的图占位框。
本次只整理已有材料和结果，没有运行模型或 benchmark 实验。
当前按用户要求只修改 LaTeX 源文件，未编译或渲染。

本轮按“先补齐内容”的方向重写摘要、引言、贡献和结论，并补充章节衔接及相关工作。论文主线固定为：完整源实现可见时，agent 能否将规定行为交付为独立包；共同通过的产物，其规模和直接复制程度又有何不同。新增 `tab:positioning` 对照任务输入、交付物与评测对象；FeatureBench 的 L1/L2 分开列示，软件移植研究作为近邻工作讨论。相关工作核对记录见 `writing/sources.md`。

| 文件 | 作用 |
|------|------|
| `PAPER_OUTLINE.md` | 当前工作大纲：论文主线、章节、5 张正文图与 4 张表的设计和证据边界 |
| `main.tex` | 论文主文件（标题、摘要、正文、附录） |
| `references.bib` | BibTeX 参考文献 |
| `writing/update_tables.py` | 从既有 CSV、JSON 和运行记录生成标记内的 LaTeX 表格 |
| `writing/table_validation.json` | 表格来源、文件哈希及离线核对记录 |
| `acmart.cls` / `ACM-Reference-Format.bst` / `acm-jdslogo.png` | ACM 编译依赖 |

## 编译

```bash
cd docs/paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Overleaf：上传本目录全部文件，编译器选 **pdfLaTeX**，入口 `main.tex`。

## 数字边界

主结果输入为 `reports/paper_analysis/python150_prime_v2_analysis_20260905/task_results.csv`。
主分母固定为 150 题 × 6 配置；空提交计为失败。七个疑似任务缺陷的剔除结果单列为 143 题的事后敏感性视图。

2026-09-08 的[本地复核报告](../../reports/paper_analysis/python150_offline_audit_20260908/README.md)补充了逐题证据：126 题在两个 freeze 间未改动，另外 24 题与替换集合完全一致；900 份初始提示词及 838 份已有功能评测 capsule 与 v2 对齐。522 条 v2、378 条前序 run ID 均按原值保留。仍有运行镜像 ID 与 release/oracle 清单不同、25 个本地完整任务树未完全复原等限制，见报告和论文附录；不能将结果解释为完全统一条件下的纯模型排名。

七题的 14 个 Pro/Flash 产物已经重新阅读：六题支持保留缺陷候选，pytest 一题仍属 accessor 空白策略歧义。正文保留原 143 题敏感性表，附录补充仅剔除六题的 144 题视图。失败语义标注仍为 AI 辅助 L1，不能当作独立人工验证的因果比例。

从项目根目录更新或核对表格：

```bash
python docs/paper/writing/update_tables.py
python docs/paper/writing/update_tables.py --check
python docs/paper/writing/known_defect_sensitivity.py
```

更新器只改 `BEGIN/END GENERATED TABLE` 标记之间的内容，保留手工正文修改。
相关工作对照表为手写 LaTeX，不由实验数据更新器生成；总计 13 张表，其中 12 张为数据表。

## 替换五张图

在 `main.tex` 中找到 `figureplaceholder` 的五处调用，用相应的 `includegraphics` 替换，保留外层 `figure`、`caption`、`Description` 和 `label`。图注已写好，框内给出了作图提示。

1. `fig:pipeline`：Blinker 示例、源仓库与独立产物边界。
2. `fig:construction`：任务构建、数据可见性与实际验证覆盖。
3. `fig:failures`：首次失败阶段与非互斥 gate flags。
4. `fig:difficulty`：0–6 个配置通过的题目分布与 Core/hard3 对照。
5. `fig:paired-copy`：Pro/Luna 在 97 个共同通过任务上的 RRES 和复制比例。

统计图应从已有数据作图；正文图注与附录表给出了分母和指标定义。原稿与原参考文献保存在 `writing/original_*_20260907.*`。

## 审稿模式

`main.tex` 使用 `\documentclass[acmsmall,screen,review,anonymous,nonacm]{acmart}`。
当前保留匿名和行号；`nonacm` 用于工作稿，避免显示尚未确定的出版信息。
投稿时按目标会议要求配置模板和出版元数据。
