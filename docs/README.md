# FeatureLiftBench Docs

文档入口。按读者角色选择路径；**当前仓库状态**见 [STATUS.md](STATUS.md)（手写摘要）与 [research_analysis/V11_IMPLEMENTATION_STATUS.md](research_analysis/V11_IMPLEMENTATION_STATUS.md)（脚本生成）。

## 快速导航

| 我想… | 从这里开始 |
| --- | --- |
| 了解 benchmark 是什么 | [00_overview.md](00_overview.md) → [01_task_definition.md](01_task_definition.md) |
| 跑实验 | 根目录 [RUN.md](../RUN.md) · [04_experiment_protocol.md](04_experiment_protocol.md) |
| 看出题 / promote 规则 | [07_incremental_task_rules.md](07_incremental_task_rules.md) · [.agents/skills/](../.agents/skills/) |
| 查 Python 150 题清单 | [python/02_python_repo_task_inventory.md](python/02_python_repo_task_inventory.md) |
| 查论文 / v1.1 门禁 | [research_analysis/](research_analysis/) · [06_paper_outline.md](06_paper_outline.md) |
| 查已知局限 | [limitations.md](limitations.md) |

## Core Docs（规范层）

长期维护的 benchmark 定义；数字型状态以 [STATUS.md](STATUS.md) 为准，不在此重复。

| File | Purpose |
| --- | --- |
| [00_overview.md](00_overview.md) | Benchmark goal, scope, evaluation philosophy |
| [01_task_definition.md](01_task_definition.md) | Shared FeatureLift task contract |
| [02_research_questions.md](02_research_questions.md) | Shared RQs and experimental handles |
| [03_evaluator_and_scoring.md](03_evaluator_and_scoring.md) | Evaluation and scoring design |
| [04_experiment_protocol.md](04_experiment_protocol.md) | Shared experiment protocol |
| [05_failure_taxonomy.md](05_failure_taxonomy.md) | Failure labels and detection notes |
| [06_task_schema.md](06_task_schema.md) | Canonical task package schema |
| [07_incremental_task_rules.md](07_incremental_task_rules.md) | Task lifecycle and promotion gates |
| [06_paper_outline.md](06_paper_outline.md) | Paper outline |
| [limitations.md](limitations.md) | Known benchmark and evaluator limitations |
| [STATUS.md](STATUS.md) | Current project status (living summary) |

## Language Splits

Python 与 Go 是 FeatureLiftBench 的 language split，共享同一 task 语义与评分哲学。

- [python/](python/) — 设计原则、repo 筛选、**150 题 inventory**、难度 rubric、示例（索引：[python/README.md](python/README.md)）
- [go/](go/) — Go split 设计（calibration / seed 阶段；索引：[go/README.md](go/README.md)）

## Task Design Notes

- [task_designs/](task_designs/) — Python 按题设计笔记（106 篇 + `TEMPLATE.md`）
- [go_task_designs/](go_task_designs/) — Go 按题设计笔记

这些是 maintainer 参考，**不是** agent 或论文读者的入口；落地 spec 以 `benchmark/tasks/*/TASK.md` 为准。

## Research & Paper

- [research_analysis/](research_analysis/) — v1.1 硬化协议、Pilot、ECSM、taxonomy、Oracle 报告
- [paper_runs_frozen.md](paper_runs_frozen.md) — 冻结 formal run ID 与 leaderboard 口径
- [paper_tables.md](paper_tables.md) — 论文表格草稿
- [../reports/paper_analysis/](../reports/paper_analysis/) — 分析工件与 case studies

生成型 audit JSON/CSV 在 `artifacts/research_analysis/`；人类可读摘要优先放在 `docs/research_analysis/`。

## Operational & Agent

| Location | Purpose |
| --- | --- |
| [../RUN.md](../RUN.md) | 实验运行速查（Docker、suite、env） |
| [../.agents/skills/](../.agents/skills/) | Cursor agent：create / validate / promote / run-eval |

## Historical Engineering Docs（根目录）

以下文档保留 batch-0 / batch-1 扩题历史，**不是**当前 sprint 真相：

| File | Notes |
| --- | --- |
| [../TODO.md](../TODO.md) | 2026-06 batch-1 工程 backlog（已归档） |
| [../BATCH1_PLAYBOOK.md](../BATCH1_PLAYBOOK.md) | 50→100 扩题 playbook（已归档） |
| [../GO_FEATURELIFTBENCH_DESIGN.md](../GO_FEATURELIFTBENCH_DESIGN.md) | Go v2 早期路线；现行规范见 [go/](go/) |

## Reports & Evidence

| Location | Purpose |
| --- | --- |
| [../reports/](../reports/) | Sprint 报告、batch3 材料化、task audit（时间点快照） |
| [../evidence/](../evidence/) | batch-1 promote 验收证据（只读） |
| [../experiments/](../experiments/) | 运行输出（非文档源） |

## 文档维护规则

1. **Canonical**（`docs/00–07`）：规范变更时人工更新。
2. **Living status**（`STATUS.md` + 生成的 `V11_IMPLEMENTATION_STATUS.md`）：freeze / gate 变更时更新。
3. **Historical**（`reports/`、根目录 backlog）：写入后尽量不 retro-edit；过时处加 banner 或 superseded 链接。
4. **Task spec**（`benchmark/tasks/*/TASK.md`）：随题目生命周期变更，不与 meta 文档混整理。
