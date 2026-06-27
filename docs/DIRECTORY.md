# FeatureLiftBench Directory Map

See [ARCHITECTURE.md](ARCHITECTURE.md) for the three product layers plus local experiments.

## Top-level layout

```text
FeatureLiftBench/
  README.md
  RUN.md                # Quick run cheatsheet (vLLM / SiliconFlow)
  pyproject.toml
  TODO.md

  docs/                 # Layer 1: documentation
  benchmark/            # Layer 2: dataset
  harness/              # Layer 3: evaluator + agent tooling
  experiments/          # Layer 4: local runs (gitignored)
```

## Layer 1: `docs/`

| Path | Purpose |
| --- | --- |
| [CONCEPTS.md](CONCEPTS.md) | Core concepts: feature definition, tests, submission, scoring |
| [SETUP.md](SETUP.md) | Environment, `./setup.sh`, `.env`, server deploy, preflight |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Three-layer design and data flow |
| [TASK_FORMAT.md](TASK_FORMAT.md) | Canonical task directory and metadata spec |
| [DIRECTORY.md](DIRECTORY.md) | This file |
| [benchmark_tasks.md](benchmark_tasks.md) | 50 hard task catalog and CLI examples |
| [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) | Current baseline, spec gaps, fix priority |
| [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) | Local vLLM / API experiment summaries |
| [limitations.md](limitations.md) | Known defects |
| [task_designs/](task_designs/) | Per-task design notes |

## Layer 2: `benchmark/`

| Path | Purpose | Git |
| --- | --- | --- |
| `benchmark/tasks/` | 50 hard benchmark tasks | Yes |
| `benchmark/sanity/` | 3 smoke tasks (appendix) | Yes |
| `benchmark/sources/` | Upstream master copies (vibe_app) | Yes |
| `benchmark/vendor-wheels/` | Wheels for Oracle builder | Yes |
| `benchmark/submissions/` | Oracle answers | Gitignored |

Per-task layout:

```text
benchmark/tasks/<task_id>/
  metadata.json
  requirements.lock
  repo/
  public_tests/
  hidden_tests/
  evaluation/
```

## Layer 3: `harness/`

| Path | Purpose |
| --- | --- |
| `harness/featureliftbench/` | Python package: evaluator, agent runner, CLI |
| `harness/featureliftbench/mini_live_runner.py` | In-process mini with per-step trajectory snapshots (live token progress) |
| `harness/featureliftbench/paths.py` | Repo path constants |
| `harness/config/` | Agent config (`agents.example.toml`) |
| `harness/scripts/` | Maintenance and analysis scripts |
| `harness/scripts/archive/` | One-time task-scaffolding tools |
| `harness/tests/` | Unit tests for the harness |

### CLI commands

```bash
pip install -e .

featureliftbench validate-task benchmark/tasks/<task_id>
featureliftbench eval benchmark/tasks/<id> benchmark/submissions/<id>/oracle \
  --output experiments/eval-smoke
featureliftbench run-agent benchmark/tasks \
  --agent mini-swe-agent \
  --output experiments/mini-swe-agent/<run_id>
```

Shorthand: `run-agent benchmark` resolves to `benchmark/tasks/`.

### Active scripts

| Script | Use |
| --- | --- |
| `harness/scripts/list_tasks.py` | List/filter tasks |
| `harness/scripts/analyze_benchmark_suite.py` | Per-run enrichment + optional `--aggregate` |
| `harness/scripts/summarize_experiment_runs.py` | Cross-run failure taxonomy + metadata join |
| `harness/scripts/reeval_suite.py` | Re-eval existing submissions (no agent re-run) |
| `harness/scripts/build_oracle_submission.py` | Build/verify Oracle |

## Layer 4: `experiments/`

Local agent and eval outputs (formerly `outputs/`). Safe to delete old runs.

```text
experiments/mini-swe-agent/<run_id>/
  suite.json
  <task_id>/
    run.json
    agent/trajectory.json
    workspace/
    submission/
    eval/result.json
```

## Path migration (breaking change)

| Old | New |
| --- | --- |
| `tasks/` | `benchmark/tasks/` |
| `submissions/` | `benchmark/submissions/` |
| `outputs/` | `experiments/` |
| `scripts/` | `harness/scripts/` |
| `config/` | `harness/config/` |
| `featureliftbench/` | `harness/featureliftbench/` |
| `sources/` | `benchmark/sources/` |
| `KNOWN_LIMITATIONS.md` | `docs/limitations.md` |

## What is safe to delete locally

| Path | Safe to delete? |
| --- | --- |
| `experiments/` | Yes (experiment logs) |
| `.agent-venv/` | Yes |
| `.pytest_cache/` | Yes |
| `benchmark/submissions/` | Only if Oracle can be rebuilt |
| `benchmark/tasks/` | **No** |
| `harness/` | **No** |
