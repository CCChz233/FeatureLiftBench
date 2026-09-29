# FeatureLiftBench 文档入口

> **Status: current · Last verified: 2026-09-29**

当前论文：150 个 Python 任务、126 个仓库、132 个固定快照；六配置共 900 条逐题结果。正文、图和数据位置以 [论文 README](paper/README.md) 和 [输入清单](paper-workbench/paper_sources.json) 为准。

| 需要 | 入口 |
| --- | --- |
| 看论文与正式图片 | [docs/paper](paper/README.md) |
| 改某一张图 | [逐图独立脚本](paper-workbench/figures/standalone/README.md) |
| 复算论文图表与检查 | [工作流](paper-workbench/WORKFLOW.md) |
| 查 RQ2 150 题草稿 | [草稿说明](paper-workbench/figures/drafts/rq2_150/README.md) |
| 查项目整体结构 | [项目地图](PROJECT_MAP.md) |
| 查论文工作区 | [数据与复现](paper-workbench/README.md) · [图片代码](paper-workbench/figures/README.md) · [数值证据](paper-workbench/writing/README.md) |
| 看结果与缺口 | [状态](STATUS.md) · [研究发现](FINDINGS.md) |
| 查公开材料的历史盘点 | [2026-09-26 发布计划](PUBLIC_RELEASE_PLAN.md) |
| 理解任务与评测 | [Benchmark 设计](BENCHMARK_DESIGN.md) · [评测协议](EVALUATION.md) · [验证门槛](BENCHMARK_VALIDATION_GATE.md) |
| 维护与失败标注 | [维护手册](REPOSITORY_MAINTENANCE.md) · [失败分析协议](FAILURE_ANALYSIS_PROTOCOL.md) · [标注 SOP](FAILURE_ANALYSIS_SOP.md) |
| 看历史记录 | [论文清理归档](archive/paper_cleanup_20260929/README.md) · [文档归档](archive/README.md) |

论文检查：`python -B scripts/paper.py check`。文档链接检查：`python -B scripts/check_docs.py`。
