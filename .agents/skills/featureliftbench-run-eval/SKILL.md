---
name: featureliftbench-run-eval
description: Run FeatureLiftBench reference, Docker, agent, and batch evaluations. Use when executing benchmark experiments, selecting batch1, batch2, main, sanity, staging, or batch3_pilot task subsets, resuming suite runs, summarizing suite.json results, or producing calibration evidence. This skill should write outputs under experiments or reports, not mutate benchmark task definitions.
---

# FeatureLiftBench Run Eval

## Guardrails

- Keep run outputs under `experiments/` or `reports/`; do not commit secrets, `.env`, raw credentials, or bulky run artifacts.
- Use `--task-id` filters for subset runs. Batch identity is a selection concern, not a separate benchmark root.
- Do not mark a task validated or promote it solely because an agent passed; validation and promotion use separate skills.
- Preserve failed runs and logs for difficulty evidence. Do not overwrite previous suites unless explicitly requested.
- Use Docker eval for promotion-quality evidence when available.

## Task Selection

Use the helper script to avoid hand-maintaining long `--task-id` lists:

```bash
python3 .agents/skills/featureliftbench-run-eval/scripts/select_featurelift_tasks.py --suite batch1 --format args
python3 .agents/skills/featureliftbench-run-eval/scripts/select_featurelift_tasks.py --suite batch2 --format args
python3 .agents/skills/featureliftbench-run-eval/scripts/select_featurelift_tasks.py --suite batch3-pilot --format args
python3 .agents/skills/featureliftbench-run-eval/scripts/select_featurelift_tasks.py --suite batch3-main --format args
```

Suite meanings:

- `main`: all task directories under `benchmark/tasks/` with metadata, excluding manifest exclusions.
- `batch1`: main tasks tagged `batch-1`.
- `batch2`: main tasks without `batch-1` or `batch-3`.
- `batch3-main`: promoted main tasks tagged `batch-3`.
- `batch3-pilot`: `benchmark/batch3_pilot/` tasks, defaulting to `materialized_candidate` and skipping `blocked`.
- `staging`: `benchmark/staging/` tasks with metadata.
- `sanity`: `benchmark/sanity/` smoke tasks.

## Common Commands

Validate a task package:

```bash
PYTHONPATH=harness python3 -B -m featureliftbench.cli validate-task <task_dir> --json
```

Evaluate a prepared submission:

```bash
PYTHONPATH=harness python3 -B -m featureliftbench.cli eval <task_dir> <submission_dir> --output <output_dir>
```

Run an agent suite (Official Main uses OpenHands):

```bash
PYTHONPATH=harness python3 -B -m featureliftbench.cli run-agent <task_root> \
  --agent openhands \
  --agent-profile <profile> \
  --env-file .env \
  --eval-docker \
  --output <experiments/.../suite-id> \
  --task-id <task_id>
```

Optional DeepSeek Harness / Codex runtime ablation (not Official Main, not the
Python-200 table):

```bash
./harness/scripts/run_runtime_ablation.sh deepseek-harness dsh_deepseek_v4_flash_main
```

See `docs/METHOD_AGENT_RUNTIME.md`.

Resume an interrupted run:

```bash
PYTHONPATH=harness python3 -B -m featureliftbench.cli run-agent <task_root> \
  --resume <existing_suite_dir> \
  --output <existing_suite_dir>
```

Analyze a completed suite:

```bash
PYTHONPATH=harness python3 harness/scripts/analyze_benchmark_suite.py <suite_dir>
```

## Evidence Summary

After a run, report:

- suite directory
- task count and selected split
- pass/fail/missing submission counts
- failed task IDs and root failure classes when available
- whether Docker eval was used
- commands needed to resume or analyze further
