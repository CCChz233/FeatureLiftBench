# FeatureLiftBench

> **Documentation status: current · Last verified: 2026-08-04**

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
| Run an experiment | [Run quick reference](RUN.md) |
| Operate a server run | [Python-200 runbook](docs/SERVER_RUNBOOK_PYTHON200.md) |
| Create or review a task | [Task design rules](docs/TASK_DESIGN_RULES.md) |
| Navigate all documentation | [Documentation portal](docs/README.md) |

## Five-Minute Preflight

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./harness

./harness/scripts/run_python200_paper.sh \
  <openhands-profile> \
  preflight-plan
```

Without `--execute`, the runner validates the release, source registry,
dependency closure, wheel coverage, task packages, and experiment plan without
making model calls.

## Repository Layout

| Path | Role |
| --- | --- |
| `benchmark/` | Frozen task packages, source registries, references, and release selections |
| `harness/` | Validation, agent execution, Docker evaluation, and analysis code |
| `docs/` | Current specifications, runbooks, paper material, and archived narratives |
| `reports/` | Audits and derived analysis; not a substitute for raw task results |
| `experiments/` | Local run outputs and transfer bundles; large artifacts are normally ignored by Git |
| `artifacts/` | Machine-readable freezes and research-analysis state |

## Result Boundary

The primary metric is evaluator `Functional Pass@1`, not agent completion
status. Results are comparable only when the task set, attempt policy, model
revision, agent profile, information arm, and agent/evaluator image identities
match. Historical and current conditions must not be silently combined.

## Citation and License

Citation metadata and licensing will be finalized with the paper release.
Upstream source snapshots retain their original licenses; see task metadata and
the source registries for provenance.
