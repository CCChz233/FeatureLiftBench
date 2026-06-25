# FeatureLiftBench Task Catalog

FeatureLiftBench is **one benchmark**: every task lives under `benchmark/tasks/<task_id>/`, uses the same `metadata.json` schema, the same evaluator, and the same scoring (`FunctionalGate` + `ExtractionRatio`). Tasks differ mainly in **`difficulty`**, **`entanglement`**, and **`feature`** scope—not in harness or rules.

**Current size:** **50 hard** tasks in `benchmark/tasks/` (main leaderboard) + **3 smoke** tasks in `benchmark/sanity/` (easy/medium appendix). `list_tasks.py` and `analyze_benchmark_suite.py` default to hard-only.

Benchmark evolution is **add or remove tasks** under `benchmark/tasks/`; do not fork separate collections or alternate schemas.

- **Concepts:** [CONCEPTS.md](CONCEPTS.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Task format:** [TASK_FORMAT.md](TASK_FORMAT.md)
- **Benchmark status & open issues:** [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)
- Directory map: [DIRECTORY.md](DIRECTORY.md)
- Design note template: [task_designs/TEMPLATE.md](task_designs/TEMPLATE.md)

## Running the full benchmark

```bash
pip install -e .

python3 harness/scripts/list_tasks.py

export PYTHONPATH=harness
PYTHON=/Users/chz/anaconda3/bin/python3.12   # 需 3.11+（系统 3.9 缺 tomllib）

$PYTHON -B -m featureliftbench.cli run-agent \
  benchmark/tasks \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile deepseek_v4_flash \
  --env-file .env \
  --yolo \
  --num-workers 4 \
  --output experiments/mini-swe-agent/<run_id>
```

`run-agent benchmark` or `run-agent benchmark/tasks` resolves to the **50 hard** main set by default.

### Multi-model profiles

Copy [`harness/config/agents.example.toml`](../harness/config/agents.example.toml) to `harness/config/agents.toml` (gitignored). Put API keys in `.env` (see [`.env.example`](../.env.example)).

| Profile | Model | `.env` keys |
| --- | --- | --- |
| `deepseek_v4_flash` | `deepseek/deepseek-v4-flash` | `FEATURELIFTBENCH_API_KEY`, `FEATURELIFTBENCH_API_BASE` |
| `deepseek_v4_pro` | `deepseek/deepseek-v4-pro` | 同上 |
| `nex_n2_pro` | `openai/nex-agi/Nex-N2-Pro` | `SILICONFLOW_API_KEY`, `SILICONFLOW_API_BASE` |
| `qwen3_6_27b` | `openai/Qwen/Qwen3.6-27B` | 同上 |

Switch models with `--agent-profile` only (no need to edit base URL in `.env` between runs).

**Important:** `SILICONFLOW_API_BASE` must be `https://api.siliconflow.cn/v1` (not `/chat/completions`). Non-DeepSeek profiles need their own `*_API_BASE` env var so they are not overridden by `FEATURELIFTBENCH_API_BASE`.

Generic 50-hard baseline script:

```bash
./harness/scripts/run_baseline.sh nex_n2_pro
./harness/scripts/run_baseline.sh deepseek_v4_flash benchmark-50-hard-flash-002
NUM_WORKERS=2 ./harness/scripts/run_baseline.sh deepseek_v4_pro
```

Smoke connectivity check (sanity task, one question):

```bash
$PYTHON -B -m featureliftbench.cli run-agent \
  benchmark/sanity/iniconfig__parse_config__001 \
  --agent mini-swe-agent \
  --agent-config harness/config/agents.toml \
  --agent-profile nex_n2_pro \
  --env-file .env \
  --yolo \
  --output experiments/mini-swe-agent/nex-n2-pro-smoke-001
```

Smoke tasks (not in main leaderboard):

```bash
python3 harness/scripts/list_tasks.py --root benchmark/sanity --paths
```

Optional **analysis slices** (same benchmark, filtered reporting):

```bash
python3 harness/scripts/list_tasks.py --tag multi-task-repo --paths
python3 harness/scripts/list_tasks.py --difficulty hard --paths
```

Analyze a suite run:

```bash
python3 harness/scripts/analyze_benchmark_suite.py experiments/mini-swe-agent/<run_id>
```

Use `--yolo` for non-interactive mini runs. Optional `--no-progress` disables the Rich suite UI.

## Latest full-suite baseline

| Run | Model | Functional pass | Avg `final_score` | Notes |
| --- | --- | ---: | ---: | --- |
| `benchmark-28-deepseek-flash-003` | Flash | 19/28 | 0.407 | 历史；含已迁出 smoke 3 题 |
| `benchmark-50-hard-flash-001` | Flash | **41/50 (82%)** | **0.472** | **当前主 baseline**；9 high-extraction pass；见 `-analysis.md` |
| `benchmark-50-hard-pro-20260625-125553` | Pro | **38/50 (76%)** | **0.440** | Pro functional **低于** Flash；见 BENCHMARK_STATUS 对比表 |

**Pass 口径：** `functional_gate=1`（public+hidden+无 forbidden import）；**extraction 不影响 pass**。报告时需并列 high-extraction pass（ratio≥0.8）。

校准目标：Flash functional **~20–30%**（当前 82%，仍偏易）；强 Agent **~35–45%**。

Details, failure breakdown, and spec gaps: [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md).

## Difficulty (primary axis)

| Partition | Count | Location |
| --- | ---: | --- |
| **hard (main)** | 50 | `benchmark/tasks/` |
| easy + medium (smoke) | 3 | `benchmark/sanity/` |

All main-benchmark tasks are `difficulty=hard`. Smoke tasks are excluded from default `list_tasks.py` / suite analysis unless `--include-sanity` or `--root benchmark/sanity`.

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
| pygments / lark / attrs / werkzeug / typer / h11 / redis / faker / rich / marshmallow / babel / networkx / json5 / importlib-metadata | (see each task) | installed snapshot | (per task) |

## `entanglement.primary` distribution (50 hard)

| primary | count |
| --- | ---: |
| `parser_state_coupling` | 16 |
| `framework_coupling` | 12 |
| `data_model_coupling` | 6 |
| `legacy_vibe_clutter` | 6 |
| `config_environment_coupling` | 5 |
| `resource_coupling` | 4 |
| `third_party_dependency_coupling` | 1 |

26 unique source libraries across 50 tasks (~18 multi-task-repo slices).

## All tasks (50 hard + 3 smoke)

### Main benchmark (50 hard)

| task_id | primary | design note |
| --- | --- | --- |
| `attrs__validators_core__001` | `data_model_coupling` | [attrs__validators_core__001.md](task_designs/attrs__validators_core__001.md) |
| `babel__plural_core__001` | `third_party_dependency_coupling` | [babel__plural_core__001.md](task_designs/babel__plural_core__001.md) |
| `click__option_parser__001` | `framework_coupling` | [click__option_parser__001.md](task_designs/click__option_parser__001.md) |
| `coverage__config_merge_core__001` | `config_environment_coupling` | [coverage__config_merge_core__001.md](task_designs/coverage__config_merge_core__001.md) |
| `coverage__glob_matcher_core__001` | `resource_coupling` | [coverage__glob_matcher_core__001.md](task_designs/coverage__glob_matcher_core__001.md) |
| `coverage__path_remap_core__001` | `resource_coupling` | [coverage__path_remap_core__001.md](task_designs/coverage__path_remap_core__001.md) |
| `coverage__report_core__001` | `config_environment_coupling` | [coverage__report_core__001.md](task_designs/coverage__report_core__001.md) |
| `coverage__source_selection_core__001` | `config_environment_coupling` | [coverage__source_selection_core__001.md](task_designs/coverage__source_selection_core__001.md) |
| `faker__provider_core__001` | `resource_coupling` | [faker__provider_core__001.md](task_designs/faker__provider_core__001.md) |
| `h11__message_parse_core__001` | `parser_state_coupling` | [h11__message_parse_core__001.md](task_designs/h11__message_parse_core__001.md) |
| `importlib_metadata__entry_points_core__001` | `config_environment_coupling` | [importlib_metadata__entry_points_core__001.md](task_designs/importlib_metadata__entry_points_core__001.md) |
| `jinja2__compile_render_core__001` | `framework_coupling` | [jinja2__compile_render_core__001.md](task_designs/jinja2__compile_render_core__001.md) |
| `jinja2__extensions_core__001` | `framework_coupling` | [jinja2__extensions_core__001.md](task_designs/jinja2__extensions_core__001.md) |
| `jinja2__filters_tests_core__001` | `framework_coupling` | [jinja2__filters_tests_core__001.md](task_designs/jinja2__filters_tests_core__001.md) |
| `jinja2__lexer_parser_core__001` | `parser_state_coupling` | [jinja2__lexer_parser_core__001.md](task_designs/jinja2__lexer_parser_core__001.md) |
| `jinja2__loader_inheritance_core__001` | `framework_coupling` | [jinja2__loader_inheritance_core__001.md](task_designs/jinja2__loader_inheritance_core__001.md) |
| `json5__parse_core__001` | `parser_state_coupling` | [json5__parse_core__001.md](task_designs/json5__parse_core__001.md) |
| `jsonschema__validator_core__001` | `data_model_coupling` | [jsonschema__validator_core__001.md](task_designs/jsonschema__validator_core__001.md) |
| `lark__grammar_loader_core__001` | `resource_coupling` | [lark__grammar_loader_core__001.md](task_designs/lark__grammar_loader_core__001.md) |
| `lark__parse_tree_core__001` | `parser_state_coupling` | [lark__parse_tree_core__001.md](task_designs/lark__parse_tree_core__001.md) |
| `lark__visitor_transform_core__001` | `data_model_coupling` | [lark__visitor_transform_core__001.md](task_designs/lark__visitor_transform_core__001.md) |
| `markdown_it__commonmark_render__001` | `parser_state_coupling` | [markdown_it__commonmark_render__001.md](task_designs/markdown_it__commonmark_render__001.md) |
| `marshmallow__schema_core__001` | `data_model_coupling` | [marshmallow__schema_core__001.md](task_designs/marshmallow__schema_core__001.md) |
| `networkx__dag_topo_core__001` | `data_model_coupling` | [networkx__dag_topo_core__001.md](task_designs/networkx__dag_topo_core__001.md) |
| `packaging__requirement_marker_specifier__001` | `parser_state_coupling` | [packaging__requirement_marker_specifier__001.md](task_designs/packaging__requirement_marker_specifier__001.md) |
| `pluggy__hook_call_order__001` | `framework_coupling` | [pluggy__hook_call_order__001.md](task_designs/pluggy__hook_call_order__001.md) |
| `pluggy__hook_specs_core__001` | `framework_coupling` | [pluggy__hook_specs_core__001.md](task_designs/pluggy__hook_specs_core__001.md) |
| `pygments__formatter_core__001` | `parser_state_coupling` | [pygments__formatter_core__001.md](task_designs/pygments__formatter_core__001.md) |
| `pygments__lexer_core__001` | `parser_state_coupling` | [pygments__lexer_core__001.md](task_designs/pygments__lexer_core__001.md) |
| `pytest__fixture_resolve_core__001` | `framework_coupling` | [pytest__fixture_resolve_core__001.md](task_designs/pytest__fixture_resolve_core__001.md) |
| `pytest__ini_markers_core__001` | `config_environment_coupling` | [pytest__ini_markers_core__001.md](task_designs/pytest__ini_markers_core__001.md) |
| `pytest__mark_expression_core__001` | `parser_state_coupling` | [pytest__mark_expression_core__001.md](task_designs/pytest__mark_expression_core__001.md) |
| `pytest__skipif_eval_core__001` | `framework_coupling` | [pytest__skipif_eval_core__001.md](task_designs/pytest__skipif_eval_core__001.md) |
| `pyyaml__safe_load_dump__001` | `parser_state_coupling` | [pyyaml__safe_load_dump__001.md](task_designs/pyyaml__safe_load_dump__001.md) |
| `redis__resp_parser_core__001` | `parser_state_coupling` | [redis__resp_parser_core__001.md](task_designs/redis__resp_parser_core__001.md) |
| `rich__markup_parse_core__001` | `parser_state_coupling` | [rich__markup_parse_core__001.md](task_designs/rich__markup_parse_core__001.md) |
| `sqlparse__format_filters_core__001` | `parser_state_coupling` | [sqlparse__format_filters_core__001.md](task_designs/sqlparse__format_filters_core__001.md) |
| `sqlparse__parse_format_core__001` | `parser_state_coupling` | [sqlparse__parse_format_core__001.md](task_designs/sqlparse__parse_format_core__001.md) |
| `sqlparse__parse_split_core__001` | `parser_state_coupling` | [sqlparse__parse_split_core__001.md](task_designs/sqlparse__parse_split_core__001.md) |
| `sqlparse__token_tree_core__001` | `parser_state_coupling` | [sqlparse__token_tree_core__001.md](task_designs/sqlparse__token_tree_core__001.md) |
| `tomlkit__roundtrip_document__001` | `data_model_coupling` | [tomlkit__roundtrip_document__001.md](task_designs/tomlkit__roundtrip_document__001.md) |
| `typer__command_parser_core__001` | `framework_coupling` | [typer__command_parser_core__001.md](task_designs/typer__command_parser_core__001.md) |
| `vibe_app__csv_transform_core__001` | `legacy_vibe_clutter` | [vibe_app__csv_transform_core__001.md](task_designs/vibe_app__csv_transform_core__001.md) |
| `vibe_app__orm_query_ast_core__001` | `framework_coupling` | [vibe_app__orm_query_ast_core__001.md](task_designs/vibe_app__orm_query_ast_core__001.md) |
| `vibe_app__plugin_registry_core__001` | `legacy_vibe_clutter` | [vibe_app__plugin_registry_core__001.md](task_designs/vibe_app__plugin_registry_core__001.md) |
| `vibe_app__pricing_rules_core__001` | `legacy_vibe_clutter` | [vibe_app__pricing_rules_core__001.md](task_designs/vibe_app__pricing_rules_core__001.md) |
| `vibe_app__rules_engine_core__001` | `legacy_vibe_clutter` | [vibe_app__rules_engine_core__001.md](task_designs/vibe_app__rules_engine_core__001.md) |
| `vibe_app__session_registry_core__001` | `legacy_vibe_clutter` | [vibe_app__session_registry_core__001.md](task_designs/vibe_app__session_registry_core__001.md) |
| `vibe_app__yaml_config_bootstrap__001` | `legacy_vibe_clutter` | [vibe_app__yaml_config_bootstrap__001.md](task_designs/vibe_app__yaml_config_bootstrap__001.md) |
| `werkzeug__routing_core__001` | `framework_coupling` | [werkzeug__routing_core__001.md](task_designs/werkzeug__routing_core__001.md) |

### Smoke / appendix (`benchmark/sanity/`)

| task_id | difficulty | design note |
| --- | --- | --- |
| `iniconfig__parse_config__001` | easy | [iniconfig__parse_config__001.md](task_designs/iniconfig__parse_config__001.md) |
| `python_slugify__slugify_core__001` | medium | [python_slugify__slugify_core__001.md](task_designs/python_slugify__slugify_core__001.md) |
| `python_pathspec__gitignore_match__001` | medium | [python_pathspec__gitignore_match__001.md](task_designs/python_pathspec__gitignore_match__001.md) |

## Adding or removing tasks

1. Add or delete `benchmark/tasks/<task_id>/` with the [standard layout](TASK_FORMAT.md).
2. Run `featureliftbench validate-task benchmark/tasks/<task_id>/`.
3. Record oracle + [design note](task_designs/TEMPLATE.md) under `docs/task_designs/`.
4. Update this catalog table and pin-commit section if needed.

Do not introduce a second task root, schema, or scoring track for new tasks.
