# FeatureLiftBench Task Catalog

FeatureLiftBench is **one benchmark**: every task lives under `benchmark/tasks/<task_id>/`, uses the same `metadata.json` schema, the same evaluator, and the same scoring (`FunctionalGate` + `ExtractionRatio`). Tasks differ mainly in **`difficulty`**, **`entanglement`**, and **`feature`** scope—not in harness or rules.

**Current size:** **100 hard** tasks in `benchmark/tasks/` (main leaderboard) + **3 smoke** tasks in `benchmark/sanity/` (easy/medium appendix). `list_tasks.py` and `analyze_benchmark_suite.py` default to hard-only.

Benchmark evolution: **batch-0 frozen**; **batch-1** adds 50 tasks via staging to reach 100 hard. Policy: [EXPANSION.md](EXPANSION.md).

- **Concepts:** [CONCEPTS.md](CONCEPTS.md)
- **Benchmark spec:** [BENCHMARK_SPEC.md](BENCHMARK_SPEC.md)
- **Expansion / curation:** [EXPANSION.md](EXPANSION.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Task format:** [TASK_FORMAT.md](TASK_FORMAT.md)
- **Status & baselines:** [BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)
- **Experiment results:** [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md)
- **Design note template:** [task_designs/TEMPLATE.md](task_designs/TEMPLATE.md)

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
  --agent-docker \
  --eval-docker \
  --num-workers 1 \
  --output experiments/mini-swe-agent/<run_id>
```

`run-agent benchmark` or `run-agent benchmark/tasks` resolves to the current main leaderboard tasks by default.

### Multi-model profiles

Copy [`harness/config/agents.example.toml`](../harness/config/agents.example.toml) to `harness/config/agents.toml` (gitignored). Put API keys in `.env` (see [`.env.example`](../.env.example)).

| Profile | Model | `.env` keys |
| --- | --- | --- |
| `deepseek_v4_flash` | `deepseek/deepseek-v4-flash` | `FEATURELIFTBENCH_API_KEY`, `FEATURELIFTBENCH_API_BASE` |
| `deepseek_v4_pro` | `deepseek/deepseek-v4-pro` | 同上 |
| `gpt_oss_120b_vllm` | `openai/GPT-OSS-120B` | `VLLM_GPT_OSS_120B_API_KEY`, `VLLM_GPT_OSS_120B_API_BASE` |
| `qwen3_coder_30b_vllm` | `openai/Qwen3-Coder-30B-A3B-Instruct` | `VLLM_QWEN3_CODER_30B_*` |
| `glm_5_2` | `openai/zai-org/GLM-5.2` | `SILICONFLOW_API_KEY`, `SILICONFLOW_API_BASE` |
| `kimi_k2_7_code` | `openai/moonshotai/Kimi-K2.7-Code` | 同上 |
| `minimax_m2_5` | `openai/MiniMaxAI/MiniMax-M2.5` | 同上 |
| `nex_n2_pro` | `openai/nex-agi/Nex-N2-Pro` | 同上 |
| `qwen3_6_27b` | `openai/Qwen/Qwen3.6-27B` | 同上 |

Switch models with `--agent-profile` only (no need to edit base URL in `.env` between runs).

**Important:** `SILICONFLOW_API_BASE` must be `https://api.siliconflow.cn/v1` (not `/chat/completions`). Non-DeepSeek profiles need their own `*_API_BASE` env var so they are not overridden by `FEATURELIFTBENCH_API_BASE`.

**Quick commands:** root [`RUN.md`](../RUN.md) (vLLM + SiliconFlow). **Docker/resource boundary:** [SETUP.md](SETUP.md) §4. **Results:** [EXPERIMENT_RESULTS.md](EXPERIMENT_RESULTS.md).

Legacy baseline wrapper (historical 50-hard run ids remain in older experiment folders):

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 \
NUM_WORKERS=1 ./harness/scripts/run_baseline.sh deepseek_v4_flash benchmark-main-flash-001
```

For formal full-suite runs, use `NUM_WORKERS=1` plus agent/eval Docker boundaries:

```bash
FEATURELIFTBENCH_AGENT_DOCKER=1 FEATURELIFTBENCH_EVAL_DOCKER=1 NUM_WORKERS=1 ./run.sh
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

## Latest baseline

官方 DeepSeek Flash/Pro 数字与失败题分解 → **[BENCHMARK_STATUS.md](BENCHMARK_STATUS.md)** §Baseline。

| Run | Model | Functional pass |
| --- | --- | ---: |
| `benchmark-50-hard-flash-001` | Flash | **41/50 (82%)** |
| `benchmark-50-hard-pro-20260625-125553` | Pro | **42/50 (84%)** |

**Pass 口径：** `functional_gate=1`；extraction 不影响 pass。报告时并列 functional pass、avg `final_score`、high-extraction pass（≥0.8）、compact pass（≤0.25）。

**主榜规模：** batch-0 **50 hard** 冻结；batch-1 **+50 已完成**（主榜 **100 hard**）→ [EXPANSION.md](EXPANSION.md)。

## Difficulty (primary axis)

| Partition | Count | Location |
| --- | ---: | --- |
| **hard (main)** | 100 | `benchmark/tasks/` |
| easy + medium (smoke) | 3 | `benchmark/sanity/` |

All main-benchmark tasks are `difficulty=hard`. Smoke tasks are excluded from default `list_tasks.py` / suite analysis unless `--include-sanity` or `--root benchmark/sanity`.

## Task lineage (curation)

| Lineage | Count | Description |
| --- | ---: | --- |
| **Upstream OSS** | 93 | Pinned real open-source `repo/`; primary paper narrative (reuse from mature libraries) |
| **Curated vibe_app** | 7 | `benchmark/sources/vibe_app/`; simulates vibe-coded / legacy clutter—not a published PyPI package |

Policy: [EXPANSION.md](EXPANSION.md). New or replacement tasks must document **practical reuse** in `task_designs/<task_id>.md`.

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
| pygments / lark / attrs / werkzeug / typer / h11 / h2 / httpx / referencing / wsproto / redis / faker / rich / marshmallow / babel / networkx / json5 / importlib-metadata | (see each task) | installed snapshot | (per task) |
| httpx | https://github.com/encode/httpx | `326b9431c761e1ef1e00b9f760d1f654c8db48c6` | BSD-3-Clause |

## `entanglement.primary` distribution (100 hard)

| primary | count |
| --- | ---: |
| `parser_state_coupling` | 39 |
| `data_model_coupling` | 24 |
| `framework_coupling` | 13 |
| `config_environment_coupling` | 12 |
| `legacy_vibe_clutter` | 6 |
| `resource_coupling` | 5 |
| `third_party_dependency_coupling` | 1 |

75 unique source libraries across 100 tasks; multi-task repo slices include `coveragepy`, `jinja2`, `pytest`, `sqlparse`, `lark`, `pluggy`, and others.

## All tasks (100 hard + 3 smoke)

### Main benchmark (100 hard)

| task_id | primary | design note |
| --- | --- | --- |
| `arrow__parse_format_core__001` | `parser_state_coupling` | [arrow__parse_format_core__001.md](task_designs/arrow__parse_format_core__001.md) |
| `astroid__nodes_core__001` | `data_model_coupling` | [astroid__nodes_core__001.md](task_designs/astroid__nodes_core__001.md) |
| `attrs__validators_core__001` | `data_model_coupling` | [attrs__validators_core__001.md](task_designs/attrs__validators_core__001.md) |
| `babel__plural_core__001` | `third_party_dependency_coupling` | [babel__plural_core__001.md](task_designs/babel__plural_core__001.md) |
| `bleach__sanitize_core__001` | `parser_state_coupling` | [bleach__sanitize_core__001.md](task_designs/bleach__sanitize_core__001.md) |
| `bidict__bidirectional_map_core__001` | `data_model_coupling` | [bidict__bidirectional_map_core__001.md](task_designs/bidict__bidirectional_map_core__001.md) |
| `boltons__iterutils_core__001` | `data_model_coupling` | [boltons__iterutils_core__001.md](task_designs/boltons__iterutils_core__001.md) |
| `cachetools__cache_eviction_core__001` | `data_model_coupling` | [cachetools__cache_eviction_core__001.md](task_designs/cachetools__cache_eviction_core__001.md) |
| `cattrs__structure_core__001` | `data_model_coupling` | [cattrs__structure_core__001.md](task_designs/cattrs__structure_core__001.md) |
| `cerberus__schema_validate_core__001` | `data_model_coupling` | [cerberus__schema_validate_core__001.md](task_designs/cerberus__schema_validate_core__001.md) |
| `chameleon__template_compile_core__001` | `parser_state_coupling` | [chameleon__template_compile_core__001.md](task_designs/chameleon__template_compile_core__001.md) |
| `click__option_parser__001` | `framework_coupling` | [click__option_parser__001.md](task_designs/click__option_parser__001.md) |
| `coverage__config_merge_core__001` | `config_environment_coupling` | [coverage__config_merge_core__001.md](task_designs/coverage__config_merge_core__001.md) |
| `coverage__glob_matcher_core__001` | `resource_coupling` | [coverage__glob_matcher_core__001.md](task_designs/coverage__glob_matcher_core__001.md) |
| `coverage__path_remap_core__001` | `resource_coupling` | [coverage__path_remap_core__001.md](task_designs/coverage__path_remap_core__001.md) |
| `coverage__report_core__001` | `config_environment_coupling` | [coverage__report_core__001.md](task_designs/coverage__report_core__001.md) |
| `coverage__source_selection_core__001` | `config_environment_coupling` | [coverage__source_selection_core__001.md](task_designs/coverage__source_selection_core__001.md) |
| `configobj__roundtrip_config_core__001` | `config_environment_coupling` | [configobj__roundtrip_config_core__001.md](task_designs/configobj__roundtrip_config_core__001.md) |
| `croniter__cron_parse_core__001` | `parser_state_coupling` | [croniter__cron_parse_core__001.md](task_designs/croniter__cron_parse_core__001.md) |
| `dataclasses_json__serde_core__001` | `data_model_coupling` | [dataclasses_json__serde_core__001.md](task_designs/dataclasses_json__serde_core__001.md) |
| `deepdiff__deep_compare_core__001` | `data_model_coupling` | [deepdiff__deep_compare_core__001.md](task_designs/deepdiff__deep_compare_core__001.md) |
| `dynaconf__settings_merge_core__001` | `config_environment_coupling` | [dynaconf__settings_merge_core__001.md](task_designs/dynaconf__settings_merge_core__001.md) |
| `email_validator__validate_core__001` | `parser_state_coupling` | [email_validator__validate_core__001.md](task_designs/email_validator__validate_core__001.md) |
| `environs__typed_env_core__001` | `config_environment_coupling` | [environs__typed_env_core__001.md](task_designs/environs__typed_env_core__001.md) |
| `faker__provider_core__001` | `resource_coupling` | [faker__provider_core__001.md](task_designs/faker__provider_core__001.md) |
| `h11__message_parse_core__001` | `parser_state_coupling` | [h11__message_parse_core__001.md](task_designs/h11__message_parse_core__001.md) |
| `h2__frame_parse_core__001` | `parser_state_coupling` | [h2__frame_parse_core__001.md](task_designs/h2__frame_parse_core__001.md) |
| `httpx__request_model_core__001` | `data_model_coupling` | [httpx__request_model_core__001.md](task_designs/httpx__request_model_core__001.md) |
| `humanize__naturaltime_core__001` | `data_model_coupling` | [humanize__naturaltime_core__001.md](task_designs/humanize__naturaltime_core__001.md) |
| `importlib_metadata__entry_points_core__001` | `config_environment_coupling` | [importlib_metadata__entry_points_core__001.md](task_designs/importlib_metadata__entry_points_core__001.md) |
| `intervaltree__interval_tree_core__001` | `data_model_coupling` | [intervaltree__interval_tree_core__001.md](task_designs/intervaltree__interval_tree_core__001.md) |
| `isodate__duration_parse_core__001` | `parser_state_coupling` | [isodate__duration_parse_core__001.md](task_designs/isodate__duration_parse_core__001.md) |
| `jinja2__compile_render_core__001` | `framework_coupling` | [jinja2__compile_render_core__001.md](task_designs/jinja2__compile_render_core__001.md) |
| `jinja2__extensions_core__001` | `framework_coupling` | [jinja2__extensions_core__001.md](task_designs/jinja2__extensions_core__001.md) |
| `jinja2__filters_tests_core__001` | `framework_coupling` | [jinja2__filters_tests_core__001.md](task_designs/jinja2__filters_tests_core__001.md) |
| `jinja2__lexer_parser_core__001` | `parser_state_coupling` | [jinja2__lexer_parser_core__001.md](task_designs/jinja2__lexer_parser_core__001.md) |
| `jinja2__loader_inheritance_core__001` | `framework_coupling` | [jinja2__loader_inheritance_core__001.md](task_designs/jinja2__loader_inheritance_core__001.md) |
| `json5__parse_core__001` | `parser_state_coupling` | [json5__parse_core__001.md](task_designs/json5__parse_core__001.md) |
| `jsonpath_ng__expression_eval_core__001` | `parser_state_coupling` | [jsonpath_ng__expression_eval_core__001.md](task_designs/jsonpath_ng__expression_eval_core__001.md) |
| `jsonpointer__resolve_core__001` | `parser_state_coupling` | [jsonpointer__resolve_core__001.md](task_designs/jsonpointer__resolve_core__001.md) |
| `jsonschema__validator_core__001` | `data_model_coupling` | [jsonschema__validator_core__001.md](task_designs/jsonschema__validator_core__001.md) |
| `lark__grammar_loader_core__001` | `resource_coupling` | [lark__grammar_loader_core__001.md](task_designs/lark__grammar_loader_core__001.md) |
| `lark__parse_tree_core__001` | `parser_state_coupling` | [lark__parse_tree_core__001.md](task_designs/lark__parse_tree_core__001.md) |
| `lark__visitor_transform_core__001` | `data_model_coupling` | [lark__visitor_transform_core__001.md](task_designs/lark__visitor_transform_core__001.md) |
| `markdown_it__commonmark_render__001` | `parser_state_coupling` | [markdown_it__commonmark_render__001.md](task_designs/markdown_it__commonmark_render__001.md) |
| `markdown__extensions_core__001` | `parser_state_coupling` | [markdown__extensions_core__001.md](task_designs/markdown__extensions_core__001.md) |
| `mako__lexer_expression_core__001` | `parser_state_coupling` | [mako__lexer_expression_core__001.md](task_designs/mako__lexer_expression_core__001.md) |
| `msgpack__pack_unpack_core__001` | `parser_state_coupling` | [msgpack__pack_unpack_core__001.md](task_designs/msgpack__pack_unpack_core__001.md) |
| `marshmallow__schema_core__001` | `data_model_coupling` | [marshmallow__schema_core__001.md](task_designs/marshmallow__schema_core__001.md) |
| `networkx__dag_topo_core__001` | `data_model_coupling` | [networkx__dag_topo_core__001.md](task_designs/networkx__dag_topo_core__001.md) |
| `packaging__requirement_marker_specifier__001` | `parser_state_coupling` | [packaging__requirement_marker_specifier__001.md](task_designs/packaging__requirement_marker_specifier__001.md) |
| `parso__python_parse_core__001` | `parser_state_coupling` | [parso__python_parse_core__001.md](task_designs/parso__python_parse_core__001.md) |
| `passlib__hash_context_core__001` | `data_model_coupling` | [passlib__hash_context_core__001.md](task_designs/passlib__hash_context_core__001.md) |
| `pathvalidate__sanitize_core__001` | `config_environment_coupling` | [pathvalidate__sanitize_core__001.md](task_designs/pathvalidate__sanitize_core__001.md) |
| `pendulum__parse_format_core__001` | `parser_state_coupling` | [pendulum__parse_format_core__001.md](task_designs/pendulum__parse_format_core__001.md) |
| `phonenumbers__parse_format_core__001` | `resource_coupling` | [phonenumbers__parse_format_core__001.md](task_designs/phonenumbers__parse_format_core__001.md) |
| `pluggy__hook_call_order__001` | `framework_coupling` | [pluggy__hook_call_order__001.md](task_designs/pluggy__hook_call_order__001.md) |
| `pluggy__hook_specs_core__001` | `framework_coupling` | [pluggy__hook_specs_core__001.md](task_designs/pluggy__hook_specs_core__001.md) |
| `pygments__formatter_core__001` | `parser_state_coupling` | [pygments__formatter_core__001.md](task_designs/pygments__formatter_core__001.md) |
| `pygments__lexer_core__001` | `parser_state_coupling` | [pygments__lexer_core__001.md](task_designs/pygments__lexer_core__001.md) |
| `pydantic_v1__validation_error_core__001` | `framework_coupling` | [pydantic_v1__validation_error_core__001.md](task_designs/pydantic_v1__validation_error_core__001.md) |
| `pydantic_settings__env_source_core__001` | `config_environment_coupling` | [pydantic_settings__env_source_core__001.md](task_designs/pydantic_settings__env_source_core__001.md) |
| `python_dateutil__relativedelta_core__001` | `data_model_coupling` | [python_dateutil__relativedelta_core__001.md](task_designs/python_dateutil__relativedelta_core__001.md) |
| `python_dateutil__rrule_core__001` | `parser_state_coupling` | [python_dateutil__rrule_core__001.md](task_designs/python_dateutil__rrule_core__001.md) |
| `python_dotenv__env_parse_core__001` | `config_environment_coupling` | [python_dotenv__env_parse_core__001.md](task_designs/python_dotenv__env_parse_core__001.md) |
| `python_box__config_box_core__001` | `data_model_coupling` | [python_box__config_box_core__001.md](task_designs/python_box__config_box_core__001.md) |
| `python_frontmatter__roundtrip_core__001` | `parser_state_coupling` | [python_frontmatter__roundtrip_core__001.md](task_designs/python_frontmatter__roundtrip_core__001.md) |
| `python_multipart__form_parse_core__001` | `parser_state_coupling` | [python_multipart__form_parse_core__001.md](task_designs/python_multipart__form_parse_core__001.md) |
| `pytest__fixture_resolve_core__001` | `framework_coupling` | [pytest__fixture_resolve_core__001.md](task_designs/pytest__fixture_resolve_core__001.md) |
| `pytest__ini_markers_core__001` | `config_environment_coupling` | [pytest__ini_markers_core__001.md](task_designs/pytest__ini_markers_core__001.md) |
| `pytest__mark_expression_core__001` | `parser_state_coupling` | [pytest__mark_expression_core__001.md](task_designs/pytest__mark_expression_core__001.md) |
| `pytest__skipif_eval_core__001` | `framework_coupling` | [pytest__skipif_eval_core__001.md](task_designs/pytest__skipif_eval_core__001.md) |
| `pyyaml__safe_load_dump__001` | `parser_state_coupling` | [pyyaml__safe_load_dump__001.md](task_designs/pyyaml__safe_load_dump__001.md) |
| `redis__resp_parser_core__001` | `parser_state_coupling` | [redis__resp_parser_core__001.md](task_designs/redis__resp_parser_core__001.md) |
| `rfc3986__uri_parse_core__001` | `parser_state_coupling` | [rfc3986__uri_parse_core__001.md](task_designs/rfc3986__uri_parse_core__001.md) |
| `referencing__json_schema_refs_core__001` | `data_model_coupling` | [referencing__json_schema_refs_core__001.md](task_designs/referencing__json_schema_refs_core__001.md) |
| `rich__markup_parse_core__001` | `parser_state_coupling` | [rich__markup_parse_core__001.md](task_designs/rich__markup_parse_core__001.md) |
| `ruamel_yaml__roundtrip_core__001` | `parser_state_coupling` | [ruamel_yaml__roundtrip_core__001.md](task_designs/ruamel_yaml__roundtrip_core__001.md) |
| `sortedcontainers__sorted_list_core__001` | `data_model_coupling` | [sortedcontainers__sorted_list_core__001.md](task_designs/sortedcontainers__sorted_list_core__001.md) |
| `sqlparse__format_filters_core__001` | `parser_state_coupling` | [sqlparse__format_filters_core__001.md](task_designs/sqlparse__format_filters_core__001.md) |
| `sqlparse__parse_format_core__001` | `parser_state_coupling` | [sqlparse__parse_format_core__001.md](task_designs/sqlparse__parse_format_core__001.md) |
| `sqlparse__parse_split_core__001` | `parser_state_coupling` | [sqlparse__parse_split_core__001.md](task_designs/sqlparse__parse_split_core__001.md) |
| `sqlparse__token_tree_core__001` | `parser_state_coupling` | [sqlparse__token_tree_core__001.md](task_designs/sqlparse__token_tree_core__001.md) |
| `tabulate__table_format_core__001` | `data_model_coupling` | [tabulate__table_format_core__001.md](task_designs/tabulate__table_format_core__001.md) |
| `tomlkit__roundtrip_document__001` | `data_model_coupling` | [tomlkit__roundtrip_document__001.md](task_designs/tomlkit__roundtrip_document__001.md) |
| `typer__command_parser_core__001` | `framework_coupling` | [typer__command_parser_core__001.md](task_designs/typer__command_parser_core__001.md) |
| `urllib3__retry_backoff_core__001` | `config_environment_coupling` | [urllib3__retry_backoff_core__001.md](task_designs/urllib3__retry_backoff_core__001.md) |
| `voluptuous__schema_validate_core__001` | `data_model_coupling` | [voluptuous__schema_validate_core__001.md](task_designs/voluptuous__schema_validate_core__001.md) |
| `vibe_app__csv_transform_core__001` | `legacy_vibe_clutter` | [vibe_app__csv_transform_core__001.md](task_designs/vibe_app__csv_transform_core__001.md) |
| `vibe_app__orm_query_ast_core__001` | `framework_coupling` | [vibe_app__orm_query_ast_core__001.md](task_designs/vibe_app__orm_query_ast_core__001.md) |
| `vibe_app__plugin_registry_core__001` | `legacy_vibe_clutter` | [vibe_app__plugin_registry_core__001.md](task_designs/vibe_app__plugin_registry_core__001.md) |
| `vibe_app__pricing_rules_core__001` | `legacy_vibe_clutter` | [vibe_app__pricing_rules_core__001.md](task_designs/vibe_app__pricing_rules_core__001.md) |
| `vibe_app__rules_engine_core__001` | `legacy_vibe_clutter` | [vibe_app__rules_engine_core__001.md](task_designs/vibe_app__rules_engine_core__001.md) |
| `vibe_app__session_registry_core__001` | `legacy_vibe_clutter` | [vibe_app__session_registry_core__001.md](task_designs/vibe_app__session_registry_core__001.md) |
| `vibe_app__yaml_config_bootstrap__001` | `legacy_vibe_clutter` | [vibe_app__yaml_config_bootstrap__001.md](task_designs/vibe_app__yaml_config_bootstrap__001.md) |
| `websockets__handshake_parse_core__001` | `parser_state_coupling` | [websockets__handshake_parse_core__001.md](task_designs/websockets__handshake_parse_core__001.md) |
| `wsproto__frame_parse_core__001` | `parser_state_coupling` | [wsproto__frame_parse_core__001.md](task_designs/wsproto__frame_parse_core__001.md) |
| `xmltodict__xml_parse_core__001` | `parser_state_coupling` | [xmltodict__xml_parse_core__001.md](task_designs/xmltodict__xml_parse_core__001.md) |
| `yarl__url_model_core__001` | `parser_state_coupling` | [yarl__url_model_core__001.md](task_designs/yarl__url_model_core__001.md) |
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
