# FeatureLiftBench Benchmark Specification

**Spec version:** 1.0 (implemented)  
**Last updated:** 2026-06-27

This document is the **reproducibility contract** for FeatureLiftBench: what the benchmark measures, how a task is packaged, and how third parties run **setup → agent → evaluate**.

| Audience | Start here |
| --- | --- |
| First-time readers | [CONCEPTS.md](CONCEPTS.md) |
| Per-task file layout | [TASK_FORMAT.md](TASK_FORMAT.md) |
| Adding or replacing tasks | [EXPANSION.md](EXPANSION.md) |
| Deploy & run | [SETUP.md](SETUP.md) · [RUN.md](../RUN.md) |
| Runtime memory limits | [SETUP.md](SETUP.md) §4 |

---

## 1. What this benchmark is (and is not)

### 1.1 Mission

FeatureLiftBench evaluates **behavior-preserving feature-level decoupling**:

> Given a **pinned snapshot** of a real (or scenario-curated) repository where a feature already exists but is **entangled** with framework, config, global state, resources, or unrelated modules, can a coding agent extract that feature into a **standalone, installable, testable package** with **compatible behavior**?

The agent delivers a **new package** (`submission/featurelifted/`), not a git patch on the original repository.

### 1.2 Explicit non-goals

This benchmark does **not** evaluate:

| Not this | Typical benchmark | FeatureLiftBench |
| --- | --- | --- |
| Issue resolution | SWE-bench, GitHub issue → patch | **Feature specification** → decoupled package |
| Bug localization | Line-level fault finding | **Closure planning** across modules/resources |
| Greenfield implementation | Write feature from scratch | **Extract** existing behavior from entangled code |
| Code review / preference | Human judgment | **Automated** pytest + import gates |

Do **not** describe tasks as “fixing bugs” or “resolving issues.” Use **feature specification**, **reference submission (oracle)**, and **decoupling closure**.

### 1.3 Track

**Decoupling / Extraction Track** (the only track in v1):

- Copy, trim, and rewrite imports from `repo/` into `featurelifted/`.
- Small glue code and packaging (`pyproject.toml`) allowed.
- **Forbidden:** depending on the original upstream package or repo path at runtime.
- **Not required:** byte-identical match to oracle; **required:** public + hidden tests pass.

---

## 2. Spec versions and scale

| Version | Status | Languages | Main leaderboard size | Notes |
| --- | --- | --- | --- | --- |
| **v1.0** | **Implemented** | Python | **50 hard** (batch-0) + 3 smoke | Frozen batch-0; see [EXPANSION.md](EXPANSION.md) |
| **v1.1** | **Implemented** | Python | **100 hard** (batch-0 + batch-1) | +50 via `benchmark/staging/`; [EXPANSION.md](EXPANSION.md) §2 |
| **v2.0** | Planned | Python + Go | Target **100 + 100** (same task type) | After Python 100; Go harness TBD |

**v1.0 policy:** **batch-0** fifty tasks in `benchmark/tasks/` are **frozen** (no edits for expansion). **batch-1** adds fifty new tasks via staging ([EXPANSION.md](EXPANSION.md)).

**v2 policy (draft):** Scale and multilingual support are **benchmark-spec extensions**, not a change to decoupling semantics. Go tasks will still require a standalone extracted module and automated tests—not repository patches.

When citing results, always report: **spec version**, **harness git commit**, **leaderboard size**, and **language partition**.

---

## 3. Formal task contract

Each task is a self-contained directory. The table below maps **paper-style field names** to this repository (v1 Python).

