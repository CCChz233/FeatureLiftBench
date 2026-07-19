# Incremental Task Rules

This document defines the **canonical lifecycle** and **promotion gates** for adding FeatureLiftBench tasks. It applies to all language splits unless a language-specific doc explicitly overrides a detail.

Related:

- [`benchmark/README.md`](../benchmark/README.md) — directory layout
- [`benchmark/manifest.json`](../benchmark/manifest.json) — split registry
- [`06_task_schema.md`](06_task_schema.md) — per-task package schema
- [`python/01_python_repo_selection_criteria.md`](python/01_python_repo_selection_criteria.md) — upstream repo criteria
- [`STATUS.md`](STATUS.md) — current main-split size and Oracle freeze

## Principles

1. **New work starts in staging or pilot**, never directly in a main split.
2. **Each task owns its upstream snapshot** in `<task_id>/repo/`. Do not point evaluators at `benchmark/sources/` or live upstream checkouts.
3. **Lifecycle status is explicit** in `metadata.json` for all new tasks. Legacy main tasks without `status` are grandfathered by split membership only.
4. **Promotion is evidence-based.** A task advances only when named gates pass and evidence is recorded (gate logs, calibration runs, inventory updates).
5. **Read-only audit first.** Run `python3 scripts/check_task_lifecycle.py` before and after materialization changes.

## Task Lifecycle

| Status | Definition |
|---|---|
| `design_only` | Feature selected and documented (`TASK.md`, design note, metadata draft). No complete runnable package yet; `repo/` may be missing or incomplete. |
| `blocked` | Materialization cannot proceed without fabricating source, behavior, or results. **Must** include `blocked_reason` (and `blocked_evidence` when available). |
| `needs_review` | Runnable package present but human review pending (spec clarity, scope, license, entanglement audit). |
| `materialized_candidate` | Source snapshot, tests, evaluator metadata, and reference/oracle artifacts exist. Calibration and gates may still be TODO. |
| `validated_candidate` | All structural gates pass; oracle/reference verified; public/hidden tests aligned with spec. Awaiting difficulty calibration or batch acceptance. |
| `hard_candidate` | Difficulty gate passed for `hard` label (strong-model calibration recorded). Ready for main-split promotion review. |
| `main` | Task is a member of a main paper split (`benchmark/tasks/` for Python). Implicit for legacy tasks without `status`. |
| `sanity` | Smoke/harness task in `benchmark/sanity/` or `benchmark/go/sanity/`. Never on main leaderboard. |
| `archived` | Retired or superseded task kept for history. Not scheduled for promotion. |

### Allowed transitions

```text
design_only → needs_review | blocked
needs_review → materialized_candidate | blocked
materialized_candidate → validated_candidate | blocked | needs_review
validated_candidate → hard_candidate | staging retention
hard_candidate → main (via promotion)
any → archived (explicit retirement)
sanity → (no promotion to main)
```

**Hard rule:** `design_only`, `needs_review`, and `materialized_candidate` tasks **must not** be added directly under `benchmark/tasks/`.

## Where New Tasks May Land

| Goal | First landing zone | May promote to |
|---|---|---|
| New Python feature lift | `benchmark/staging/` or `benchmark/batch3_pilot/` | `benchmark/tasks/` |
| Python hard-3 pilot | `benchmark/batch3_pilot/` | `benchmark/staging/` → `benchmark/tasks/` |
| Python smoke | `benchmark/sanity/` | (none) |
| Go calibration | `benchmark/go/tasks/` | Go hard split (TODO — not paper-ready yet) |
| Oracle / gold only | `benchmark/submissions/<task_id>/` | (harness artifact, not a task split) |
| Shared upstream template | `benchmark/sources/` | copied into per-task `repo/` |

**Do not use as eval input:** `benchmark/sources/`, live git clones, agent `submission/` trees.

## Promotion Gates

A task promotes **one gate at a time**. Record evidence under `evidence/` or the relevant gate review directory before changing split membership.

### 1. Source Gate

**Purpose:** Prove the task is grounded in a real, pinned upstream snapshot.

Pass when:

- `metadata.json` records `source.name`, `source.url`, `source.commit` (or equivalent flat `repo` + `commit` for pilot schema).
- License recorded and compatible with benchmark use.
- Task-local `repo/` contains the pinned snapshot used to author tests and oracle.
- `blocked` tasks are not promoted; they must remain in pilot/staging with `blocked_reason`.

### 2. Task Package Gate

**Purpose:** Ensure the directory is a complete evaluator-ready package.

