---
name: featureliftbench-promote-task
description: Promote one validated FeatureLiftBench task from benchmark/staging or benchmark/batch3_pilot into the Python main split benchmark/tasks. Use after source, package, reference, isolation, and difficulty gates have passed and the user explicitly asks to make a task part of the main leaderboard. This skill updates task copy, metadata status/schema, manifest/inventory, and runs lifecycle validation.
---

# FeatureLiftBench Promote Task

## Guardrails

- Promote one task at a time. Do not bulk-copy a whole pilot batch into `benchmark/tasks/`.
- Do not promote `blocked`, `design_only`, `needs_review`, or plain `materialized_candidate` tasks without explicit evidence that all gates passed.
- Never fabricate reference eval, Docker eval, agent calibration, or difficulty evidence.
- Prefer copy-on-promote. Preserve pilot/staging history unless the user explicitly asks to archive it.
- Do not commit ignored experiment outputs, `.env`, secrets, or local-only reports.

## Required Context

Before promotion, read:

- `docs/07_incremental_task_rules.md`
- `docs/06_task_schema.md`
- `benchmark/README.md`
- `docs/python/02_python_repo_task_inventory.md`
- the candidate task's `TASK.md` and `metadata.json`

Run `$featureliftbench-validate-task` first when the user has not already supplied a gate verdict.

## Promotion Workflow

1. Preflight.
   - Run the helper:

```bash
python3 .agents/skills/featureliftbench-promote-task/scripts/preflight_promotion.py <task_id>
```

   - Confirm source task exists, target task does not exist, status is acceptable, and no duplicate task ID is present.

2. Verify gates.
   - Source, package, reference/oracle, isolation, and difficulty gates must have evidence.
   - For hard tasks, require strong-agent calibration evidence and a short failure-mode summary.

3. Copy task.
   - For batch3 pilot tasks, use the repo script when appropriate:

```bash
python3 scripts/promote_batch3_task.py <task_id>
```

   - For other staging tasks, copy into `benchmark/tasks/<task_id>/` and normalize metadata manually according to `docs/06_task_schema.md`.

4. Normalize metadata.
   - Set or preserve `task_id`, `language`, `difficulty`, `source`, `feature`, `output`, `environment`, and `tests`.
   - Use `status: main` for new main tasks unless intentionally matching legacy implicit-main convention.
   - Keep `output.package` as `featurelifted`.

5. Update registries.
   - Update `docs/python/02_python_repo_task_inventory.md`.
   - Update `benchmark/manifest.json` split counts and any relevant notes.

6. Validate.
   - Run `python3 scripts/check_task_lifecycle.py`.
   - Run `PYTHONPATH=harness python3 -B -m featureliftbench.cli validate-task benchmark/tasks/<task_id> --json`.
   - Re-run reference/oracle eval if the promotion changed paths, metadata, or oracle placement.

7. Commit.
   - Stage only benchmark task files, manifest/inventory updates, and intended skill/script/docs changes.
   - Do not stage `experiments/`, `reports/`, `evidence/`, `.env`, or local-only batch workspaces unless the user explicitly changed publication policy.

## Output

End with:

- promoted task ID
- source path and target path
- gate evidence summary
- files changed
- validation commands and results
- commit hash if committed
