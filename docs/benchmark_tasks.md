# FeatureLiftBench Task Catalog

FeatureLiftBench is **one benchmark**: every task lives under `benchmark/tasks/<task_id>/`, uses the same `metadata.json` schema, the same evaluator, and the same scoring (`FunctionalGate` + `ExtractionRatio`). Tasks differ mainly in **`difficulty`**, **`entanglement`**, and **`feature`** scope—not in harness or rules.

**Current size:** 28 tasks (Python-only v0).

Benchmark evolution is **add or remove tasks** under `benchmark/tasks/`; do not fork separate collections or alternate schemas.

- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Task format:** [TASK_FORMAT.md](TASK_FORMAT.md)
- Directory map: [DIRECTORY.md](DIRECTORY.md)
- Design note template: [task_designs/TEMPLATE.md](task_designs/TEMPLATE.md)

## Running the full benchmark

```bash
pip install -e .

python3 harness/scripts/list_tasks.py

python3 -B -m featureliftbench.cli run-agent \
  benchmark/tasks \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --env-file .env \
  --num-workers 2 \
  --output experiments/mini-swe-agent/<run_id>
```

`run-agent benchmark` or `run-agent benchmark/tasks` also resolves to the full task set (28 tasks).

Optional **analysis slices** (same benchmark, filtered reporting):

```bash
python3 harness/scripts/list_tasks.py --tag multi-task-repo --paths
python3 harness/scripts/list_tasks.py --difficulty hard --paths
```

Analyze a suite run:

```bash
python3 harness/scripts/analyze_benchmark_suite.py experiments/mini-swe-agent/<run_id>
```

## Difficulty (primary axis)

| Difficulty | Count | Tasks |
| --- | ---: | --- |
| easy | 1 | `iniconfig__parse_config__001` |
| medium | 2 | `python_slugify__slugify_core__001`, `python_pathspec__gitignore_match__001` |
| hard | 25 | all remaining tasks |

Hard tasks span clean OSS packages, multi-task-per-repo slices, and one curated legacy-style app (`vibe_app`).

## Optional metadata tags (reporting only)

Tags do **not** define separate benchmarks. Use them to slice results:

| Tag | Meaning |
| --- | --- |
| `multi-task-repo` | Shares a pinned `source.commit` with other tasks from the same upstream repo |
| `functional-discriminator` | Hidden tests emphasize incomplete oracle closures |
| `decoupling-discriminator` | Oracle vs Copy-All extraction spread matters |
| `extreme` | Legacy tag on newer hard tasks; prefer `difficulty=hard` + entanglement fields |

## Pinned source commits

| Source | URL | Commit | License |
| --- | --- | --- | --- |
| iniconfig | https://github.com/pytest-dev/iniconfig | (per task metadata) | MIT |
| python-slugify | https://github.com/un33k/python-slugify | (per task metadata) | MIT |
| python-pathspec | https://github.com/cpburnz/python-pathspec | (per task metadata) | MPL-2.0 |
| tomlkit / packaging / pluggy / click / markdown-it-py / PyYAML / jsonschema | (see each task) | (per task metadata) | (per task) |
| sqlparse | https://github.com/andialbrecht/sqlparse | `f80af6a4007f11ada847218df8c29dc859238290` | BSD-3-Clause |
| coveragepy | https://github.com/coveragepy/coveragepy | `f0dcf65f47120d9f74f6777134d3b8e92515ce6f` | Apache-2.0 |
| jinja | https://github.com/pallets/jinja | `15206881c006c79667fe5154fe80c01c65410679` | BSD-3-Clause |
| pytest | https://github.com/pytest-dev/pytest | `b55ab2aabb68c0ce94c3903139b062d0c2790152` | MIT |
| vibe_app | curated `benchmark/sources/vibe_app/` | in-repo snapshot | MIT |

## All tasks (28)

### easy / medium

| task_id | difficulty | design note |
| --- | --- | --- |
| `iniconfig__parse_config__001` | easy | — |
| `python_slugify__slugify_core__001` | medium | — |
| `python_pathspec__gitignore_match__001` | medium | — |

