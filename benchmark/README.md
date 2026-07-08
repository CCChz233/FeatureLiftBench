# FeatureLiftBench Task Layout

This directory holds all benchmark task packages, split workspaces, oracle artifacts, and shared source curation. **Do not add new tasks directly to `benchmark/tasks/`** without following the incremental lifecycle in [`docs/07_incremental_task_rules.md`](../docs/07_incremental_task_rules.md).

Machine-readable split definitions live in [`manifest.json`](manifest.json).

## Top-Level Layout

```text
benchmark/
  manifest.json          # split registry (roots, lifecycle, paper use)
  README.md              # this file
  tasks/                 # Python main candidate pool (current paper split)
  sanity/                # Python smoke tasks (not on main leaderboard)
  go/
    tasks/               # Go candidate / calibration tasks
    sanity/              # Go smoke tasks
  go_pilot/              # legacy Go pilot workspace
  sources/               # shared / curated upstream templates (not eval input)
  submissions/           # oracle / reference artifacts (not agent output)
  vendor-wheels/         # vendored wheels for offline eval
```

Local development workspaces such as `benchmark/staging/` and `benchmark/batch3_pilot/` are intentionally ignored in the public checkout. They may exist on a maintainer machine while designing or calibrating new tasks, but they are not part of the clone-and-run benchmark surface.

## Split Semantics

### `benchmark/tasks/` — Python main candidate pool

- Current **Python main split** used for paper-scale runs (100 tasks with `metadata.json` as of 2026-07-07 scan).
- Treat every directory here as **main lifecycle** by split membership, even when legacy tasks omit a `status` field in `metadata.json`.
- **New tasks must not be created here directly.** Promote from local staging or pilot workspaces only after all promotion gates pass.

### `benchmark/sanity/` — Python smoke (not main)

- Small smoke set for harness and agent wiring checks.
- **Never** included in main Pass@N leaderboard reporting.

### `benchmark/go/tasks/` — Go candidate / calibration

- Go language split tasks (calibration, seed placeholders, redesign candidates).
- **Not** paper-ready hard Go tasks today. See [`docs/go/02_go_task_inventory.md`](../docs/go/02_go_task_inventory.md).

### `benchmark/go/sanity/` and `benchmark/go_pilot/`

- Go smoke and legacy pilot workspaces. Not main-split tasks.

### `benchmark/sources/` — shared / curated upstream only

- Master copies for rebuilding or curating task repos (e.g. `vibe_app/`, `networkx_dag_curated/`).
- **Not** used as runtime evaluation input. Each task's formal upstream snapshot lives in that task's own `repo/`.

### `benchmark/submissions/` — oracle / reference artifacts

- Gold oracle trees, reference solutions used by harness scripts, and evaluation baselines.
- **Not** where agents write output. Agents deliver to a run workspace under `submission/` (see task schema).

## Per-Task Package (Python)

```text
benchmark/<split>/<task_id>/
  metadata.json
  requirements.lock
  TASK.md                    # recommended human spec
  repo/                      # sole formal upstream snapshot for this task
  public_tests/
  hidden_tests/
  evaluation/
  reference_solution/        # optional inline reference (pilots)
```

Go tasks use `environment/go.mod` instead of `requirements.lock`. See [`docs/06_task_schema.md`](../docs/06_task_schema.md).

## Agent Output (evaluation runtime)

Agents produce an installable package at:

```text
submission/
  featurelifted/             # Python canonical package name
```

Tests import `featurelifted`, not `submission`.

## Adding Tasks (summary)

| Action | Allowed location |
|---|---|
| New Python task (always start here) | local `benchmark/staging/` or `benchmark/batch3_pilot/` |
| Promote to main Python split | `tasks/` (copy/move only after gates) |
| Python smoke | `sanity/` |
| New Go task | `go/tasks/` (calibration) or design docs first |
| Oracle / gold reference | `submissions/` (harness-maintained) |
| Shared upstream template | `sources/` (curation only) |

Run the read-only lifecycle checker after changes:

```bash
python3 scripts/check_task_lifecycle.py
```

Reports are written to the ignored `reports/` directory.

## Related Docs

- [`docs/06_task_schema.md`](../docs/06_task_schema.md) — canonical task package fields
- [`docs/07_incremental_task_rules.md`](../docs/07_incremental_task_rules.md) — lifecycle and promotion gates
- [`docs/python/02_python_repo_task_inventory.md`](../docs/python/02_python_repo_task_inventory.md) — Python main inventory
