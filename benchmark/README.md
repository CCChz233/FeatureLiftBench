# FeatureLiftBench Task Layout

> **Documentation status: current · Last verified: 2026-09-03**

This directory holds task packages, named suites, source registries, and freeze
inputs. **Runnable suite names live in [`suites.toml`](suites.toml).** Do not
add tasks directly to `benchmark/tasks/` or `benchmark/hard50/` without the
lifecycle in [`docs/reference/07_incremental_task_rules.md`](../docs/reference/07_incremental_task_rules.md).

Paper identity and freeze hashes are maintained only in
[`docs/STATUS.md`](../docs/STATUS.md). The paper main suite is **Python-200'**
(frozen Python-150 + Hard-50), not 150 + External-50.

## Which root to use

| `--benchmark` | Task root | Role |
| --- | --- | --- |
| `python200_hard` | `python200_hard_tasks/` | **Paper freeze asset.** 200 symlinks: 150 → `tasks/`, 50 → `hard50/`. Unreleased. |
| `python200_hard_standard` | same root, 200 ids | **freeze v2 labels 200/0.** Predecessor 168/32 archived. Not an Agent leaderboard. |
| `python150` | `tasks/` | Frozen Python-150 packages. Paper 150 scores must use the freeze artifact, not a dirty worktree. |
| `hard50` | `hard50/` | Hard-50 packages only (no `reference_solution/`). Do **not** copy into `tasks/`. |
| `python200_legacy` | `python200_tasks/` | **Superseded** 150 + External-50 view. Historical scores only. |
| `sanity` | `sanity/` | Harness smoke. Never a leaderboard. |
| `staging` / `batch3_pilot` | `staging/` / `batch3_pilot/` | Local candidate workspaces. Not paper splits. |

```bash
PYTHONPATH=harness python3.12 -B -m featureliftbench.cli catalog list --kind suites
./scripts/run_benchmark.sh --benchmark python200_hard --agent openhands --method main
```

`python200_hard_tasks/` and `python200_tasks/` are **generated views**, not a
second edit surface. Change a task in its canonical split (`tasks/`, `hard50/`,
or `external50/`), then rematerialize the view if needed.

## Top-level layout

```text
benchmark/
  suites.toml                 # named --benchmark ids (authority for runners)
  manifest.json               # split registry (roots, lifecycle)
  tasks/                      # frozen Python-150 packages
  hard50/                     # Hard-50 packages (no oracle / reference_solution)
  external50/                 # superseded easy/copy-heavy 50; not the new main table
  python200_hard_tasks/       # symlink view: 150 + Hard-50
  python200_tasks/            # symlink view: 150 + External-50 (superseded)
  sources/                    # canonical registries and archives
  vendor-wheels/              # offline eval wheels
  selection/                  # suite JSON, Hard-50 ledger, freeze helpers
  submissions/                # maintainer reference artifacts (not agent output)
  sanity/                     # Python smoke
  curated/                    # Curated-7 appendix; excluded from Main
  go/  go_pilot/              # Go calibration; not paper-ready
  pilots/                     # historical Pilot-16 manifests
  staging/  batch3_pilot/     # local design/calibration (often gitignored)
  hard50_pilot/               # Hard-50 construction workspace (high-risk local payload)
  quarantine/  contract_v2/   # historical repair workspaces
```

Local staging and pilot trees may exist on a maintainer machine. They are not
the clone-and-run paper surface.

## Split semantics

### `benchmark/python200_hard_tasks/` — paper Python-200'

- 200 symlinks. Source registry:
  [`sources/python200_hard_registry.json`](sources/python200_hard_registry.json).
- Suite membership:
  [`selection/python200_hard_suite.json`](selection/python200_hard_suite.json).
- Materialize / check:
  `python3.12 benchmark/selection/scripts/materialize_python200_hard_release.py --check`.
- Do not treat this directory as a place to create or edit packages.

### `benchmark/tasks/` — frozen Python-150

- 150 packages admitted to the contract-hardened freeze
  `0b106842710368a497b49b7f6714e0dfea54778d1fb2dae38c93ea449b339542`.
  Its pre-hardening ancestor `846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd`
  matches only 102/150 of these packages; experiment runs materialized from that
  ancestor must be reported against it, not against the current freeze.
- The worktree may drift relative to that freeze. Paper 150 numbers must come
  from the freeze artifact, not an uncommitted dirty tree.
- **New tasks must not be created here.** Promote from staging/pilot only after
  gates pass. Hard-50 must not be copied here.

### `benchmark/hard50/` — Hard-50

- 50 packages, disjoint repositories from Python-150 and External-50.
- No `reference_solution/` on the release tree.
- Selection ledger: `selection/hard50_expansion_20260827.json`.

### `benchmark/external50/` and `benchmark/python200_tasks/` — superseded 150+E50

- External-50 remains as an easy / copy-heavy side split.
- `python200_tasks/` is the old unified view. Do not report it as the new paper
  main table. Historical 21.5%–72.5% numbers stay in STATUS as superseded.

### `benchmark/sources/`

- Python-150: [`sources/registry.json`](sources/registry.json).
- Python-200': [`sources/python200_hard_registry.json`](sources/python200_hard_registry.json).
- Policy: [`docs/FULL_REPOSITORY_SOURCE_POLICY.md`](../docs/FULL_REPOSITORY_SOURCE_POLICY.md).
- Agent workspaces are materialized from registered archives, not from a
  task-local `repo/` slice.

### `benchmark/sanity/`, `curated/`, `go/`

- Sanity: smoke only; never Main Pass@N.
- Curated-7: appendix / vibe_app extension; disjoint from Main.
- Go: calibration; not a paper hard split.

### `benchmark/submissions/`

- Maintainer reference submissions. Never mounted in the functional evaluator.
- Agents write `submission/` under the run workspace, not here.

## Per-task package (Python)

```text
benchmark/<canonical-split>/<task_id>/
  metadata.json
  requirements.lock
  TASK.md
  repo/                      # provenance marker; full source comes from the registry
  public_tests/
  hidden_tests/
  evaluation/
  reference_solution/        # optional; absent on Hard-50 release
```

Go tasks use `environment/go.mod` instead of `requirements.lock`. See
[`docs/reference/06_task_schema.md`](../docs/reference/06_task_schema.md).

## Agent output

Agents produce an installable package at `submission/featurelifted/`. Tests
import `featurelifted`, not `submission`.

## Adding tasks

| Action | Location |
| --- | --- |
| New Python candidate | `staging/` or `batch3_pilot/` |
| Promote to frozen Python-150 | `tasks/` only after gates + new freeze |
| Promote Hard-50 | `hard50/` only; never `tasks/` |
| Python smoke | `sanity/` |
| Go calibration | `go/tasks/` |
| Oracle / gold reference | `submissions/` |
| Canonical source | `sources/` |

```bash
python3 scripts/check_task_lifecycle.py
```

## Related docs

- [`docs/STATUS.md`](../docs/STATUS.md) — paper suite identity and counts
- [`docs/archive/plans/PLAN_HARD50_EXPANSION.md`](../docs/archive/plans/PLAN_HARD50_EXPANSION.md) — Hard-50 release record
- [`docs/reference/06_task_schema.md`](../docs/reference/06_task_schema.md)
- [`docs/reference/07_incremental_task_rules.md`](../docs/reference/07_incremental_task_rules.md)
- [`docs/FULL_REPOSITORY_SOURCE_POLICY.md`](../docs/FULL_REPOSITORY_SOURCE_POLICY.md)