Pass when (Python):

- `metadata.json`, `requirements.lock`, `repo/`, `public_tests/`, `hidden_tests/`, `evaluation/` present.
- `TASK.md` documents included/excluded behavior and target API.
- `metadata.json` includes `task_id`, `language`, `source`, `feature`, `output`, `tests`, `environment`.
- `task_id` matches directory name.

Pass when (Go):

- `metadata.json`, `repo/`, `public_tests/`, `hidden_tests/`, `evaluation/`, `environment/go.mod` present.
- Go module and output package fields documented in metadata.

### 3. Reference Gate

**Purpose:** Prove the feature is extractable and tests are trustworthy.

Pass when:

- Oracle or `reference_solution/` passes public and hidden tests locally.
- `evaluation/oracle_manifest.json` lists required source files consistent with `repo/`.
- `evaluation/forbidden_imports.txt` (and metadata forbidden paths) match isolation intent.
- Hidden tests exercise **documented** behaviors only — no hidden-only API requirements.

### 4. Isolation Gate

**Purpose:** Ensure agents cannot trivially re-import the original package.

Pass when:

- Forbidden imports/paths enforced and verified (audit-output-imports, copy-all, module probes as applicable).
- Tests import **`featurelifted`** (Python), not `submission` and not the upstream package name.
- Agent deliverable path is `submission/featurelifted/` (Python package name **`featurelifted`**).
- No evaluator or hidden-test dependency on undisclosed files outside `repo/` closure.

### 5. Difficulty Gate

**Purpose:** Prevent hand-waved `hard` labels.

Pass when:

- Declared difficulty recorded in metadata (`difficulty`, `difficulty_initial` for pilots).
- For `hard` tasks: strong-model calibration run completed (e.g. OpenHands + tier-A/B model) with results archived under `experiments/` or `evidence/`.
- Calibration summary documents pass rate band, failure modes, and whether the task discriminates models.
- `hard_reason` (or `entanglement` + `expected_hidden_behaviors`) explains why the closure is hard.
- **Manual `hard` labels alone are insufficient** — calibration evidence required before `hard_candidate` → `main`.

## Python-Specific Rules

### Output layout

```text
submission/
  pyproject.toml          # or setup.cfg/setup.py as task allows
  featurelifted/
    __init__.py
    ...
```

- Canonical package name: **`featurelifted`**.
- `metadata.output.package` must be `featurelifted`.

### Tests

- Public and hidden tests import from `featurelifted`.
- Do **not** import `submission` in tests.
- Hidden tests must not require behaviors absent from `feature.included_behaviors`, `TASK.md`, or documented `expected_hidden_behaviors`.

### Blocked tasks

When status is `blocked`, metadata **must** include:

```json
"blocked_reason": "..."
```

Optional but recommended: `blocked_evidence` with upstream URL, commit, and what failed (clone, license, missing sources, etc.).

## Promoting a Batch-3 Pilot to Main

Example path for `benchmark/batch3_pilot/<task_id>`:

1. **Unblock or finish materialization** — status `materialized_candidate`, full `repo/`, not `blocked`.
2. **Run lifecycle checker** — `python3 scripts/check_task_lifecycle.py`; fix all errors.
3. **Pass gates 1–4** — source, package, reference, isolation (local oracle + audit scripts).
4. **Pass gate 5** — run strong-model calibration; archive results; set `hard_candidate` in metadata.
5. **Copy to staging** — `benchmark/staging/<task_id>/` for batch review (do not skip if batch policy requires staging).
6. **Inventory update** — add row to `docs/python/02_python_repo_task_inventory.md`.
7. **Promote to main** — copy approved task tree to `benchmark/tasks/<task_id>/`; set `status` to `main` (or omit only if matching legacy convention deliberately).
8. **Update manifest counts** — refresh `benchmark/manifest.json` scanned counts after promotion.
9. **Re-run checker** — confirm no overlap, no missing metadata, no ID collision.

Never move or delete the pilot directory unless explicitly archiving; prefer copy-on-promote to preserve pilot history.

## Checklist Before Any Promotion

- [ ] `python3 scripts/check_task_lifecycle.py` passes or only documents known grandfathered issues
- [ ] `task_id` not already in target split
- [ ] Oracle in `benchmark/submissions/<task_id>/` if harness expects it
- [ ] No fabricated commits, LOC, or experiment results
- [ ] Design note or `TASK.md` linked from inventory
- [ ] Difficulty calibration evidence on file for `hard` tasks
