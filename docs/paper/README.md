# Paper Documents

> **Status: current index · Last verified: 2026-09-05**

| Document | Role |
| --- | --- |
| **[manuscript.md](manuscript.md)** | **Paper draft (Markdown). This is the write-up to read.** |
| [FSE LaTeX draft](fse26/README.md) | Optional ACM `acmart` copy; not required |
| [Harness-Bench structure mapping](01_harness_bench_structure_mapping.md) | What to imitate, what not to imitate |
| [Research Questions](02_research_questions.md) | Questions and hypotheses |
| [Experimental Analysis chapter](08_experimental_analysis_chapter.md) | Results & Analysis 分母和 Finding 顺序 |

论文主套件是 **冻结 Python-150 + Hard-50**（freeze v2
`6c20ff0307762503a73cbb9ff32e9992c6446e4b17483a68373027be58cbf419`）。
**Headline 实证是 Python-150 Official Main**（2026-09-04/05）：Pro **115/150**，
Flash **108/150**，Luna **102/150**，Qwen **63/150**，OSS **36/150**。写回
[python150_prime_v2_analysis_20260905](../../reports/paper_analysis/python150_prime_v2_analysis_20260905/README.md)。
官方 Hard-50 进附录。200 题四模型机械表见
[python200_prime_v2_results_20260905](../../reports/paper_analysis/python200_prime_v2_results_20260905/README.md)
（无 Pro）。
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
