# FeatureLiftBench scripts

> **Status: current · Last verified: 2026-08-29**

The stable experiment entrypoint is `./scripts/run_benchmark.sh`, which resolves
the benchmark × agent × method catalogs and delegates to `run_experiment.sh`.
The installed `featureliftbench` CLI is the other supported entrypoint.
Paper Main is `--benchmark python200_hard`. Do not use
`./harness/scripts/run_python200_paper.sh` for that suite.

Prefer `python3.12` for catalog, docs check, and `reorganize_experiments.py`
(the default `python3` on some Macs is 3.9).

## Script ownership

| Location | Role |
| --- | --- |
| `scripts/run_benchmark.sh` | Stable benchmark × agent × method entrypoint |
| `scripts/run_experiment.sh` | Shared experiment implementation and compatibility options |
| `scripts/check_*.py`, `scripts/audit_*.py` | Repository and release audits |
| `scripts/build_*.py`, `scripts/materialize_*.py` | Maintainer-only task/release generation |
| `harness/scripts/` | Evaluator, Agent runtime, suite execution, and analysis helpers |
| `tools/research_analysis/` | Research-only taxonomy and derived-analysis tooling |

One-off scripts must not be added at the repository root. A new script should
state its input authority, output location, overwrite policy, and validation
command before it becomes a current maintenance entrypoint.

## Root compatibility layer

Only `run_benchmark.sh` and `run_experiment.sh` are supported thin root
forwarders. The following historical scripts entered a deprecation cycle on
2026-08-29 and now print a warning when invoked:

- `run.sh`
- `run-batch1-docker-flash.sh`
- `run_easy.sh`
- `run_featurelift.sh`
- `run_openhands.sh`
- `run_openhands_pilot5.sh`
- `run_smoke.sh`
- `start_run.sh`
- `resume_run.sh`
- `check_env.sh`

They are retained for migration compatibility only. At the next repository
maintenance review, remove a wrapper only after current documentation and code
contain no references to it and its replacement has been recorded in the
maintenance log. Historical documents may retain the old command as evidence.
