---
name: featureliftbench-create-task
description: Create or materialize FeatureLiftBench benchmark tasks from real upstream Python repositories. Use when designing a new task, building a task package in benchmark/staging or benchmark/batch3_pilot, writing TASK.md, metadata.json, public_tests, hidden_tests, evaluation files, requirements.lock, or a reference_solution. Do not use for promotion into benchmark/tasks; use featureliftbench-promote-task after validation instead.
---

# FeatureLiftBench Create Task

## Guardrails

- Start new Python work in `benchmark/staging/` or `benchmark/batch3_pilot/`; never create new tasks directly in `benchmark/tasks/`.
- Use a real pinned upstream snapshot in `<task_id>/repo/`. Do not make evaluators depend on `benchmark/sources/`, live clones, or network access.
- Do not fabricate commits, licenses, test results, calibration results, LOC counts, or upstream behavior.
- Keep agent output expectations fixed at `submission/featurelifted/`; tests must import `featurelifted`.
- Hidden tests must exercise documented behavior only: `TASK.md`, metadata `feature.included_behaviors`, or `expected_hidden_behaviors`.
- Leave promotion, manifest count updates, and main split membership to `$featureliftbench-promote-task`.

## Required Context

Before creating or materially changing a task, read:

- `docs/07_incremental_task_rules.md`
- `docs/06_task_schema.md`
- `docs/python/01_python_repo_selection_criteria.md`
- `docs/python/03_python_difficulty_rubric.md`
- `benchmark/README.md`

For examples, inspect a nearby task in the intended split and, for hard-3 pilots, a task design note under `docs/task_designs/`.

## Workflow

1. Define the source.
   - Record upstream name, URL, pinned commit, and license.
   - Reject repositories needing services, browsers, cloud credentials, network, large binary assets, or unstable platform behavior.

2. Define the feature slice.
   - Prefer realistic, bounded extraction targets: parsers, validators, serializers, config loaders, path/resource resolvers, plugin registries, retry/rule engines.
   - Document included behavior, excluded behavior, target APIs, source hints, forbidden imports, and forbidden paths.
   - Avoid greenfield prompt-only tasks where the source closure adds little value.

3. Build the task package.
   - Required Python paths: `metadata.json`, `requirements.lock`, `TASK.md`, `repo/`, `public_tests/`, `hidden_tests/`, `evaluation/`.
   - For pilots, `reference_solution/featurelifted/` and `evaluator_config.yaml` may be present.
   - Set lifecycle status to `design_only`, `needs_review`, or `materialized_candidate`; use `blocked` with `blocked_reason` when materialization would require fabrication.

4. Write tests.
   - Public tests should expose the API and common behaviors.
   - Hidden tests should cover edge, error, state, compatibility, and integration behavior already documented.
   - Both public and hidden tests import `featurelifted`, not `submission` and not the upstream package.

5. Add evaluation metadata.
   - `evaluation/forbidden_imports.txt` must match upstream imports disallowed at runtime.
   - `evaluation/oracle_manifest.json` should list required source files and support isolation review.
   - Metadata `environment` should include offline/network/timeout/dependency restrictions.

6. Validate locally.
   - Run `python3 scripts/check_task_lifecycle.py`.
   - Run `PYTHONPATH=harness python3 -B -m featureliftbench.cli validate-task <task_dir> --json`.
   - If a reference exists, evaluate it locally and preferably with Docker before claiming materialization is complete.

## Status Decisions

- Use `design_only` when the design exists but package files or source snapshot are incomplete.
- Use `needs_review` when the package is runnable but spec, scope, license, or entanglement needs review.
- Use `materialized_candidate` only after source snapshot, tests, evaluator metadata, and reference/oracle artifacts exist.
- Use `blocked` when proceeding would require inventing source, behavior, or results.

## Output

End with:

- task directory path
- lifecycle status
- files created or changed
- commands run and their result
- remaining gates before validation or promotion
