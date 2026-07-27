# FeatureLiftBench 文档

这里是项目文档的唯一入口。上游仓库自带的 README/RST、任务 `TASK.md` 和
实验轨迹属于输入或证据，不属于项目说明书，不在本索引中维护。

## 先读

| 目的 | 文档 |
| --- | --- |
| 快速了解项目 | [项目 README](../README.md) |
| 看当前是否可跑、还缺什么 | [STATUS.md](STATUS.md) |
| 理解核心设计 | [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md) |
| 理解完整方法 | [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) |
| 在服务器运行 v3 Python-150 | [SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md) |

当前状态（2026-07-27）：Python v3 External Main **150/150 ready**，
source registry **126 external repositories / 132 snapshots**，Docker Oracle
**450/450**、对抗样例 **12/12**。active freeze 以机器指针文件为准。
v3 模型 baseline 尚未产生；已有模型结果都属于历史
`mixed_snapshot_v1` 条件。

## 权威顺序

发生冲突时按以下顺序处理：

1. 机器冻结与审计：
   [`current_benchmark_freeze.json`](../artifacts/research_analysis/v3/current_benchmark_freeze.json)、
   [`v3_main_readiness.md`](../reports/audits/v3_main_readiness.md) 和
   [`benchmark/sources/registry.json`](../benchmark/sources/registry.json)。
2. 设计与任务规范：
   [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md)、
   [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md)、
   [FULL_REPOSITORY_SOURCE_POLICY.md](FULL_REPOSITORY_SOURCE_POLICY.md)。
3. 运行与评测：
   [03_evaluator_and_scoring.md](03_evaluator_and_scoring.md)、
   [04_experiment_protocol.md](04_experiment_protocol.md)、
   [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md)。
4. 手写状态与研究叙事：
   [STATUS.md](STATUS.md)、[CURRENT_RESEARCH.md](CURRENT_RESEARCH.md)、
   [EXPERIMENTS.md](EXPERIMENTS.md)、[FINDINGS.md](FINDINGS.md)。

## 规范

| 文档 | 内容 |
| --- | --- |
| [BENCHMARK_DESIGN_PRINCIPLES.md](BENCHMARK_DESIGN_PRINCIPLES.md) | 八条 Full-Repository / No-Hint 原则 |
| [BENCHMARK_DESIGN.md](BENCHMARK_DESIGN.md) | 构念、信息边界、指标和实验设计 |
| [TASK_DESIGN_RULES.md](TASK_DESIGN_RULES.md) | 公开契约、私有评测映射和准入门禁 |
| [FULL_REPOSITORY_SOURCE_POLICY.md](FULL_REPOSITORY_SOURCE_POLICY.md) | canonical source、revision、archive、digest |
| [06_task_schema.md](06_task_schema.md) | task package 与 metadata schema |
| [07_incremental_task_rules.md](07_incremental_task_rules.md) | staging、验证和 promotion 生命周期 |
| [limitations.md](limitations.md) | 当前可支持与不可外推的结论 |

## 实验与论文

| 文档 | 内容 |
| --- | --- |
| [RUN.md](../RUN.md) | 本地运行速查 |
| [SERVER_RUNBOOK_PYTHON150.md](SERVER_RUNBOOK_PYTHON150.md) | 正式服务器运行、恢复和验收 |
| [EXPERIMENT_ARMS.md](EXPERIMENT_ARMS.md) | Main 与各消融臂 |
| [EXPERIMENTS.md](EXPERIMENTS.md) | 已有结果、缺失结果和口径 |
| [FINDINGS.md](FINDINGS.md) | 现有证据能支持的结论 |
| [02_research_questions.md](02_research_questions.md) | 研究问题 |
| [05_failure_taxonomy.md](05_failure_taxonomy.md) | 失败分类 |
| [06_paper_outline.md](06_paper_outline.md) | 当前论文结构 |
| [REPORTS_INDEX.md](REPORTS_INDEX.md) | 审计与结果文件索引 |

## 语言分区

- [python/](python/)：当前 Python-150 主榜的仓库选择、任务分布、难度和示例。
- [go/](go/)：Go calibration；尚不是 paper-ready Main。
- [go_task_designs/](go_task_designs/)：仍在使用的 Go pilot 设计笔记。

Python 的旧逐题设计笔记已经删除。它们只覆盖部分题目、重复
`metadata.json`/`public_spec`，并含源码定位信息。当前出题事实源是任务包、
source registry、reference registry 和可执行门禁。

## 历史证据

- [`reports/python150_compliant_20260726/`](../reports/python150_compliant_20260726/)：
  v1 mixed-snapshot 四模型 candidate，不能作为 v3 baseline。
- [`reports/archive/v1_mixed_snapshot_runs_20260712.md`](../reports/archive/v1_mixed_snapshot_runs_20260712.md)：
  更早的冻结 run 集。
- [research_analysis/](research_analysis/)：仍可复查的 taxonomy 与轨迹证据；
  不再保存已废弃方法路线图或取消的独立审核包。

## 维护规则

1. 数字状态只在 [STATUS.md](STATUS.md) 汇总；其他文档链接到它。
2. 任务和 source 数量由机器文件生成，不手抄逐题长表。
3. `mixed_snapshot_v1` 与 v3 Full-Repository / No-Hint 结果严格分报。
4. 已完成的 sprint、迁移清单和废弃方法不留在当前 `docs/`。
5. 上游源码文档和原始实验证据不为“统一文风”而改写。
