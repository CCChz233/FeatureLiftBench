# FeatureLiftBench

FeatureLiftBench evaluates whether coding agents can **extract one existing feature from an entangled repository** into a standalone, behavior-preserving Python package.

The agent receives a real repo snapshot, public tests, and task metadata. It must produce:

```text
submission/featurelifted/
  __init__.py
  ...
```

The evaluator runs public and hidden tests, rejects forbidden imports from the original package, and scores correctness plus extraction footprint.

## Current Status

| Item | Path / tool |
|------|-------------|
| Main benchmark | `benchmark/tasks/` (~100 hard tasks) |
| Smoke tasks | `benchmark/sanity/` (3 tasks) + CLI `smoke` suite (1 task) |
| **Experiment mainline** | **OpenHands + agent Docker + eval Docker** |
| **Run interface** | **`flb.local.toml` + `featureliftbench` CLI** |
| Legacy baseline | `mini-swe-agent` (not used for long-context claims) |

## How It Works (short)

```text
flb.local.toml + .env
    → featureliftbench run
    → preflight → OpenHands (agent Docker) → submission/
    → eval (eval Docker) → run.json / suite.json
```

Full implementation: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Commands: [RUN.md](RUN.md).

## Start Here

| Goal | Doc |
|------|-----|
| **Run experiments** | [RUN.md](RUN.md) |
| Architecture & modules | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| What we measure | [docs/CONCEPTS.md](docs/CONCEPTS.md) |
| Eval contract | [docs/BENCHMARK_SPEC.md](docs/BENCHMARK_SPEC.md) |
| Environment setup | [docs/SETUP.md](docs/SETUP.md) |
| Task format | [docs/TASK_FORMAT.md](docs/TASK_FORMAT.md) |
| All docs | [docs/README.md](docs/README.md) |

## Quick Start

```bash
./setup.sh && source .venv/bin/activate && pip install -e .
cp flb.local.toml.example flb.local.toml && cp .env.example .env
# edit configs; build Docker images — see RUN.md

export PYTHONPATH=$PWD/harness
featureliftbench setup
featureliftbench smoke --output experiments/openhands-agent/smoke-test
featureliftbench run --suite pilot5 --max-steps 120
```

## Repository Map

```text
benchmark/          tasks, sanity, vendor-wheels
harness/
  featureliftbench/   CLI, agent runner, evaluator, local_config, run_workflow
  scripts/            preflight, analysis
docker/               agent & eval images
flb.local.toml        local experiment config (gitignored)
experiments/          run outputs (gitignored)
```

## License

Upstream task repos keep their original licenses. Project-wide license metadata is not finalized here.