| Spec field | v1 implementation | Description |
| --- | --- | --- |
| `task_id` | Directory name | e.g. `sqlparse__parse_format_core__001` |
| `language` | `metadata.language` | `"python"` only in v1 |
| `repository` | `metadata.source` + `repo/` | Pinned upstream snapshot |
| `commit hash` | `metadata.source.commit` | Immutable task input |
| `feature specification` | `metadata.feature` + generated `TASK.md` | **Not** a GitHub issue; defines behavior boundary |
| `reference submission` | `benchmark/submissions/<task_id>/oracle/` | Maintainer-curated decoupling answer (gitignored) |
| `base environment` | `metadata.environment` | Python version, timeout, network=false, dependency lock |
| `setup` | `./setup.sh` + evaluator venv bootstrap | Project-level; per-task deps via `requirements.lock` |
| `test command` | `pytest` on `public_tests/` and `hidden_tests/` | Invoked by harness evaluator |
| `evaluator` | `featureliftbench eval` | See §5 |
| `difficulty` | `metadata.difficulty` | `easy` \| `medium` \| `hard` |
| `metadata` | Full `metadata.json` | Includes `entanglement`, `output`, `tests`, `tags` |

### 3.1 Required on-disk layout (v1)

```text
benchmark/tasks/<task_id>/
  metadata.json
  requirements.lock
  repo/
  public_tests/
  hidden_tests/
  evaluation/
    forbidden_imports.txt
    oracle_manifest.json
```

Machine-readable schema: [`harness/featureliftbench/schemas/task_metadata.schema.json`](../harness/featureliftbench/schemas/task_metadata.schema.json).

Validate:

```bash
export PYTHONPATH=harness
python -B -m featureliftbench.cli validate-task benchmark/tasks/<task_id>/
```

### 3.2 Agent input (workspace)

`run-agent` materializes a **redacted** workspace (no hidden tests, no scoring secrets):

```text
workspace/
  repo/
  public_tests/
  requirements.lock
  metadata.json      # redacted
  TASK.md            # generated from metadata
  submission/        # agent writes here
```

### 3.3 Agent output (submission)

```text
submission/
  pyproject.toml           # recommended
  featurelifted/           # unified output package name (v1)
    ...
```

Rules: installable in isolation; no forbidden imports; must pass evaluation tests.

### 3.4 Reference submission (oracle)

Not shipped in git. Built locally:

```bash
python3 harness/scripts/build_oracle_submission.py benchmark/tasks/<task_id>/
python3 harness/scripts/verify_all_oracles.py --task-id <task_id>
```

Oracle proves **solvability** and supports regression; it is not shown to agents.

---

## 4. End-to-end reproduction protocol

Anyone reproducing a published number should follow:

```text
1. SETUP      → ./setup.sh ; configure .env / agents.toml
2. PREFLIGHT  → harness/scripts/preflight.py (optional --bootstrap)
3. RUN AGENT  → featureliftbench.cli run-agent … → experiments/<run_id>/
4. EVALUATE   → automatic per task (eval/result.json) + suite.json
5. ANALYZE    → analyze_benchmark_suite.py ; report_entanglement_coverage.py
```

### 4.1 Setup

See [SETUP.md](SETUP.md). Minimum:

- Python **3.11+** (3.12 recommended)
- `./setup.sh` → `.venv`, `mini-swe-agent`, `agents.toml` template
- API or vLLM credentials in `.env`

### 4.2 Run agent (suite)

```bash
export PYTHONPATH=harness
export NUM_WORKERS=1
export FEATURELIFTBENCH_AGENT_DOCKER=1
export FEATURELIFTBENCH_EVAL_DOCKER=1

./run.sh
# or equivalent featureliftbench.cli run-agent benchmark/tasks …
```

### 4.3 Evaluate

Evaluation runs **automatically** after each task unless invoked alone:

```bash
python -B -m featureliftbench.cli eval benchmark/tasks/<task_id>/ /path/to/submission
```

Per-task artifacts:

```text
experiments/<run_id>/<task_id>/
  run.json
  agent/trajectory.json
  submission/
  eval/result.json
  eval/logs/
```

Suite summary: `experiments/<run_id>/suite.json`.

### 4.4 Runtime safety (part of spec)

Untrusted submission code is executed under pytest. Published runs should use Docker eval (`FEATURELIFTBENCH_EVAL_DOCKER=1`) so memory, CPU, process count, logs, network, and writable mounts are bounded. Long/shared agent runs should also use agent Docker (`FEATURELIFTBENCH_AGENT_DOCKER=1`). Local `EVAL_MEMORY_MB` / `AGENT_MEMORY_MB` are debug fallbacks, not the official paper baseline.

