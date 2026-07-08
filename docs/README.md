# FeatureLiftBench Docs

This directory is intentionally small at the top level. Core benchmark and paper-planning docs live here; language-specific docs live in subdirectories.

## Core Docs

| File | Purpose |
|---|---|
| [00_overview.md](00_overview.md) | Benchmark goal, scope, and status |
| [01_task_definition.md](01_task_definition.md) | Shared FeatureLift task contract |
| [02_research_questions.md](02_research_questions.md) | Shared RQs and experimental handles |
| [03_evaluator_and_scoring.md](03_evaluator_and_scoring.md) | Evaluation and scoring design |
| [04_experiment_protocol.md](04_experiment_protocol.md) | Shared experiment protocol |
| [05_failure_taxonomy.md](05_failure_taxonomy.md) | Failure labels and detection notes |
| [06_task_schema.md](06_task_schema.md) | Canonical task package schema |
| [07_incremental_task_rules.md](07_incremental_task_rules.md) | Task lifecycle and promotion gates |
| [06_paper_outline.md](06_paper_outline.md) | Paper outline |

## Language Splits

- [python/](python/) — Python split design, repo criteria, inventory, difficulty rubric, examples.
- [go/](go/) — Go split design, repo criteria, inventory, difficulty rubric, examples.

Python and Go are FeatureLiftBench language splits, not separate benchmarks.

## Task Design Notes

- [task_designs/](task_designs/) — Python per-task design notes.
- [go_task_designs/](go_task_designs/) — Go per-task design notes and templates.

These are reference notes for task auditing and construction; they are not the entry point for the benchmark design.
