---
name: featureliftbench-validate-task
description: Audit FeatureLiftBench task packages and decide whether a task can progress toward the Python main leaderboard. Use when checking source, package, reference/oracle, isolation, hidden-test fairness, difficulty calibration, lifecycle status, or whether a benchmark under benchmark/staging or benchmark/batch3_pilot is ready for promotion. This skill is primarily read-only and should not promote tasks.
---

# FeatureLiftBench Validate Task

## Guardrails

- Default to read-only inspection. Do not copy tasks into `benchmark/tasks/`, update manifests, or change lifecycle status unless explicitly asked to fix a concrete issue.
- Treat `benchmark/tasks/` membership as main split, but do not use legacy main shortcuts for new tasks.
- Do not accept `hard` labels without calibration evidence.
- Do not accept hidden tests that require behavior absent from `TASK.md`, metadata, or documented expected hidden behaviors.
- Report uncertain evidence as missing; never infer experiment success from file names alone.

## Required Context

Read these before a promotion-readiness review:

- `docs/07_incremental_task_rules.md`
- `docs/06_task_schema.md`
- `docs/python/01_python_repo_selection_criteria.md`
- `docs/python/03_python_difficulty_rubric.md`
- `benchmark/README.md`

Use `scripts/check_task_lifecycle.py` as the repository-level audit and `scripts/audit_featurelift_task.py` in this skill for a task-local preflight.

## Review Workflow

1. Identify the task.
   - Confirm the directory exists and `metadata.json` parses.
   - Confirm `task_id` matches the directory name and does not already exist in the target main split.
   - Reject `blocked` tasks unless the request is specifically to diagnose the block.

2. Source gate.
   - Verify source name, URL, commit, and license are recorded.
   - Verify task-local `repo/` exists and is the formal upstream snapshot.
   - Reject fabricated or vague source claims.

3. Package gate.
   - Python tasks require `metadata.json`, `requirements.lock`, `TASK.md`, `repo/`, `public_tests/`, `hidden_tests/`, and `evaluation/`.
   - Metadata must include source, feature, output, tests, environment, language, difficulty, and status for new tasks.
   - `metadata.output.package` must be `featurelifted`.

4. Reference gate.
   - Reference/oracle must pass public and hidden tests before validation is complete.
   - `evaluation/oracle_manifest.json` must align with source files.
   - `evaluation/forbidden_imports.txt` and metadata forbidden imports/paths must align.

5. Isolation gate.
   - Public and hidden tests must import `featurelifted`, not `submission` or the upstream package.
   - Evaluation must forbid upstream imports and paths.
   - Check for accidental hidden dependencies on local files, network, random state, wall-clock time, or undisclosed data.

6. Difficulty gate.
   - Require hard calibration evidence for hard main promotion: strong-agent run results, pass/fail band, failure modes, and compactness or extraction-ratio notes when available.
   - Prefer evidence under `experiments/`, `evidence/`, or named reports, but remember those directories may be ignored in public clones.

## Commands

Run the lightweight task preflight:

```bash
python3 .agents/skills/featureliftbench-validate-task/scripts/audit_featurelift_task.py <task_dir>
```

Run repository lifecycle audit:

```bash
python3 scripts/check_task_lifecycle.py
```

Run harness validation:

```bash
PYTHONPATH=harness python3 -B -m featureliftbench.cli validate-task <task_dir> --json
```

When a reference solution exists and the environment is available, evaluate it with the harness and, for promotion review, Docker as well.

## Verdict Format

End with one of:

- `pass`: all requested gates have evidence.
- `fix_required`: the task is plausible but missing files, metadata, tests, oracle proof, isolation proof, or calibration evidence.
- `reject`: blocked, fabricated, duplicate, unfair hidden behavior, impossible isolation, or unsuitable source.

Include concise gate-by-gate findings and the exact missing evidence.
