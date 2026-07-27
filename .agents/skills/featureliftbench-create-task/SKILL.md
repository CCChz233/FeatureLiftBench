---
name: featureliftbench-create-task
description: Create or materialize FeatureLiftBench benchmark tasks from real upstream Python repositories. Use when designing a new task, building a task package in benchmark/staging or benchmark/batch3_pilot, writing TASK.md, metadata.json, public_tests, hidden_tests, evaluation files, requirements.lock, or a reference_solution. Do not use for promotion into benchmark/tasks; use featureliftbench-promote-task after validation instead.
---

# FeatureLiftBench Create Task

## Guardrails

- Start new Python work in `benchmark/staging/` or `benchmark/batch3_pilot/`; never create new tasks directly in `benchmark/tasks/`.
- Use a real pinned upstream revision and register it in the canonical source
  registry. A task-local `repo/` is staging provenance, not v2 Main source proof;
  evaluators must not depend on live clones or network access.
- Do not fabricate commits, licenses, test results, calibration results, LOC counts, or upstream behavior.
- Keep agent output expectations fixed at `submission/featurelifted/`; tests must import `featurelifted`.
- Hidden tests must exercise documented behavior only: `TASK.md`, metadata `feature.included_behaviors`, or `expected_hidden_behaviors`.
- Leave promotion, manifest count updates, and main split membership to `$featureliftbench-promote-task`.

## Required Context

Before creating or materially changing a task, read:

- `docs/BENCHMARK_DESIGN.md`
- `docs/TASK_DESIGN_RULES.md`（规格规则；与旧文冲突时以此为准）
- `docs/FULL_REPOSITORY_SOURCE_POLICY.md`
- `docs/EXPERIMENT_ARMS.md`（若涉及臂相关测试布局）
- `docs/07_incremental_task_rules.md`
- `docs/06_task_schema.md`
- `docs/python/01_python_repo_selection_criteria.md`
- `docs/python/03_python_difficulty_rubric.md`
- `benchmark/README.md`

New tasks target `public_spec` / generated TASK; never maintain a second
handwritten Agent-visible specification. Inspect a nearby task in the intended
split for package examples. Historical per-task Python design notes were removed
because they duplicated metadata and exposed source-location hints.

## Workflow

1. Define the source.
   - Record upstream name, URL, pinned commit, and license.
   - Reject repositories needing services, browsers, cloud credentials, network, large binary assets, or unstable platform behavior.

2. Define the feature slice.
   - Prefer realistic, bounded extraction targets: parsers, validators, serializers, config loaders, path/resource resolvers, plugin registries, retry/rule engines.
   - Document included behavior, excluded behavior, target APIs, forbidden imports,
     and forbidden paths. Source entrypoints may exist only as private maintainer
     provenance or an explicit ablation input; never render them into Main.
   - Avoid greenfield prompt-only tasks where the source closure adds little value.

3. Build the task package.
   - Required Python paths: `metadata.json`, `requirements.lock`, generated
     `TASK.md`, staging `repo/`, `public_tests/`, `hidden_tests/`, `evaluation/`.
   - For pilots, `reference_solution/featurelifted/` and `evaluator_config.yaml` may be present.
   - Set lifecycle status to `design_only`, `needs_review`, or `materialized_candidate`; use `blocked` with `blocked_reason` when materialization would require fabrication.

4. Write tests.
   - Public tests should exercise the API and common behaviors, but remain private
     evaluator assets in Main.
   - Hidden tests should cover edge, error, state, compatibility, and integration behavior already documented.
   - Both public and hidden tests import `featurelifted`, not `submission` and not the upstream package.

5. Add evaluation metadata.
   - `evaluation/forbidden_imports.txt` must match upstream imports disallowed at runtime.
   - `evaluation/oracle_manifest.json` should list required source files and support isolation review.
   - Metadata `environment` should include offline/network/timeout/dependency restrictions.
   - Add the upstream revision to `benchmark/sources/registry.json` with immutable
     revision, archive/tree digests, license path, scope, and source statistics.

6. Validate locally.
   - Run `python3 scripts/check_task_lifecycle.py`.
   - Run the source registry/materialization checks.
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
