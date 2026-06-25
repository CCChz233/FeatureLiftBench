# FeatureLiftBench Docs

Canonical docs for the **28-task unified benchmark**:

| Doc | Purpose |
| --- | --- |
| [CONCEPTS.md](CONCEPTS.md) | **Start here** — what we measure, how a task is defined, tests, submission |
| [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) | **Current baseline, spec gaps, fix priority** |
| [benchmark_tasks.md](benchmark_tasks.md) | Task catalog and run commands |
| [TASK_FORMAT.md](TASK_FORMAT.md) | Task directory and `metadata.json` spec |
| [limitations.md](limitations.md) | Harness / evaluator known issues |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Three-layer layout |
| [DIRECTORY.md](DIRECTORY.md) | Path map |

Design notes for individual tasks: [task_designs/](task_designs/) (human notes; machine spec is `TASK_FORMAT.md`).

A task design note is allowed to be speculative. A real task under `benchmark/tasks/` should only ship after source snapshot, public/hidden tests, metadata, forbidden imports, and oracle eval path are ready.
