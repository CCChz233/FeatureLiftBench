# FeatureLiftBench 分析与审计报告

> **Status: reference · Last verified: 2026-09-14**

这里保存派生分析，原始运行属于 `experiments/`。论文输入只按
[paper_sources.json](../docs/paper/paper_sources.json) 选择。

| 报告 | 当前用途 |
| --- | --- |
| [150 题逐题分析](paper_analysis/python150_prime_v2_analysis_20260905/README.md) | 900 条主结果、门禁、用量及过程信息 |
| [最终统计汇总](paper_analysis/python150_paper_analysis_final/README.md) | 配对统计与数值交叉检查 |
| [40 题源码消融](paper_analysis/source_ablation_40_20260913/REPORT.md) | 240 条实际结果与敏感性分析 |
| [源码暴露分析](paper_analysis/source_exposure/diagnosis/REPORT.md) | 900 条轨迹派生证据，明确检测边界 |
| [旧分析索引](paper_analysis/README.md) | 历史范围与旧方法结果；不自动进入论文 |

本轮整理不会重新解释旧报告中的日期、批次、排除规则或模型版本。
按现有源文件重建数值不等于原始结果包已恢复完整。当前缺口见 [STATUS](../docs/STATUS.md)。
