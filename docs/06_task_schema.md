# Task Schema

FeatureLiftBench tasks use the filesystem schema implemented by the current evaluator, not a `task.yaml` schema.

Canonical lifecycle and promotion rules: [`07_incremental_task_rules.md`](07_incremental_task_rules.md).
Split registry: [`../benchmark/manifest.json`](../benchmark/manifest.json).

## Canonical Python Task Package

```text
benchmark/<split>/<task_id>/
  metadata.json
  requirements.lock
  TASK.md                      # human-readable feature spec (recommended)
  repo/                        # sole formal upstream snapshot for this task
  public_tests/
  hidden_tests/
  evaluation/
  reference_solution/          # optional inline oracle notes / pilot reference
```

Batch-3 pilots currently live under `benchmark/batch3_pilot/<task_id>/` and may also include `evaluator_config.yaml` and `reference_solution/featurelifted/` during materialization.

### Required paths (Python)

| Path | Role |
|---|---|
| `metadata.json` | Machine-readable task metadata, source, feature, output, difficulty/status, forbidden imports, test paths. |
| `requirements.lock` | Task runtime dependencies. Empty or comment-only files are valid for stdlib-only tasks. |
| `repo/` | **The only formal upstream snapshot** for evaluation and test authoring. Pinned commit content lives here. |
| `public_tests/` | Visible pytest tests. Import **`featurelifted`**, not `submission`. |
| `hidden_tests/` | Hidden pytest tests for behavior preservation. Same import rules as public tests. |
| `evaluation/` | Evaluator support: `forbidden_imports.txt`, `oracle_manifest.json`, and related probes. |

### Optional paths (Python)

| Path | Role |
|---|---|
| `TASK.md` | Human spec: included/excluded behavior, target API, calibration notes. |
| `reference_solution/` | Inline reference implementation for pilots; production oracle may also live under `benchmark/submissions/<task_id>/`. |
| `evaluator_config.yaml` | Pilot-local evaluator overrides (batch-3). |

Neither `TASK.md` nor `reference_solution/` is strictly required by every legacy main task, but **new tasks must include `TASK.md`** per the Task Package Gate.

## Canonical Go Task Package

```text
benchmark/go/<split>/<task_id>/
  metadata.json
  TASK.md
  repo/
  environment/go.mod
  public_tests/
  hidden_tests/
  evaluation/
```

Go tasks use `environment/go.mod` instead of `requirements.lock`. Output module is typically `featurelifted` under agent `submission/`.

## Upstream Snapshots vs Shared Sources

| Location | Purpose |
|---|---|
| `<task_id>/repo/` | **Formal eval input.** Every task must carry its own snapshot. |
| `benchmark/sources/` | Shared or curated master copies (e.g. `vibe_app/`, `networkx_dag_curated/`). Used when **building** tasks, **not** as runtime eval input. |
| Live git clone | Materialization workflow only; content must be copied into `repo/` before promotion. |

## Agent Submission vs Oracle Submissions

| Path | Owner | Purpose |
|---|---|---|
| `submission/` (per run workspace) | Agent | Deliverable tree created during a benchmark run. |
| `submission/featurelifted/` | Agent (Python) | Canonical extracted package name. |
| `benchmark/submissions/<task_id>/` | Maintainers / harness | Oracle, gold reference, and baseline artifacts for evaluation. **Not** agent output. |

## Example `metadata.json` (Python pilot style)

