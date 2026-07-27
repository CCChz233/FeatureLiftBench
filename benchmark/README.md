# FeatureLiftBench Task Layout

This directory holds all benchmark task packages, split workspaces, oracle artifacts, and shared source curation. **Do not add new tasks directly to `benchmark/tasks/`** without following the incremental lifecycle in [`docs/07_incremental_task_rules.md`](../docs/07_incremental_task_rules.md).

Machine-readable split definitions live in [`manifest.json`](manifest.json).

The current Python-150 task packages are admitted to the frozen
**Full-Repository / No-Hint v3 Main**. Agent workspaces are generated from the
canonical source archives, not from the historical task-local slices. See
[`docs/BENCHMARK_DESIGN_PRINCIPLES.md`](../docs/BENCHMARK_DESIGN_PRINCIPLES.md)
and the current
[`reports/audits/v3_main_readiness.md`](../reports/audits/v3_main_readiness.md).

## Top-Level Layout

```text
benchmark/
  manifest.json          # split registry (roots, lifecycle, paper use)
  README.md              # this file
  tasks/                 # Python main candidate pool (current paper split)
  curated/
    tasks/               # Curated-7 extension, excluded from Main headline
    references/          # Curated reference implementations
    sources/             # Curated source trees
  sanity/                # Python smoke tasks (not on main leaderboard)
  go/
    tasks/               # Go candidate / calibration tasks
    sanity/              # Go smoke tasks
  go_pilot/              # legacy Go pilot workspace
  sources/               # External Main canonical source registry/archives
  pilots/                # migration/calibration subset manifests
  submissions/           # oracle / reference artifacts (not agent output)
  vendor-wheels/         # vendored wheels for offline eval
```

Local development workspaces such as `benchmark/staging/` and `benchmark/batch3_pilot/` are intentionally ignored in the public checkout. They may exist on a maintainer machine while designing or calibrating new tasks, but they are not part of the clone-and-run benchmark surface.

## Split Semantics

### `benchmark/tasks/` — Python v3 External Main

- Current Python External Main used for paper-scale runs: 150 frozen tasks.
- Membership requires the passing v3 benchmark freeze; future task changes
  invalidate that freeze and must rerun admission.
- Treat every directory here as **main lifecycle** by split membership, even when legacy tasks omit a `status` field in `metadata.json`.
- **New tasks must not be created here directly.** Promote from local staging or pilot workspaces only after all promotion gates pass.

### `benchmark/sanity/` — Python smoke (not main)

- Small smoke set for harness and agent wiring checks.
- **Never** included in main Pass@N leaderboard reporting.

### `benchmark/curated/tasks/` — Curated extension

- Seven `vibe_app` tasks retained for extension/appendix analysis.
- Disjoint from `benchmark/tasks/`, source registry and Main compactness
  registry; never included in the External-150 headline.

### `benchmark/go/tasks/` — Go candidate / calibration

- Go language split tasks (calibration, seed placeholders, redesign candidates).
- **Not** paper-ready hard Go tasks today. See [`docs/go/02_go_task_inventory.md`](../docs/go/02_go_task_inventory.md).

### `benchmark/go/sanity/` and `benchmark/go_pilot/`

- Go smoke and legacy pilot workspaces. Not main-split tasks.

### `benchmark/sources/` — External Main canonical sources

- Canonical repository/snapshot inventory:
  [`sources/registry.json`](sources/registry.json).
- Normative source policy:
  [`docs/FULL_REPOSITORY_SOURCE_POLICY.md`](../docs/FULL_REPOSITORY_SOURCE_POLICY.md).
- Curated source trees live under `benchmark/curated/sources/`.
- v3 task workspaces are materialized from verified registered archives; a
  legacy task-local `repo/` is not itself canonical source evidence.

### `benchmark/pilots/` — migration/calibration manifests

- The selected Full-Repository / No-Hint Pilot-16 is recorded in
  [`pilots/full_repository_v2.json`](pilots/full_repository_v2.json).
- Pilot-16 is retained as migration provenance. Its source materialization
  gates are now subsumed by the completed Python-150 migration.

### `benchmark/submissions/` — local reference compatibility artifacts

- Reference submissions used by maintainer validation. They are never mounted
  in a functional evaluator container.
- **Not** where agents write output. Agents deliver to a run workspace under `submission/` (see task schema).

## Per-Task Package (Python)

```text
benchmark/<split>/<task_id>/
  metadata.json
  requirements.lock
  TASK.md                    # recommended human spec
  repo/                      # historical task-local source/provenance
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

For v3 Main, promotion additionally requires a canonical source registry entry,
immutable source digest, complete tracked-tree audit, generated-workspace
No-Hint leak check, Oracle/isolation/determinism revalidation, and a new
benchmark freeze. A non-empty task-local `repo/` alone is insufficient.

## Related Docs

- [`docs/06_task_schema.md`](../docs/06_task_schema.md) — canonical task package fields
- [`docs/07_incremental_task_rules.md`](../docs/07_incremental_task_rules.md) — lifecycle and promotion gates
- [`docs/FULL_REPOSITORY_SOURCE_POLICY.md`](../docs/FULL_REPOSITORY_SOURCE_POLICY.md) — canonical source inclusion/digest rules
- [`reports/audits/v3_main_readiness.md`](../reports/audits/v3_main_readiness.md) — current v3 release gate
- [`docs/python/02_python_repo_task_inventory.md`](../docs/python/02_python_repo_task_inventory.md) — Python main inventory
