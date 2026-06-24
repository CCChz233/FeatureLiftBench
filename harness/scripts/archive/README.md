# Archived Task-Scaffolding Scripts

These scripts were used to **build** benchmark tasks during initial dataset construction. They are not needed to run or evaluate the benchmark.

## When you might still use them

| Script | Use case |
| --- | --- |
| `setup_vibe_app_tasks.py` | After editing `benchmark/sources/vibe_app/`, copy into all three `vibe_app__*` task repos |
| `generate_vibe_app_source.py` | Regenerate `benchmark/sources/vibe_app/` |
| `setup_m3_tasks.py` | One-time scaffold for jinja2×4 and pytest×3 tasks (references `/tmp/flb-clones/`) |

## Deprecated wrappers

| Script | Replacement |
| --- | --- |
| `list_extreme_tasks.py` | `python3 harness/scripts/list_tasks.py --tag extreme` |
| `analyze_extreme_suite.py` | `python3 harness/scripts/analyze_benchmark_suite.py <suite_dir>` |

## Active scripts (repo `harness/scripts/`)

- `list_tasks.py` — list/filter tasks
- `analyze_benchmark_suite.py` — suite analysis entry point
- `analyze_suite_results.py` — report generator (called by above)
- `build_oracle_submission.py` — build/verify Oracle submissions