---

## 5. Evaluator and scoring

Implementation: [`harness/featureliftbench/evaluator.py`](../harness/featureliftbench/evaluator.py), [`scoring.py`](../harness/featureliftbench/scoring.py).

### 5.1 Functional gate

```text
FunctionalGate = BuildPass ∧ TestPass ∧ OriginalImportPass
```

| Gate | Meaning |
| --- | --- |
| BuildPass | `featurelifted` installs/imports in clean eval venv |
| TestPass | All **public** and **hidden** pytest tests pass |
| OriginalImportPass | No forbidden imports / forbidden dependencies |

`FunctionalGate` is **binary** (0 or 1). It does **not** measure decoupling quality.

### 5.2 Extraction ratio

```text
ExtractionRatio = submission Python LOC / repo Python LOC
```

Lower is better. Copying the entire repository can yield `FunctionalGate = 1` with `ExtractionRatio ≈ 1`.

### 5.3 Final score

```text
final_score = FunctionalGate × max(0, 1 - ExtractionRatio)
```

If `FunctionalGate = 0`, then `final_score = 0`.

### 5.4 Task success (paper primary metric)

**Task Success** in FeatureLiftBench means:

```text
status = passed  ⟺  agent finished normally  ∧  eval FunctionalGate = 1
```

Report **Task Success Rate** as `summary.passed / summary.total` from `suite.json`.

**Always report alongside** (secondary but essential for this benchmark):

| Metric | Source | Why |
| --- | --- | --- |
| Avg `final_score` | `suite.json` `summary.average_final_score` | Rewards compact decoupling |
| High-extraction pass count | `analyze_benchmark_suite.py` | `extraction_ratio ≥ 0.8` but functional pass |
| Compact pass count | same | `extraction_ratio ≤ 0.25` and functional pass |
| Token / cost totals | `agent_usage_totals` | Efficiency; not part of pass |

**Do not** reduce the benchmark to test-pass rate alone—that collapses FeatureLiftBench into a generic SWE-style metric and ignores decoupling.

---

## 6. Curation and quality bar

Task **semantics** are fixed (decoupling). Task **selection** follows [EXPANSION.md](EXPANSION.md).

Summary:

- Every task needs a **practical reuse story** (what real module `featurelifted` represents).
- Difficulty should come from **legitimate entanglement**, not artificial clutter.
- v1 leaderboard: **43** pinned OSS slices + **7** curated `vibe_app` scenario tasks—report separately when claiming “real library” results.
- New or replacement tasks: oracle verified, module probes, `validate-task`, design note with **Practical reuse** section.

### 6.1 Inclusion (v1)

- Public open-source snapshot **or** documented scenario repo (`vibe_app`).
- Behavior verifiable by **automated pytest** (public + hidden).
- Reference submission constructible with bounded oracle closure.
- Forbidden-import gate enforceable.

### 6.2 Exclusion

- Requires live network, external DB, or human judgment at eval time.
- Cannot pin reproducible environment.
- “Solution” is a monorepo patch with no standalone package interpretation.
- No credible reuse narrative for the extracted module.

---

## 7. Dataset statistics (reporting template)

For papers, report at least:

### 7.1 Coverage (v1 snapshot)

| Metric | v1 value |
| --- | ---: |
| Main hard tasks | 50 |
| Smoke tasks | 3 |
| Source libraries | 26 |
| pytest test functions (hard) | 242 (94 public + 148 hidden) |
| OSS lineage tasks | 43 |
| Scenario (`vibe_app`) tasks | 7 |

### 7.2 Per-task descriptors (compute from tasks + oracle)

| Descriptor | Use |
| --- | --- |
| `repo` Python LOC | Extraction denominator |
| Oracle `ExtractionRatio` | Difficulty / closure size prior |
| `entanglement.primary` | Stratified results |
| Hidden / public test counts | Test hardness proxy |
| Module probe count | Closure necessity evidence |

