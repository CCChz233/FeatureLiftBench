# FeatureLiftBench 论文工作稿

> **Status: current · Last verified: 2026-09-11**

目标：FSE。正文入口：[main.tex](main.tex)，文献：[references.bib](references.bib)。当前有八章正文、附录、七张表和五张正式图片。

## 当前口径

- FeatureLiftBench：200 个 Python 任务、176 个仓库、182 个快照。
- 主比较：六配置在相同 150 题上比较；扩展评测：五配置额外覆盖 50 题。
- 核心问题：完整源码可见时，目标能力能否跨越新软件包边界并保持行为？
- 作者已确认完成全部 200 个保留任务的复核，AI 辅助。
- Functional pass 为正确性结果；RRES / Copy 为产物诊断；Steps / Tokens 为效率统计。
- 正文统一 source repository、Public / Hidden；两组 evaluator tests 均不向智能体开放。
- RQ3 使用通过频次与构建批次控制分析；lift type 不作为独立难度刻度。

## 代码与数据入口

先看 [WORKFLOW.md](WORKFLOW.md)。当前输入路径、模型全名和顺序集中在 [paper_sources.json](paper_sources.json)，由 [paper_inputs.py](paper_inputs.py) 读取。旧文件夹名称只作存储标识。

具体材料：[论文大纲](PAPER_OUTLINE.md) · [写作脚本与证据](writing/README.md) · [图片与绘图脚本](figures/README.md)。

补充实验：[Source ablation 与机械提取 baseline 服务器指南](SUPPLEMENTARY_EXPERIMENT_RUNBOOK.md)。已固定 40 题与 3 个独立 smoke 题；Contract-only 仍需按指南实现，不代表已经运行或得到新结果。

从项目根目录执行：

```powershell
python -B scripts/paper.py check
python -B scripts/paper.py tables
python -B scripts/paper.py figures
python -B scripts/paper.py package
```

依次为只读核对、更新数值表格、绘制 Fig. 3–5、打包 Overleaf。绘图可使用本机 `D:/Anaconda3/python.exe`。这些入口不启动实验或编译论文。普通写作直接编辑 main.tex，不运行历史组装器。

## 定稿图与 Overleaf

| 图 | 正文文件 |
| --- | --- |
| Fig. 1 通用 motivation / 任务示意 | `figures/fig01_motivation.png` |
| Fig. 2 构建与验证 | `figures/fig02_construction_validation.png` |
| Fig. 3 任务组成 | `figures/figA_task_coverage.pdf` |
| Fig. 4 功能结果与通过频次 | `figures/figB_functional_results.pdf` |
| Fig. 5 共同成功产物差异 | `figures/figC_paired_footprint.pdf` |

打包命令包含 `main.tex`、`references.bib`、上述五图及 `acmart.cls`、`ACM-Reference-Format.bst`、`acm-jdslogo.png`。输出为 `featureliftbench_overleaf.zip`；修改正文后需重新打包。Overleaf 中保留 figures/ 层级，路径下划线直接写 `_`。

代码整理后，正文已于 2026-09-11 按最终 200/150/50 范围同步修订：评测协议说明共同任务与评分规则，Threats 保留实际配置与统计限制，附录介绍当前数据与复现入口。开发批次、旧标识和本地目录核对过程不再作为当前实验问题展开。定稿图片与数值表格保持原样，上传包随正文更新。

修改前正文及大纲见 [LaTeX 快照](../archive/snapshots/paper_final_scope_20260911/README.md)；旧入口文档见 [工作流快照](../archive/snapshots/paper_workflow_20260911/README.md)。

当前使用 `acmsmall,screen,review,anonymous,nonacm` 工作稿选项；正式投稿模板与元数据另行对齐目标 track。
