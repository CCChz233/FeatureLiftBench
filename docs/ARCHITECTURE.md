# Architecture & Repository Layout

FeatureLiftBench: four layers (three product + local experiments).

## Layers & data flow

```text
docs/           Layer 1 — documentation
benchmark/      Layer 2 — dataset (tasks, staging, sources, oracle)
harness/        Layer 3 — evaluator + agent tooling
experiments/    Layer 4 — local runs (gitignored)
```

```text
benchmark/tasks/<task_id>/          # Question
benchmark/submissions/<id>/oracle/  # Reference submission (gitignored)
         │
         ▼
harness/featureliftbench/evaluator
         │
         ▼
experiments/<run_id>/eval/

Optional: benchmark/tasks/ → agent_runner → submission/ → evaluator
```

Benchmark definition does **not** require an agent (`eval`, `validate-task` work standalone).

## Top-level tree

```text
FeatureLiftBench/
  README.md
  RUN.md                 # Quick run (vLLM / API)
  setup.sh
  TODO.md                # Engineering backlog (not doc index)

  docs/                  # Layer 1 — see docs/README.md
  benchmark/
    tasks/               # Main leaderboard (batch-0 → 100)
    staging/             # Candidates — see EXPANSION.md
    sanity/              # 3 smoke tasks
    sources/             # vibe_app master; OSS uses pinned repo/ per task
    vendor-wheels/
    submissions/         # Oracle (gitignored)
  harness/
    featureliftbench/    # Python package
    config/
    scripts/
    tests/
  experiments/           # Run outputs (gitignored)
```

## Benchmark layer

| Path | Purpose | Git |
| --- | --- | --- |
| `benchmark/tasks/` | Official hard tasks | Yes |
| `benchmark/staging/` | Trial tasks before promote | Yes |
| `benchmark/sanity/` | Smoke appendix | Yes |
| `benchmark/sources/` | Curated upstream (e.g. vibe_app) | Yes |
| `benchmark/submissions/` | Oracle answers | Gitignored |

Per-task layout: [TASK_FORMAT.md](TASK_FORMAT.md).

## Harness

| Component | Module | Role |
| --- | --- | --- |
| Evaluator | `evaluator.py`, `validate.py`, `scoring.py` | Grading contract |
| Runtime safety | `resource_limits.py`, `run_limited.py` | Memory caps (Linux) |
| Agent runner | `agent_runner.py`, `agent_adapters.py` | Optional agent path |
| CLI | `cli.py` | `validate-task`, `eval`, `run-agent` |
| Paths | `paths.py` | `TASKS_DIR`, etc. |

### Key scripts (`harness/scripts/`)

| Script | Role |
| --- | --- |
| `preflight.py` | Pre-run env / API / mini check |
| `server_setup.sh` | Called by `./setup.sh` |
| `verify_all_oracles.py` | Oracle regression |
| `build_oracle_submission.py` | Build oracle from task |
| `analyze_benchmark_suite.py` | Suite analysis |
| `reeval_suite.py` | Re-eval without re-running agent |
| `list_tasks.py` | Task listing (default: `tasks/` only) |

Path constants: [`harness/featureliftbench/paths.py`](../harness/featureliftbench/paths.py). CLI `benchmark` → `benchmark/tasks/`.

## Experiments output

```text
experiments/mini-swe-agent/<run_id>/
  suite.json
  <task_id>/
    run.json
    agent/trajectory.json
    submission/
    eval/result.json
```

Safe to delete old `experiments/` locally. **Do not** delete `benchmark/tasks/` or `harness/`.

## Evolution

- **batch-0 (50 tasks):** frozen — no edits for expansion scope.
- **batch-1:** add via staging only — [EXPANSION.md](EXPANSION.md).
- No forked schemas or second benchmark collection.
- Oracle stays gitignored under `benchmark/submissions/`.

## Path migration (historical)

| Old | New |
| --- | --- |
| `tasks/` | `benchmark/tasks/` |
| `outputs/` | `experiments/` |
| `featureliftbench/` | `harness/featureliftbench/` |
| `KNOWN_LIMITATIONS.md` | `docs/limitations.md` |

## Related docs

- [docs/README.md](README.md) — documentation index
- [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md) — reproducibility contract
- [TASK_FORMAT.md](TASK_FORMAT.md) — per-task spec
- [EXPANSION.md](EXPANSION.md) — 50→100 workflow
