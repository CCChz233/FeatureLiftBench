# FeatureLiftBench Architecture

FeatureLiftBench is organized into four top-level layers. Three define the product; one holds local experiment artifacts.

## Layers

```text
docs/           Layer 1 — Documentation (human-facing)
benchmark/      Layer 2 — Dataset (tasks, sources, Oracle; no agent code)
harness/        Layer 3 — Tooling (evaluator + optional agent runner)
experiments/    Layer 4 — Local runs (gitignored; not part of the benchmark definition)
```

## Data flow

```text
benchmark/tasks/<task_id>/          # Question
benchmark/submissions/<id>/oracle/  # Reference answer (local, gitignored)
         │
         ▼
harness/featureliftbench/evaluator  # Grader (core contract)
         │
         ▼
experiments/<run_id>/eval/          # Scores and logs
```

Optional agent path:

```text
benchmark/tasks/  ──►  harness/agent_runner  ──►  submission/  ──►  evaluator  ──►  experiments/
```

The benchmark definition does **not** depend on any agent. `eval` and `validate-task` work without `run-agent`.

## Layer responsibilities

| Layer | Path | Contains | Does not contain |
| --- | --- | --- | --- |
| Docs | `docs/` | Architecture, task catalog, design notes, limitations | Executable code, task snapshots |
| Benchmark | `benchmark/` | `tasks/`, `sources/`, `vendor-wheels/`, local `submissions/` | Evaluator, agent harness, experiment logs |
| Harness | `harness/` | `featureliftbench/`, `config/`, `scripts/`, `tests/` | Per-task `repo/` snapshots |
| Experiments | `experiments/` | Agent/eval run output | Benchmark schema or task data |

## Harness internals

| Component | Module | Role |
| --- | --- | --- |
| Evaluator | `evaluator.py`, `validate.py`, `scoring.py` | Grade submissions; define the benchmark contract |
| Agent runner | `agent_runner.py`, `agent_adapters.py` | Optional; produce submissions via external agents |
| CLI | `cli.py` | `validate-task`, `eval`, `score`, `run-agent` |
| Paths | `paths.py` | Single source of truth for repo layout |

## Path constants

All code should prefer [`harness/featureliftbench/paths.py`](../harness/featureliftbench/paths.py):

- `TASKS_DIR` → `benchmark/tasks/`
- `SUBMISSIONS_DIR` → `benchmark/submissions/`
- `EXPERIMENTS_DIR` → `experiments/`
- `CONFIG_DIR` → `harness/config/`

CLI shorthand: `benchmark` or `benchmark/tasks` resolves to `TASKS_DIR` for `run-agent`.

## Evolution rules

- Add or remove tasks under `benchmark/tasks/` only.
- Do not fork alternate collections or schemas.
- Oracle stays local (`benchmark/submissions/`, gitignored).
- Prune old directories under `experiments/` when disk is tight.

## Related docs

- [TASK_FORMAT.md](TASK_FORMAT.md) — canonical task directory and metadata spec
- [DIRECTORY.md](DIRECTORY.md) — full directory map
- [benchmark_tasks.md](benchmark_tasks.md) — task catalog and CLI examples
- [limitations.md](limitations.md) — known defects
