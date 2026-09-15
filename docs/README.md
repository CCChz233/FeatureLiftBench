# FeatureLiftBench 文档入口

> **Status: current · Last verified: 2026-09-14**

当前以新版 FSE 论文为主：150 题、126 仓库、132 快照，六配置共 900 条结果。
项目全貌先读 [PROJECT_MAP.md](PROJECT_MAP.md)，数字与缺口见 [STATUS.md](STATUS.md)。

| 需要 | 入口 |
| --- | --- |
| 写论文、更新图表和打包 | [论文工作流](paper/WORKFLOW.md) |
| 看最新正文与图表状态 | [论文 README](paper/README.md) |
| 查数据来源 | [paper_sources.json](paper/paper_sources.json) |
| 改单张图 | [绘图源码](paper/figures/scripts/README.md) |
| 查本轮整理与验证 | [FSE 同步记录](paper/FSE_SYNC_20260914.md) |
| 当前论文发现 | [FINDINGS.md](FINDINGS.md) |
| 理解任务与评测 | [设计](BENCHMARK_DESIGN.md) · [评测协议](EVALUATION.md) |
| 准备新运行 | [RUN.md](../RUN.md) · [服务器手册](SERVER_RUNBOOK_PYTHON200.md) |
| 查任务与原始运行 | [目录对应](paper/PAPER_FOLDERS.md) |
| 查历史研究与记录 | [历史文档](archive/README.md) · [派生报告](../reports/README.md) |
| 开发维护 | [维护手册](REPOSITORY_MAINTENANCE.md) · [脚本入口](../scripts/README.md) |

## 任务构建与方法参考

任务构建规范：[TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)、
[BENCHMARK_VALIDATION_GATE.md](BENCHMARK_VALIDATION_GATE.md)、
[失败分析协议](FAILURE_ANALYSIS_PROTOCOL.md)、[标注 SOP](FAILURE_ANALYSIS_SOP.md)。
来源与身份规则：[设计原则](BENCHMARK_DESIGN_PRINCIPLES.md)、
[完整源码政策](FULL_REPOSITORY_SOURCE_POLICY.md)、[参考规范](reference/README.md)。

历史/可选方法入口：[V1](METHOD_V1.md)、[runtime](METHOD_AGENT_RUNTIME.md)。
这些方法不进入当前 OpenHands Main 表。旧文档中的批次名称和分数按其原日期理解。

文档检查：`python -B scripts/check_docs.py`。
论文检查：`python -B scripts/paper.py check`。
