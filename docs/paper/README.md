# Paper Documents

> **Status: current index · Last verified: 2026-09-02**

| Document | Role |
| --- | --- |
| [FSE LaTeX draft](fse26/README.md) | Compilable ACM `acmart` manuscript generated from the user-provided template |
| [Manuscript zero draft](00_manuscript_zero_draft.md) | English argument draft; final main-table values and bibliography remain pending |
| [Harness-Bench structure mapping](01_harness_bench_structure_mapping.md) | What to imitate, what not to imitate, and the proposed seven-section paper spine |
| [Research Questions](02_research_questions.md) | Questions and hypotheses |
| [Token utility results](03_results_token_utility.md) | RQ3 cost slice + RQ5 lift-type \(T^\*\)（旧 150+E50 轨迹） |
| [RQ6 Public-feedback](04_results_rq6.md) | Information-boundary ablation (Flash-12; not main table) |
| [Failure Taxonomy](05_failure_taxonomy.md) | Failure coding framework |
| [Paper Outline](06_paper_outline.md) | Manuscript structure |
| [Top-conference readiness plan](07_top_conference_readiness_plan.md) | Execution gates before submission |
| [Known Limitations](limitations.md) | Scope and validity limits |

论文主套件是 **冻结 Python-150 + Hard-50**（suite 仍 `unreleased`）。整套 Flash
收到包的 **132/200（66.0%）只能作为 audit headline**：17 题未启动，16 题在离线
依赖安装阶段失败，59 题触发 context-window audit，去重后严格替换集合为 84 题。
闭环前不作为最终主表。分析见
[Python-200′ candidate readout](../../reports/paper_analysis/python200_hard_main_20260829/paper_readout.md)，
论文段落底稿见
[Results draft](../../reports/paper_analysis/python200_hard_main_20260829/results_draft.md)。
题集身份见 [STATUS.md](../STATUS.md)；Hard-50 完成记录见
[PLAN_HARD50_EXPANSION.md](../archive/plans/PLAN_HARD50_EXPANSION.md)。

旧 150 + External-50 的 21.5%–72.5% 是 superseded 对照，不是新主表。
External-50 升格计划（合同升格已完成；copy-all / freeze 仍见该文）在
[PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md](../archive/plans/PLAN_EXTERNAL50_TO_PYTHON150_QUALITY.md)
（独立 freeze；不并进 150，也不进新主表）。

Hard-50 Phase 0 卡片阶段已结束：50 题已 release 到 `benchmark/hard50/` 与
`benchmark/python200_hard_tasks/`。**不要**写「仅有 design cards」。

Current evidence and numerical status remain in [../STATUS.md](../STATUS.md)
and [../FINDINGS.md](../FINDINGS.md). The live cost method is
[../METHOD_V1.md](../METHOD_V1.md). RQ6 Public-feedback is
[../METHOD_RQ6_PUBLIC_FEEDBACK.md](../archive/methods/METHOD_RQ6_PUBLIC_FEEDBACK.md). Optional
DeepSeek Harness / Codex runtime ablation is
[../METHOD_AGENT_RUNTIME.md](../METHOD_AGENT_RUNTIME.md); it is not Official
Main. Metric definitions are in [../EVALUATION.md](../EVALUATION.md).
