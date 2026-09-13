# Source-evidence ablation：实测结果与论文结论

2026-09-13。分析用户提供的 `experiments/source-ablation-40-r1-full.tar.gz`，不运行新实验，不修改题包，不选择最佳尝试。当前论文采用 150 题、126 仓库、132 快照；消融样本是其中预先固定的 40 题、38 仓库。

## 最值得进入正文的发现

**仓库证据显著改善行为保持，其收益不能仅用是否交付产物解释；但源码可见仍不足以保证成功。**

Luna 的 Full Source 通过率为 57.5%，Contract Only 为 22.5%；Qwen 分别为 30.0% 和 2.5%。更有解释力的是：Luna 的 17 个 Full-only 成功和 Qwen 的 12 个 Full-only 成功，其 Contract-only 对应运行全部已交付产物，并在行为门槛失败。因此，这些成功差异发生在行为正确性层面。

这个结果支持 FeatureLiftBench 将完整仓库作为 implementation evidence 的设定。它没有隔离源码文本、上游文档、测试、资源各自的贡献，也没有证明某个具体依赖恢复或导航机制占主导。

## 全部 240 条实际记录

每配置同一组 40 题、两臂，共 80 个保留结果；三个配置共 240 条。没有把主实验中的 Full 运行混入消融，也没有把打包文件名中的 full 误认为只包含一个实验条件。

| 配置 | Full Source | Contract Only | 差值 | 配对 bootstrap 95% CI（百分点） | Full-only / Contract-only | Holm 校正 p |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.6 Luna | 23/40，57.5% | 9/40，22.5% | +35.0 pp | [15.0, 55.0] | 17 / 3 | 0.00515 |
| DeepSeek V4 Pro | 25/40，62.5% | 6/40，15.0% | +47.5 pp | [30.0, 65.0] | 20 / 1 | 0.000063 |
| Qwen3.6-35B-A3B-FP8 | 12/40，30.0% | 1/40，2.5% | +27.5 pp | [12.5, 42.5] | 12 / 1 | 0.00515 |

主统计按 assigned-40 计分，空提交为失败。p 值为双侧 exact McNemar，三模型探索性比较做 Holm 校正。配对 bootstrap 为 100,000 次重采样，随机种子 20260913；它描述任务集合的不确定性，不是重复运行方差，也不会消除 API 中断影响。

**Pro 的 +47.5 pp 不能作为纯粹的语义能力增益来解释。** 它的 Contract-only 有 18 次空提交，全部末尾记录 `LLMTimeoutError`，Full 没有对应错误。这些日志确认中断存在，但不单独证明是服务故障还是条件相关的响应延迟。论文保留实际总体结果，同时明确其解释限制。

## 失败发生在哪里

| 配置与条件 | Pass | Missing | Build-first | Public-first | Hidden-first | Isolation-first |
|---|---:|---:|---:|---:|---:|---:|
| Luna Full | 23 | 5 | 0 | 10 | 2 | 0 |
| Luna Contract Only | 9 | 3 | 0 | 20 | 8 | 0 |
| Pro Full | 25 | 0 | 0 | 12 | 3 | 0 |
| Pro Contract Only | 6 | 18 | 0 | 10 | 6 | 0 |
| Qwen Full | 12 | 4 | 2 | 15 | 6 | 1 |
| Qwen Contract Only | 1 | 1 | 0 | 33 | 5 | 0 |

关键不是逐格复述这个表，而是三点：

1. Luna Full-only 的 17 题对应 Contract-only 11 次 Public、6 次 Hidden 失败；Qwen 的 12 题对应 10 次 Public、2 次 Hidden 失败。
2. Luna/Qwen 在 Full 下反而有更多缺交（5 vs 3、4 vs 1）。二者的成功收益不来自更高的提交可用率。
3. Full 下 Luna 仍有 12 次行为首次失败，Qwen 仍有 21 次。源码证据有用，但行为重建依然困难。

两组 benchmark 测试均不向 agent 公开。不能把 Public/Hidden 差异称为“对公开测试过拟合”。First gate 也不是自动获得的语义根因标注。

## 中断与条件集合敏感性

| 分析集合 | Luna | Pro | Qwen |
|---|---|---|---|
| 两臂都交付 | 34 对：23 vs 8，+44.1 pp | 22 对：11 vs 6，+22.7 pp | 35 对：12 vs 1，+31.4 pp |
| 两臂均无指定 LLM 错误记录 | 28 对：18 vs 7，p=0.0127 | 22 对：11 vs 6，p=0.125 | 40 对：12 vs 1，p=0.00342 |

指定错误包括 `LLMTimeoutError`、`LLMServiceUnavailableError`、`LLMRateLimitError`、`LLMBadRequestError`。任一臂出现即从该敏感性集合排除，不根据通过与否排除。这里的 p 为各敏感性分析的未校正探索性值，不能和主表校正值混写。

Luna 的方向在排除这些错误后仍保持；Qwen 的保留轨迹没有这些错误类型。Pro 移除 18 个超时对应的整对任务后，方向仍为正，但只有六对 Full-only、一对 Contract-only，精确 p=0.125。这既不能证明没有收益，也不能用全样本 p 值宣称超时无关紧要。

条件集合会受到选择偏差，不是“排掉坏数据后重新定义 benchmark”。主表仍保留 40 题原始分母，不把 22/28/34/35 当作新的正式样本。

