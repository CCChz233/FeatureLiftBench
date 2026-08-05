# Python split docs

> **Documentation status: reference · Last verified: 2026-08-04**

Python language split 设计文档。Benchmark 共享定义见
[BENCHMARK_DESIGN.md](../../BENCHMARK_DESIGN.md)。当前 release、规模与 freeze：
[STATUS.md](../../STATUS.md)。

| Doc | Purpose |
| --- | --- |
| [00_python_design_principles.md](00_python_design_principles.md) | Python 出题设计原则 |
| [01_python_repo_selection_criteria.md](01_python_repo_selection_criteria.md) | 上游 repo 筛选标准 |
| [02_python_repo_task_inventory.md](02_python_repo_task_inventory.md) | 仓库、任务和规模汇总；机器事实源索引 |
| [03_python_difficulty_rubric.md](03_python_difficulty_rubric.md) | 难度与校准 rubric |
| [04_python_task_examples.md](04_python_task_examples.md) | 示例任务说明 |
| [../LIFT_TAXONOMY.md](../LIFT_TAXONOMY.md) | Direct / Adapted / Composite lift 类型（题层能力分布） |
逐题事实源是 `benchmark/tasks/*/metadata.json` 和机器审计，不再维护重复的
手写 task-design notes。
