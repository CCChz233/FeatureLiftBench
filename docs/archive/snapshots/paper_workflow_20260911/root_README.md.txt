# FeatureLiftBench

> **Documentation status: current · Last verified: 2026-09-02**

FeatureLiftBench evaluates whether a coding agent can extract and reconstruct a
coherent feature from a real upstream repository under a controlled information
boundary. The official Main arm provides the full upstream repository, hides
benchmark tests and source hints, and evaluates the submitted `featurelifted`
package in an isolated Docker capsule.

Current release status, freeze identifiers, task counts, and available results
are maintained only in [docs/STATUS.md](docs/STATUS.md).

## Start Here

| Goal | Entry |
| --- | --- |
| Understand the benchmark | [Design](docs/BENCHMARK_DESIGN.md) |
| Check readiness and current results | [Status](docs/STATUS.md) |
| Current V1 method (Main + 2M cap) | [V1](docs/METHOD_V1.md) |
| Optional DeepSeek Harness / Codex runtime | [Agent runtime](docs/METHOD_AGENT_RUNTIME.md) |
| Run an experiment | [Run quick reference](RUN.md) · **only** `./scripts/run_benchmark.sh` |
| Operate a server run | [Python-200 runbook](docs/SERVER_RUNBOOK_PYTHON200.md) |
| Reorganize or clean the repository | [Repository maintenance](docs/REPOSITORY_MAINTENANCE.md) |
| Create or review a task | [Task design rules](docs/TASK_DESIGN_RULES.md) |
| Navigate all documentation | [Documentation portal](docs/README.md) |

## Five-Minute Preflight

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./harness

PYTHONPATH=harness python -B -m featureliftbench.cli catalog check
```

`catalog check` validates `benchmark/suites.toml`, `agent/registry.toml`, and
`method/registry.toml` against adapters and OpenHands profiles. Paper Main
execution is `./scripts/run_benchmark.sh --benchmark python200_hard --agent
openhands --method main`. `./harness/scripts/archive/run_python200_paper.sh` still
validates the superseded 150+External-50 release; do not use it for Python-200'.

## Repository Layout

Experiments are **benchmark × agent × method**. List ids with
`PYTHONPATH=harness python -B -m featureliftbench.cli catalog list`.

| Path | Role |
| --- | --- |
| [`benchmark/`](benchmark/README.md) | Task packages and named suites. Paper root is `python200_hard_tasks/` (150 + Hard-50), not `python200_tasks/` |
| `agent/` | Public catalog of coding runtimes (`--agent`). Adapters stay in `harness/` |
| `method/` | Public catalog of protocols / information arms (`--method` / `--arm`) |
| [`scripts/`](scripts/README.md) | Maintainer entrypoints. Root only has thin forwarders `run_benchmark.sh` / `run_experiment.sh` plus `setup.sh` |
| [`harness/`](harness/README.md) | Evaluator, Docker capsule, agent adapters, and CLI. Not a third experiment axis |
| `docs/` | Current specifications, runbooks, paper material, and archived narratives |
| `reports/` | Audits and derived analysis; not a substitute for raw task results |
| [`experiments/`](experiments/README.md) | Raw runs in seven canonical directories only |
| `artifacts/` | Small freezes, selection, taxonomy snapshots — not full checkouts |
| `evidence/` | Historical task-construction gates only |
| `integrations/` | External method adapters (e.g. AutoSaddler) that do not fork the harness |
| `archive/` | Local historical payload; not a run entrypoint |

```bash
./scripts/run_benchmark.sh \
  --benchmark python200_hard \
  --agent openhands \
  --method main \
  --docker --workers 1 --timeout 3600
```

`--arm` is an alias of `--method`. Official paper numbers use OpenHands + `main`.
DeepSeek Harness and Codex share this CLI but stay off the OpenHands table.
Do not start experiments with deleted root wrappers (`run.sh`, `run_openhands.sh`, `run_easy.sh`).

Task packages and source archives are **not** stored on GitHub. For a server
run, copy `experiments/bundles/outgoing/FeatureLiftBench-benchmark-20260828.tar.gz`
(about 690 MB) and unpack it at the repository root so `benchmark/` is restored.
Verify with
[`experiments/bundles/outgoing/current/FeatureLiftBench-benchmark-20260828.tar.gz.sha256`](experiments/bundles/outgoing/current/FeatureLiftBench-benchmark-20260828.tar.gz.sha256).
Do not commit `.env` or `harness/config/agents.toml`.

## Result Boundary

The primary metrics are evaluator `Functional Pass@1` and pass-conditioned
Reference-Relative Extraction Size (RRES). Agent completion status is not a
correctness score. Official Main uses OpenHands. DeepSeek Harness and Codex are
the same CLI level after `./setup.sh`, but remain a runtime ablation and must
not be merged into the OpenHands Python-200 table. Results are comparable only
when the task set, attempt policy, model revision, agent runtime, agent
profile, information arm, and agent/evaluator image identities match.
Historical and current conditions must not be silently combined.

## Citation and License

Citation metadata and licensing will be finalized with the paper release.
Upstream source snapshots retain their original licenses; see task metadata and
the source registries for provenance.