按仓库整簇重采样的 95% 区间：Luna [15.8, 52.6] pp，Pro [30.8, 64.1] pp，Qwen [12.5, 42.5] pp。区间沿用观测到的中断结果，不能修复 Pro 的解释问题。

## 反向结果与剩余困难

Luna 有三个 Contract-only 成功而 Full 失败的任务，Pro 和 Qwen 各有一个。因此不能写“源码对每题都有效”或把相对收益当成确定性的单题因果结论。一轮配对运行不足以区分偶然性和信息负担。

构建组成的探索性统计：样本中 earlier 27 题、later 13 题。Luna 分别为 Full/Contract 21/7 与 2/2；Pro 为 24/5 与 1/1；Qwen 为 12/1 与 0/0。净收益集中在 earlier 组，但该分组与任务结构相关，且 later 样本只有 13 题。这一现象可以作为后续选案例的线索，暂不升格为主文的“难任务源码无效”结论。

## 实验控制核对

- 三模型样本与本地预选 JSON 的 40 条任务记录一致，全部属于当前论文的 150 题。
- 120 个配对的 agent 配置差异仅为 `source_context` 与 `ablation_arm`。
- 去掉两个源码可见性说明段后，配对 `TASK.md` 完全相同。
- 所有 Full 初始 workspace inventory 均记录 repo 存在，所有 Contract-only 均记录 repo 不存在；测试与 source-location hints 均不公开。
- 120 个模型–任务对中，两臂都产生 evaluator 结果的每一对，capsule digest 相同。
- 两臂共享各自配置的 3600 秒超时、131072 context、8192 output reserve。
- 持久化 OpenHands 状态全部记录 `max_iterations=500`。Pro 另有 harness override=120；Luna/Qwen 的该 override 为空。不能照原计划写“三模型均严格 120 步”。
- Luna/Pro agent 用 bridge 网络，Qwen 用 host 网络以访问本地模型服务；常见源码分发站点通过 host mappings 阻断。evaluator 网络为 none。不能把 agent 端这些设置描述为完整网络沙箱或证明任何旁路都不存在。
- 两个外层 `run.status != passed` 的产物通过了全部四门槛（Pro/bleach Full；Qwen/attrs Full）。按功能门槛计分，与包内 summary 一致。
- 33 个 `.infra_*` 目录（Luna 31、Pro 2）作为历史尝试保存，不加入 240 条分母，也不用于挑选最佳结果。部分目录是中断尝试，不能把 33 直接称为 33 次完整评测。

对 Contract-only 主事件中的典型外部获取命令做了有限扫描；命中主要涉及标准库、允许依赖和自身代码检查。扫描不等于完整轨迹与网络流量审计，没有据此声称旁路不存在。

## 推荐的论文写法

主文标题：**Source Evidence Improves Behavioral Reconstruction**。

主文一张配对表、三段即可：

1. 报告真实 paired gains，Luna/Qwen 为主要可解释证据，Pro 的超时限制紧邻其结果。
2. 解释 Full-only 对应 Contract-only 的行为失败，说明收益不只是交付差异。
3. 说明 Full 仍有行为失败，收束为“仓库证据帮助恢复能力，但跨新边界的行为保持仍需独立验证”。

可用于摘要的实测句子：

> A paired source-evidence ablation on 40 tasks increases GPT-5.6 Luna's success from 22.5% to 57.5% and Qwen's from 2.5% to 30.0%. Their Full-only successes correspond to behaviorally failing Contract-only artifacts, showing a benefit beyond package delivery.

主文不写：

- “三模型均证明纯粹的源码因果收益为 27.5–47.5 pp”。
- “源码使模型更懂依赖闭包”，除非追加过程证据。
- “这是模型强弱的新排行榜”，因为不同模型的 runtime 设置与服务条件不同。
- 把 Full 的上游测试、文档和资源作用都归结为源码文本。
- 用此前的预测表格或主实验历史 Full 成绩替代本次配对运行。

## 文件与复现

- `analyze.py`：任务级核对、计分、配对检验和区间；仅依赖 Python 与 NumPy。
- `task_outcomes.csv`：240 条保留结果，含门槛、中断标签、设置和原始记录相对路径。
- `paired_outcomes.csv`：120 个模型–任务配对，含 Full-only/Contract-only 等关系。
- `statistics.json`：主统计与敏感性结果。
- `verification.json`：样本、配置与 evaluator 检查、历史尝试列表、wrapper 状态差异。
- `api_empty_review_queue.csv`：24 个有指定 API 错误且未交付的保留 cell，供需要时回查，不自动重跑。
- `source_ablation_table.tex`：根据统计生成的实测表。

本机原始记录位于 Git 忽略的 `experiments/source_ablation_review_20260913/source-ablation-40-r1-full/`。解包时只复制常规文件，拒绝绝对路径和 `..`，不执行包内脚本；仓库快照和 submission 未完整展开到本地副本，原始压缩包完整保留。需要在其他机器复算时，把原包安全解出后传入：

```text
python -B reports/paper_analysis/source_ablation_40_20260913/analyze.py --records <extracted>/source-ablation-40-r1-full
```

LaTeX 已更新：方法、结果实测表、摘要、Introduction、Discussion、Conclusion 和量化附录。主实验的 900 条记录、原有图和分类均未更改。修改前正文保存于 `docs/archive/snapshots/source_ablation_results_20260913/main.tex.txt`。本轮不编译或渲染。