```json
{
  "task_id": "jupyter_core__paths_resolver_core__hard3_001",
  "language": "python",
  "difficulty": "hard",
  "difficulty_initial": "hard",
  "status": "materialized_candidate",
  "repo": "https://github.com/jupyter/jupyter_core",
  "commit": "ad6b4aea233a9634ffcd6ad553ecd63129ab5f6e",
  "license": "BSD-3-Clause",
  "feature_name": "Jupyter config/data/runtime path resolution",
  "feature_type": "path/resource resolver",
  "target_api": [
    "jupyter_config_dir(env=None, home=None, platform='linux') -> str",
    "jupyter_path(*subdirs, env=None, home=None, platform='linux') -> list[str]"
  ],
  "source_hints": [
    "repo/jupyter_core/paths.py"
  ],
  "forbidden_imports": [
    "jupyter_core"
  ],
  "forbidden_paths": [
    "repo/",
    "jupyter_core/paths.py"
  ],
  "hard_reason": "The target requires preserving path precedence across environment variables, platform defaults, user paths, and runtime fallbacks.",
  "expected_hidden_behaviors": [
    "explicit JUPYTER_* paths take precedence",
    "JUPYTER_NO_CONFIG suppresses normal config search",
    "Windows path separator behavior is preserved"
  ],
  "environment": {
    "python": "3.11",
    "network": false,
    "timeout_seconds": 90,
    "dependency_lock": "requirements.lock",
    "allowed_dependencies": [],
    "forbidden_dependencies": [
      "jupyter_core"
    ],
    "forbidden_imports": [
      "jupyter_core"
    ],
    "forbidden_paths": [
      "repo/",
      "jupyter_core/paths.py"
    ]
  },
  "tests": {
    "public": "public_tests/",
    "hidden": "hidden_tests/",
    "command": "pytest"
  },
  "output": {
    "package": "featurelifted",
    "import": "import featurelifted",
    "callable": "jupyter_config_dir",
    "signature": "jupyter_config_dir(env=None, home=None, platform='linux') -> str"
  }
}
```

## Example `metadata.json` (Python main style)

Main tasks often nest `source`, `feature`, and `output`:

```json
{
  "task_id": "jinja2__compile_render_core__001",
  "source": {
    "name": "jinja2",
    "url": "https://github.com/pallets/jinja",
    "commit": "15206881c006c79667fe5154fe80c01c65410679",
    "license": "BSD-3-Clause"
  },
  "language": "python",
  "difficulty": "hard",
  "feature": {
    "name": "Jinja2 compile and render core",
    "description": "Extract Jinja2 template compilation and rendering as a standalone package."
  },
  "output": {
    "package": "featurelifted",
    "import": "from featurelifted import Environment",
    "callable": "featurelifted.Environment.from_string"
  },
  "environment": { "...": "..." },
  "tests": {
    "public": "public_tests/",
    "hidden": "hidden_tests/",
    "command": "pytest"
  }
}
```

Legacy main tasks may omit `status`; split membership in `benchmark/tasks/` implies `main`.

## Status Values

See [`07_incremental_task_rules.md`](07_incremental_task_rules.md) for the full lifecycle enum. Common values in repo today:

| Status | Meaning |
|---|---|
| `design_only` | Planning pack; not a runnable benchmark task. |
| `needs_review` | Runnable package awaiting human review. |
| `materialized_candidate` | Snapshot, tests, and evaluator metadata present; calibration may be TODO. |
| `validated_candidate` | Structural gates passed; awaiting difficulty acceptance. |
| `hard_candidate` | Hard calibration recorded; ready for main promotion review. |
| `blocked` | Cannot complete without fabrication. Requires `blocked_reason`. |
| `main` | Member of main paper split. |
| `sanity` | Smoke task only. |
| `archived` | Retired. |

Do not report `materialized_candidate` tasks as validated benchmark tasks until oracle, public/hidden tests, forbidden import/path checks, copy-all, and model calibration have run and been recorded.

## Test Import Convention (Python)

```python
# correct
from featurelifted import SomeApi

# incorrect for new tasks
from submission.featurelifted import SomeApi
import jinja2  # upstream forbidden at runtime
```

Hidden tests must not introduce behaviors that are absent from the task spec (`TASK.md`, `feature.included_behaviors`, or documented `expected_hidden_behaviors`).
