# FeatureLiftBench

> **Status: current · Last verified: 2026-09-14**

FeatureLiftBench evaluates behavior-preserving feature lifting: given an intact,
version-pinned source repository and a public behavioral contract, a coding agent
builds an independent package, evaluated without runtime access to the source repository.

The current FSE manuscript reports **150 Python tasks, 126 repositories, 132 snapshots**,
with **six configurations × 150 tasks = 900 retained outcomes**. A separate paired
source ablation contains 240 outcomes on 40 tasks. The historical 200-task storage
view remains on disk; the extra 50 tasks are outside the paper.

## Start here

| Work | Entry |
| --- | --- |
| Understand the entire project and its evidence | [Project map](docs/PROJECT_MAP.md) |
| Read current results and remaining gaps | [Status](docs/STATUS.md) |
| Write, check, and package the updated paper | [Paper workflow](docs/paper/WORKFLOW.md) |
| Edit one figure | [Per-figure source index](docs/paper/figures/scripts/README.md) |
| Find the data behind a table or figure | [Paper source manifest](docs/paper/paper_sources.json) |
| Understand the benchmark and evaluator | [Design](docs/BENCHMARK_DESIGN.md) · [Evaluation](docs/EVALUATION.md) |
| Prepare an experiment | [Run guide](RUN.md) |
| Browse current and historical documentation | [Documentation portal](docs/README.md) |

```bash
python -B scripts/paper.py check
python -B scripts/paper.py tables
python -B scripts/paper.py package
```

`check` verifies saved numerical evidence, table contents, local figure assets and
cross-references. It reports raw-run coverage separately: **307/900 main-task profiles
are locally available**. `python -B scripts/paper.py audit` additionally requires all
900 original profiles and currently fails on the missing 593. Neither command launches
an agent. A successful numeric check does not establish complete raw-evidence recovery.

## Repository layout

| Directory | Role |
| --- | --- |
| `docs/paper/` | Active manuscript, bibliography, figures, table templates and paper tools |
| `benchmark/` | Frozen tasks and source identities; paper membership is selected explicitly |
| `harness/` | Evaluation gates, Docker capsule, adapters and CLI |
| `agent/`, `method/` | Runtime and protocol catalogs; historical methods are separate from paper Main |
| `reports/` | Derived results, source ablation and trace diagnostics |
| `experiments/` | Recovered raw runs and recovery records |
| `artifacts/` | Task selection, freeze identities and taxonomy records |
| `scripts/`, `tools/` | Maintainer entrypoints and analysis utilities |
| `docker/`, `integrations/`, `third_party/` | Execution environment and optional integrations |
| `docs/archive/`, `archive/` | Historical documents and payloads |
| `exports/` | Transfer/release bundles |

Current writing is based on the supplied `FSE.zip`; its immutable copy and the previous
local state are recorded in [the import snapshot](docs/archive/snapshots/fse_sync_20260914/README.md).
Task packages, model outputs and experiment identities were not rewritten during this sync.
Do not commit `.env`, local credentials or complete upstream checkouts.