Scripts: `analyze_benchmark_suite.py`, `report_entanglement_coverage.py`, `list_tasks.py`.

### 7.3 Difficulty labels

`metadata.difficulty` is the primary axis (`hard` for main leaderboard). Optional future: letter tiers (S/A/B/C) derived from oracle extraction, cross-module count, and agent calibration—**not** a separate benchmark.

---

## 8. Baseline experiment protocol

Minimum for a credible model row:

| Requirement | Detail |
| --- | --- |
| Agent harness | `mini-swe-agent` + documented profile (`agents.toml`) |
| Task set | Full main leaderboard unless ablation stated |
| Workers | `NUM_WORKERS=1` for official numbers |
| Resource boundary | `FEATURELIFTBENCH_EVAL_DOCKER=1`; agent Docker recommended for long/shared runs ([SETUP.md](SETUP.md) §4) |
| Repeats | Single run minimum; multi-seed runs report mean ± std and pass@k |
| Harness version | Git commit hash in paper appendix |

**Model tiers to report:**

- Strong API agents (e.g. DeepSeek Flash/Pro — see [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md))
- Open-weight / vLLM agents (same protocol; note endpoint)
- Optional ablations (no agent, oracle-only sanity)

Compare models only when **missing_submission** rate is low; high missing rates measure infrastructure, not capability.

---

## 9. Failure analysis (paper contribution)

Classify failures at the **decoupling** layer—not SWE-bench localization buckets.

| Category | Operational signal | Interpretation |
| --- | --- | --- |
| **No submission** | `missing_submission` | Agent/API infra; not a task fail |
| **Build / import fail** | `build_pass = false` | Packaging or wrong module layout |
| **Forbidden dependency** | `original_import_pass = false` | Still coupled to upstream package |
| **Public test fail** | public pytest fail | Wrong API or core logic |
| **Public-only fail** | public pass, hidden fail | Under-scoped closure; weak decoupling |
| **Copy-heavy pass** | functional pass, `extraction_ratio ≥ 0.8` | Functional but not decoupled |
| **Compact pass** | functional pass, `extraction_ratio ≤ 0.25` | Strong decoupling |
| **Resource limited** | `resource_limited` in eval | Memory cap / OOM ([SETUP.md](SETUP.md) §4) |

Aggregate with `summarize_experiment_runs.py` / per-run `*-comparison.json` ([EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md)).

---

## 10. Suggested paper positioning

Prefer **narrow and defensible**:

✅ *A repository-level benchmark for behavior-preserving feature decoupling and reusable module extraction.*

✅ *Evaluating whether coding agents can extract entangled features into standalone packages—not merely patch existing repos.*

Avoid:

❌ *A comprehensive benchmark for software engineering agents.*

❌ *Multilingual bug-fix benchmark* (unless v2 Go track ships with the same decoupling semantics and clear labeling).

---

## 11. v2 roadmap (spec only; not implemented)

Planned extensions **without changing task semantics**:

| Item | Plan |
| --- | --- |
| Languages | Python 100 + Go 100 decoupling tasks |
| `language` field | `go` tasks with `go test`, Go module layout, Go forbidden-import rules |
| Unified spec doc | This file remains canonical; TASK_FORMAT gains per-language annex |
| Harness | Go evaluator parallel to Python venv path |
| Curation | Same [EXPANSION.md](EXPANSION.md) reuse principles; Go OSS libraries |

v2 development should **freeze Python v1 baselines** before retroactive relabeling of published numbers.

---

## 12. Document map

| Question | Document |
| --- | --- |
| What are we measuring? | [CONCEPTS.md](CONCEPTS.md) §1 |
| Exact file formats? | [TASK_FORMAT.md](TASK_FORMAT.md) |
| How to pick tasks? | [EXPANSION.md](EXPANSION.md) |
| Current baselines & gaps? | [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) |
| Experiment results? | [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md) |
| Architecture? | [ARCHITECTURE.md](ARCHITECTURE.md) |

**Change control:** Any change to scoring, pass definition, or required task layout increments **spec minor version** and should be noted in [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md) and experiment reproduction notes.
