# Upstream Source Snapshots

Master copies used when building or refreshing benchmark tasks. Runtime evaluation uses per-task snapshots under `benchmark/tasks/<task_id>/repo/`.

## Contents

| Path | Purpose |
| --- | --- |
| `vibe_app/` | Curated legacy-style shop backend. After editing, sync into task repos with `python3 harness/scripts/archive/setup_vibe_app_tasks.py`. |

## Rebuilding OSS task repos

Coverage, jinja2, pytest, sqlparse, and other OSS tasks do **not** keep a second upstream tree here. Clone the pinned commit from [`docs/benchmark_tasks.md`](../docs/benchmark_tasks.md) and copy into `benchmark/tasks/<task_id>/repo/`.
