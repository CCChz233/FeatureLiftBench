# Task Lifecycle Report

Generated: 2026-09-06

Read-only audit from `scripts/check_task_lifecycle.py`. No files were modified.

## Summary

- Tasks checked: 224
- Tasks with errors: 7
- Tasks with warnings: 0
- Global issues: 0

### Lifecycle status counts

| Status | Count |
|---|---:|
| implicit_archived | 1 |
| implicit_sanity | 4 |
| implicit_validated_candidate | 12 |
| legacy_main_implicit | 100 |
| main | 57 |
| materialized_candidate | 38 |
| validated | 12 |

## Manifest splits

- **python_main_candidate** (`benchmark/tasks`): checked 157 tasks, errors 7
- **python200_external** (`benchmark/external50`): checked 50 tasks, errors 0
- **python_sanity** (`benchmark/sanity`): checked 3 tasks, errors 0
- **go_candidate** (`benchmark/go/tasks`): checked 12 tasks, errors 0
- **go_sanity** (`benchmark/go/sanity`): checked 1 tasks, errors 0
- **go_legacy_pilot** (`benchmark/go_pilot`): checked 1 tasks, errors 0

## Tasks with errors

| Split | Task | Status | Issues |
|---|---|---|---|
| python_main_candidate | `vibe_app__csv_transform_core__001` | legacy_main_implicit | missing metadata.json |
| python_main_candidate | `vibe_app__orm_query_ast_core__001` | legacy_main_implicit | missing metadata.json |
| python_main_candidate | `vibe_app__plugin_registry_core__001` | legacy_main_implicit | missing metadata.json |
| python_main_candidate | `vibe_app__pricing_rules_core__001` | legacy_main_implicit | missing metadata.json |
| python_main_candidate | `vibe_app__rules_engine_core__001` | legacy_main_implicit | missing metadata.json |
| python_main_candidate | `vibe_app__session_registry_core__001` | legacy_main_implicit | missing metadata.json |
| python_main_candidate | `vibe_app__yaml_config_bootstrap__001` | legacy_main_implicit | missing metadata.json |

## Full data

See `reports/audits/task_lifecycle_report.csv` for the complete per-task matrix.

