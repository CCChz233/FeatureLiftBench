# Sanity / smoke tasks

Three **non-hard** tasks used for harness and evaluator smoke checks. They are **not** part of the main 50-hard benchmark leaderboard.

| task_id | difficulty |
| --- | --- |
| `iniconfig__parse_config__001` | easy |
| `python_slugify__slugify_core__001` | medium |
| `python_pathspec__gitignore_match__001` | medium |

Run validation:

```bash
python3 -m featureliftbench.cli validate-task benchmark/sanity/<task_id>/
python3 harness/scripts/list_tasks.py --root benchmark/sanity
```

Main benchmark tasks live under [`../tasks/`](../tasks/).
