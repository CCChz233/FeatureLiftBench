# FeatureLiftBench

FeatureLiftBench evaluates whether coding agents can **extract one existing feature from an entangled repository** into a standalone, behavior-preserving Python package.

The benchmark is not a bug-fix benchmark. The agent sees a real repository snapshot, public tests, task metadata, and a target API. It must produce:

```text
submission/
  featurelifted/
    __init__.py
    ...
```

The evaluator checks behavior with public and hidden tests, rejects forbidden imports from the original package, and scores both correctness and extraction footprint.

## Current Status

- Main Python benchmark: `benchmark/tasks/` with 100 hard tasks.
- Smoke tasks: `benchmark/sanity/` with 3 quick tasks.
- Current experiment mainline: **OpenHands + Docker agent + Docker eval**.
- `mini-swe-agent` results are legacy baselines. Because append-only histories can exceed model context windows, they should not be used as the main long-context claim unless rerun with verified context handling.
- `featurelift-agent` is a protocol/control scaffold, not the current main evaluated agent.

## Start Here

| Goal | Read |
| --- | --- |
| Understand the benchmark | [docs/CONCEPTS.md](docs/CONCEPTS.md) |
| Reproduce the benchmark contract | [docs/BENCHMARK_SPEC.md](docs/BENCHMARK_SPEC.md) |
| Run current OpenHands experiments | [RUN.md](RUN.md) and [docs/OPENHANDS_SERVER_RUNBOOK.md](docs/OPENHANDS_SERVER_RUNBOOK.md) |
| Set up environment and Docker | [docs/SETUP.md](docs/SETUP.md) |
| Understand task format | [docs/TASK_FORMAT.md](docs/TASK_FORMAT.md) |
| See task catalog | [docs/benchmark_tasks.md](docs/benchmark_tasks.md) |
| See all docs | [docs/README.md](docs/README.md) |

## Minimal OpenHands Pilot

After configuring `.env` and building Docker images:

```bash
AGENT_PROFILE=openhands_deepseek_v4_flash \
NUM_WORKERS=1 \
FEATURELIFTBENCH_OPENHANDS_MAX_STEPS=120 \
./run_openhands_pilot5.sh
```

Expected output:

```text
experiments/openhands-agent/<RUN_ID>/
  sanity3/
  batch2/
  pilot5-summary.json
  pilot5-summary.md
```

A pilot is infrastructure-clean only if:

- `total == 5`
- `agent_failures == 0`
- `docker_sandbox_failures == 0`
- `log_limit_failures == 0`
- every task has `agent/usage.json`
- token/context evidence is verified or explicitly marked `usage_unverified=true`

## Repository Map

```text
benchmark/
  sanity/             # 3 quick smoke tasks
  tasks/              # main benchmark tasks
harness/
  featureliftbench/   # CLI, agent adapters, evaluator, suite logic
  scripts/            # preflight, analysis, migration, utility scripts
docker/               # agent/eval Docker images
docs/                 # canonical documentation
experiments/          # local run outputs; not a source of truth
```

## Core Commands

```bash
./setup.sh
cp .env.example .env

FEATURELIFTBENCH_AGENT_PYTHON_BASE=python:3.12-slim \
FEATURELIFTBENCH_INSTALL_OPENHANDS=1 \
./docker/build_agent_image.sh featureliftbench-agent:latest

./docker/build_eval_image.sh featureliftbench-eval:latest

PYTHONPATH=harness python -m unittest discover -s harness/tests
```

## License

Project license metadata is not finalized in this repository. Source repositories embedded in benchmark tasks keep their original upstream licenses.
