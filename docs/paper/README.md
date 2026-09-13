# FeatureLiftBench 论文工作稿

> **Status: current · Last verified: 2026-09-13**

目标：FSE。正文入口：[main.tex](main.tex)，文献：[references.bib](references.bib)。当前有八章正文、附录和五张正文图片及两张附录图片。

## 当前口径

- FeatureLiftBench：150 个 Python 任务、126 个仓库、132 个快照。
- 主比较：六配置覆盖全部 150 题，共 900 条结果；本文不讨论额外任务池。
- 核心问题：完整源码可见时，目标能力能否跨越新软件包边界并保持行为？
- 作者原有全量复核声明覆盖本文的全部 150 题，AI 辅助。
- Functional pass 为正确性结果；RRES / Copy 为产物诊断；Steps / Tokens 为效率统计。
- 正文统一 source repository、Primary / Extended；两组 evaluator tests 均不向智能体开放。
- RQ3 为 Source Ablation，检验 repository evidence 的作用。通过频次与共同未解决任务降为描述性分析；lift type 不作为难度刻度。

## 代码与数据入口

最终决策为**不新增大实验，暂缓 120-run Entrypoint-Hint**，见[执行指南](experiments/SOURCE_EXPOSURE_HINT_RUNBOOK.md)。900 条轨迹已分析：303 次行为首败中，241 次（79.5%）有成功工具返回入口关联文件内容的证据。该指标仅为文件内容暴露，不证明入口定义已读取、理解或完整定位。方法、原始事件索引、映射缺失和 107/39 题标注子集见[离线报告](../../reports/paper_analysis/source_exposure/diagnosis/REPORT.md)。方法放 §3，结果放 §4，附录说明检测范围。摘要、引言与结论均包含 79.5%，主线为源码证据有帮助、相关文件内容已暴露、行为仍未完整保留。

先看 [WORKFLOW.md](WORKFLOW.md)。当前输入路径、模型全名和顺序集中在 [paper_sources.json](paper_sources.json)，由 [paper_inputs.py](paper_inputs.py) 读取。旧文件夹名称只作存储标识。

具体材料：[论文大纲](PAPER_OUTLINE.md) · [写作脚本与证据](writing/README.md) · [图片与绘图脚本](figures/README.md)。

补充实验：[Source ablation 与机械提取 baseline 服务器指南](SUPPLEMENTARY_EXPERIMENT_RUNBOOK.md)保留原始设计。2026-09-13 已收到并分析 Luna、Pro、Qwen 三配置 × 40 题 × 两臂的 240 条实际记录；执行设置与原计划的差别按运行记录写入论文附录。

`main.tex` 的预测占位已全部替换为实测：Luna Full/Contract Only 为 23/40 对 9/40，Pro 为 25/40 对 6/40，Qwen 为 12/40 对 1/40。Pro 的 18 次 Contract-only 空提交均有 LLM timeout，正文和表注保留该限制；主要解释依据 Luna/Qwen 的行为差异及敏感性分析。见[消融结果报告](../../reports/paper_analysis/source_ablation_40_20260913/REPORT.md)。

2026-09-12 的第二章方法与结果解释修订记录见[本轮修改与待核实事项](writing/METHODS_RESULTS_REVISION_20260912.md)。当前表格生成器另外读取经过核对的消融结果表，主比较的 900 条结果保持不变。消融统计复算命令为 `python -B reports/paper_analysis/source_ablation_40_20260913/analyze.py`，输入是本地解出的原始记录。

从项目根目录执行：

```powershell
python -B scripts/paper.py check
python -B scripts/paper.py tables
python -B scripts/paper.py figures
python -B scripts/paper.py package
```

依次为只读核对、更新数值表格、绘制 Fig. 3–5 及附录产物图、打包 Overleaf。绘图可使用本机 `D:/Anaconda3/python.exe`。这些入口不启动实验或编译论文。普通写作直接编辑 main.tex，不运行历史组装器。

## 定稿图与 Overleaf

本轮正文、附录、未来计划与图表术语调整见 [修订记录](writing/SCOPE_TERMINOLOGY_REVISION_20260913.md)。

| 图 | 正文文件 |
| --- | --- |
| Fig. 1 通用 motivation / 任务示意 | `figures/fig1.png` |
| Fig. 2 构建与验证 | `figures/fig2.png` |
| Fig. 3 任务组成 | `figures/fig3.pdf` |
| Fig. 4 功能结果与通过频次 | `figures/fig4.pdf` |
| Fig. 5 源码证据消融 | `figures/fig5.pdf` |
| 附录分类交叉图 | `figures/fig6.pdf` |
| 附录产物差异图 | `figures/fig7.pdf` |

打包命令包含 `main.tex`、`references.bib`、上述七个图文件及 `acmart.cls`、`ACM-Reference-Format.bst`、`acm-jdslogo.png`。输出为 `featureliftbench_overleaf.zip`；修改正文后需重新打包。Overleaf 中保留 figures/ 层级，路径下划线直接写 `_`。

2026-09-13：论文范围统一为固定 Python-150 集合，摘要、方法、组成统计、图 1–3、结论和复现附录同步修改，删除额外 50 题的扩展评测。参考执行为 450/450；本文任务对应修复记录为 24/4。主结果表保持原值。题包、历史 200 题 freeze 和原始运行不变。当前修改及图像编辑提示词见 [范围修订记录](writing/PYTHON150_SCOPE_REVISION_20260913.md)。

修改前正文及大纲见 [LaTeX 快照](../archive/snapshots/paper_final_scope_20260911/README.md)；旧入口文档见 [工作流快照](../archive/snapshots/paper_workflow_20260911/README.md)。

当前使用 `acmsmall,screen,review,anonymous,nonacm` 工作稿选项；正式投稿模板与元数据另行对齐目标 track。