### hard — single-feature OSS

| task_id | design note |
| --- | --- |
| `tomlkit__roundtrip_document__001` | — |
| `packaging__requirement_marker_specifier__001` | — |
| `pluggy__hook_call_order__001` | — |
| `click__option_parser__001` | — |
| `markdown_it__commonmark_render__001` | — |
| `pyyaml__safe_load_dump__001` | — |
| `jsonschema__validator_core__001` | — |

### hard — sqlparse (×4, same commit)

| task_id | design note |
| --- | --- |
| `sqlparse__parse_format_core__001` | [sqlparse__parse_format_core__001.md](task_designs/sqlparse__parse_format_core__001.md) |
| `sqlparse__parse_split_core__001` | [sqlparse__parse_split_core__001.md](task_designs/sqlparse__parse_split_core__001.md) |
| `sqlparse__token_tree_core__001` | [sqlparse__token_tree_core__001.md](task_designs/sqlparse__token_tree_core__001.md) |
| `sqlparse__format_filters_core__001` | [sqlparse__format_filters_core__001.md](task_designs/sqlparse__format_filters_core__001.md) |

### hard — coveragepy (×4)

| task_id | design note |
| --- | --- |
| `coverage__glob_matcher_core__001` | [coverage__glob_matcher_core__001.md](task_designs/coverage__glob_matcher_core__001.md) |
| `coverage__config_merge_core__001` | [coverage__config_merge_core__001.md](task_designs/coverage__config_merge_core__001.md) |
| `coverage__source_selection_core__001` | [coverage__source_selection_core__001.md](task_designs/coverage__source_selection_core__001.md) |
| `coverage__path_remap_core__001` | [coverage__path_remap_core__001.md](task_designs/coverage__path_remap_core__001.md) |

### hard — jinja2 (×4)

| task_id | design note |
| --- | --- |
| `jinja2__lexer_parser_core__001` | [jinja2__lexer_parser_core__001.md](task_designs/jinja2__lexer_parser_core__001.md) |
| `jinja2__compile_render_core__001` | [jinja2__compile_render_core__001.md](task_designs/jinja2__compile_render_core__001.md) |
| `jinja2__loader_inheritance_core__001` | [jinja2__loader_inheritance_core__001.md](task_designs/jinja2__loader_inheritance_core__001.md) |
| `jinja2__filters_tests_core__001` | [jinja2__filters_tests_core__001.md](task_designs/jinja2__filters_tests_core__001.md) |

### hard — pytest (×3)

| task_id | design note |
| --- | --- |
| `pytest__mark_expression_core__001` | [pytest__mark_expression_core__001.md](task_designs/pytest__mark_expression_core__001.md) |
| `pytest__skipif_eval_core__001` | [pytest__skipif_eval_core__001.md](task_designs/pytest__skipif_eval_core__001.md) |
| `pytest__ini_markers_core__001` | [pytest__ini_markers_core__001.md](task_designs/pytest__ini_markers_core__001.md) |

### hard — vibe_app curated (×3)

| task_id | design note |
| --- | --- |
| `vibe_app__pricing_rules_core__001` | [vibe_app__pricing_rules_core__001.md](task_designs/vibe_app__pricing_rules_core__001.md) |
| `vibe_app__yaml_config_bootstrap__001` | [vibe_app__yaml_config_bootstrap__001.md](task_designs/vibe_app__yaml_config_bootstrap__001.md) |
| `vibe_app__csv_transform_core__001` | [vibe_app__csv_transform_core__001.md](task_designs/vibe_app__csv_transform_core__001.md) |

## Adding or removing tasks

1. Add or delete `benchmark/tasks/<task_id>/` with the [standard layout](TASK_FORMAT.md).
2. Run `featureliftbench validate-task benchmark/tasks/<task_id>/`.
3. Record oracle + [design note](task_designs/TEMPLATE.md) under `docs/task_designs/`.
4. Update this catalog table and pin-commit section if needed.

Do not introduce a second task root, schema, or scoring track for new tasks.
