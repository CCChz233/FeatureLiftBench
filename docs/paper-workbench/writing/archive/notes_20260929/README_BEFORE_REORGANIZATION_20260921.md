# FeatureLiftBench 论文工作区

当前提交不含独立 Supplement；正文原有的 4 处 supplementary / S1 / S2 指向均改为 replication materials。Overleaf 包不包含本地历史 supplementary.tex 和 qualitative_mapping.tex。RepoZero 当前引用 arXiv v1，使用该版本五位作者及顺序。

> **本轮主线修订（2026-09-20）：** 三个核心 RQ 按“总体成功 → 源码证据作用 → 确认入口关联源文件内容读取后的契约失配”排列；执行继续与 footprint 为后置次要分析。现 Fig.4 为消融、Fig.5 为首败分布、Fig.6 为作者提供的 `fig6.png`、Fig.7 为执行继续、Fig.8 为 footprint；Table 3 为消融统计，Table 4 为源码暴露。Fig.3 未改，所有实验数字不变；后文旧图号/RQ编号以此为准。验证流程按2026-09-21作者最新确认为：全量 AI 辅助检查后，作者人工复核全部150个保留任务；保留与修改由作者决定。

> **投稿前口径更正（2026-09-20）：** 当前 FSE 正文与消融的最大交互步数为 **150**，取代先前的 120-step 作者说明。历史 profile、日志和已归档审阅保留原值，不能作为当前复现实验预算；复现时需显式核对并设置 150。GPT-OSS 120B、120 个配对等数值不受影响。


> **当前更新（2026-09-20 themes）：** Fig.6 已换为 `fig6_qualitative_mechanisms.pdf` 机制图；源码为 `fig06_qualitative_mechanisms.py`。40 条映射在 `data/qualitative_themes_20260920/`，补充材料纳入样本内计数与逐例解释。A/B/C 为 3/2/4 条，其余 31 条保留为 Other/case-specific；不是总体比例或新一轮独立人工标注。

> **Status: archived· Last verified: 2026-09-17**

新版正文来自用户提供的 FSE.zip。入口：[main.tex](../../../../paper/main.tex) · [项目地图](../../../../PROJECT_MAP.md) · [本次同步记录](../../../../archive/paper_cleanup_20260929/workbench_plans/FSE_SYNC_20260914.md)。

当前论文包含 150 个 Python 任务、126 个仓库、132 个快照；六配置各 150 题，共 900 条主比较结果。另有三配置 × 40 题 × 两臂的 240 条源码消融结果。当前正文三个核心 RQ 和两项次要分析、八张图、五张正文表和两张补充表，引用十一个图形文件；没有附录。

## 写作与修改

- 软件工程主线修订：[四里程碑执行计划（2026-09-18）](../../../../archive/paper_cleanup_20260929/workbench_plans/SE_REVISION_PLAN_20260918.md)。RQ3 已按 2026-09-20 决定改为目的性多样化 40-case 定性分析；不再报告全量 taxonomy 分母和比例。Fig.6 由正文 LaTeX 直接呈现三组案例，旧分类图及 codebook 表退出正文。
- 作者只需使用[复核工作簿](../../../../../reports/paper_analysis/se_obligations_pilot_20260918/REVIEW_GUIDE.md)：操作、规则、40 条案例填写区与裁决/冻结/总结均在一份文件中；各人复制填写，旧拆分模板不再使用。
- 论述与文献：[main.tex](../../../../paper/main.tex)、[references.bib](../../../../paper/references.bib)。不运行历史章节组装器。
- 输入、模型顺序、图片打包清单：[paper_sources.json](../../../paper_sources.json)。
- 表格布局：[writing/templates/](../../templates/README.md)；数值从保留记录计算，模板修改不会被数值更新覆盖。
- 正式图形资产位于 [figures/](../../../figures/README.md) 根目录；绘图源码在 [figures/scripts/](../../../figures/scripts/README.md)。旧文件名已归档，不进 Overleaf 包。
- Fig.1–Fig.3 锁定不动；原结构 Fig.4 删除，Table 2 保留；footprint 使用柱状图。
- 运行记录与题包：[PAPER_FOLDERS.md](../../../../archive/paper_cleanup_20260929/workbench_plans/PAPER_FOLDERS.md)。

从项目根目录执行：

```bash
python -B scripts/paper.py check
python -B scripts/paper.py tables
python -B docs/paper/figures/scripts/draw_all.py --output-dir /tmp/flb-figures-preview
python -B scripts/paper.py package
```

`check` 只读核对，`tables` 更新生成区域，预览绘图不替换正式图片，`package` 检查后输出 [Overleaf 压缩包](../../../../paper/featureliftbench_overleaf.zip)。完整步骤见 [WORKFLOW.md](../../../WORKFLOW.md)。

## 当前证据边界

主比较逐题结果完整，最新原始交付包覆盖正式 900 个运行，已完成包与文件索引核对。旧 profile 检查器仅在既有解包路径找到 307/900 个 profile，因此 `python -B scripts/paper.py audit` 仍会报告该路径下缺失；这不等于新交付包缺少原始日志。普通 `check` 通过也不能代替全部历史回放的重新验证。

Luna / GLM 的 Token 总量按作者确认值写入 Table 1。Pro ablation 最终保留结果为 Full Source 25/40、Contract Only 6/40，18 次未交付计作失败；逐任务配对重算得到 Full-only/Contract-only = 20/1、差值 47.5 pp、95% CI [30.0, 65.0] pp、Holm p = 6.2943e-5。当前数据由 paper_sources.json 指向 source_ablation_retained_20260921；正文不讨论运行历史。此口径覆盖之前的 Pro 数值说明。源码读取的 241/303（79.5%）不变。

当前使用 `acmsmall,screen,review,anonymous`，未修改 `acmart.cls`。图 caption 在下、表 caption 在上；本轮未编译或验证最终分页。

辅助入口：[写作证据](../../README.md) · [图形工作区](../../../figures/README.md) · [大纲与历史论证](../../../../archive/paper_cleanup_20260929/workbench_plans/PAPER_OUTLINE.md) · [方法与结果修订记录](METHODS_RESULTS_REVISION_20260912.md)。

新增 RQ2 的口径、执行记录及样本范围见 [Token 与执行开销整合计划](../../../../archive/paper_cleanup_20260929/workbench_plans/TOKEN_EFFICIENCY_INTEGRATION_PLAN.md)。

最新分工及图表编号见 [Results 视觉证据计划](../../../../archive/paper_cleanup_20260929/workbench_plans/RESULTS_VISUAL_PLAN.md) 顶部最终决定；历史预览不进入 Overleaf 包。

RQ2 已接入 20260917T072646Z 原始交付：六配置均有 token 时间线与后续响应数据，图中分别标注 317/403 条样本的配置分母；Table 3 用完整总用量的 764 条记录。恢复方法与核查见 [原始交付复核](../../../../archive/paper_cleanup_20260929/workbench_plans/TOKEN_RAW_DELIVERY_REVIEW_20260917.md)。

## 2026-09-20：RQ3 定性收口

Fig.5、Table 3 和 RQ4 原文及统计保持不变。40-case 样本按配置配额和功能族、lift type、旧复核状态覆盖选择，使用确定性 hash 破同分，不是随机样本。保留原始复核和历史分类数据；当前生成器、检查器和打包清单不再将分类构成纳入正文。
