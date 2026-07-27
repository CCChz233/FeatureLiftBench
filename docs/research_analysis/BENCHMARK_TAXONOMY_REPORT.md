# FeatureLiftBench Python-150 Benchmark Taxonomy Report

- Taxonomy version: `v2`
- Task-level rows: **150**
- Evidence boundary: metadata, oracle manifests, source snapshots, public tests, hidden tests.
- Explicitly excluded: trajectories, submissions, evaluation results, and historical pass/fail labels.
- Generated from: `artifacts/research_analysis/python150_task_taxonomy.csv`
- Audit invariant errors: **0**

## Repository archetype

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `library` | 102 | 68.0% |
| `developer_tooling` | 29 | 19.3% |
| `framework_plugin` | 17 | 11.3% |
| `application_service` | 2 | 1.3% |

## Repository provenance

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `real_oss_mature` | 150 | 100.0% |
| `curated_vibe` | 0 | 0.0% |
| `real_oss_legacy` | 0 | 0.0% |

`real_oss_legacy` is empty in v2 because project age/maintenance is not inferable from the local task package. The label is reserved for future tasks carrying explicit provenance evidence.

## Repository domain

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `parsing` | 41 | 27.3% |
| `general_utility` | 38 | 25.3% |
| `configuration` | 15 | 10.0% |
| `data_modeling` | 13 | 8.7% |
| `networking` | 12 | 8.0% |
| `packaging` | 11 | 7.3% |
| `testing` | 11 | 7.3% |
| `application` | 9 | 6.0% |

## Feature family

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `parse_tokenize_decode` | 31 | 20.7% |
| `registry_plugin_dispatch` | 22 | 14.7% |
| `serialize_format_render` | 19 | 12.7% |
| `config_resolve_discover` | 18 | 12.0% |
| `validate_normalize_construct` | 15 | 10.0% |
| `resource_metadata_loading` | 12 | 8.0% |
| `algorithm_data_structure` | 11 | 7.3% |
| `protocol_state_transition` | 9 | 6.0% |
| `cache_retry_policy` | 8 | 5.3% |
| `workflow_session_orchestration` | 5 | 3.3% |

## Feature statefulness

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `local_state` | 53 | 35.3% |
| `stateless` | 42 | 28.0% |
| `lifecycle_state` | 40 | 26.7% |
| `session_state` | 11 | 7.3% |
| `global_state` | 4 | 2.7% |

## Normalized entanglement mechanisms (multi-label)

Percentages use all 150 tasks as denominator and therefore sum above 100%.

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `static_transitive_dependency` | 123 | 82.0% |
| `data_model_invariant` | 98 | 65.3% |
| `implicit_runtime_dependency` | 93 | 62.0% |
| `parser_state` | 64 | 42.7% |
| `dynamic_import_plugin` | 51 | 34.0% |
| `framework_lifecycle` | 44 | 29.3% |
| `config_environment` | 33 | 22.0% |
| `resource_packaging` | 24 | 16.0% |
| `third_party_contract` | 18 | 12.0% |
| `global_state_registry` | 15 | 10.0% |

## Behavioral hidden-risk tags (multi-label)

Tags are deterministic lexical/AST audits of hidden tests; they describe tested contract dimensions, not outcomes.

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `boundary_cases` | 130 | 86.7% |
| `exception_semantics` | 92 | 61.3% |
| `lifecycle_semantics` | 41 | 27.3% |
| `mutation_side_effects` | 34 | 22.7% |
| `ordering_semantics` | 33 | 22.0% |
| `platform_variation` | 10 | 6.7% |

## Codebase condition tags (multi-label)

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `weak_module_boundaries` | 53 | 35.3% |
| `dead_code_distractors` | 1 | 0.7% |
| `duplicated_implementation` | 0 | 0.0% |
| `generated_code` | 0 | 0.0% |
| `legacy_clutter` | 0 | 0.0% |

## Repository archetype × feature family

| repo_archetype_primary | `algorithm_data_structure` | `cache_retry_policy` | `config_resolve_discover` | `parse_tokenize_decode` | `protocol_state_transition` | `registry_plugin_dispatch` | `resource_metadata_loading` | `serialize_format_render` | `validate_normalize_construct` | `workflow_session_orchestration` | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `application_service` | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| `developer_tooling` | 1 | 1 | 8 | 5 | 0 | 5 | 6 | 2 | 1 | 0 | 29 |
| `framework_plugin` | 0 | 0 | 0 | 1 | 0 | 12 | 1 | 2 | 0 | 1 | 17 |
| `library` | 10 | 7 | 10 | 25 | 9 | 3 | 5 | 15 | 14 | 4 | 102 |

## Feature family × entanglement mechanism

| feature_family_primary | `config_environment` | `data_model_invariant` | `dynamic_import_plugin` | `framework_lifecycle` | `global_state_registry` | `implicit_runtime_dependency` | `parser_state` | `resource_packaging` | `static_transitive_dependency` | `third_party_contract` | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `algorithm_data_structure` | 0 | 11 | 2 | 0 | 0 | 8 | 5 | 0 | 9 | 1 | 11 |
| `cache_retry_policy` | 2 | 6 | 0 | 1 | 1 | 5 | 3 | 2 | 5 | 2 | 8 |
| `config_resolve_discover` | 15 | 5 | 7 | 3 | 2 | 10 | 3 | 7 | 15 | 2 | 18 |
| `parse_tokenize_decode` | 2 | 23 | 10 | 5 | 1 | 20 | 27 | 3 | 27 | 4 | 31 |
| `protocol_state_transition` | 1 | 5 | 1 | 0 | 1 | 8 | 8 | 1 | 7 | 0 | 9 |
| `registry_plugin_dispatch` | 3 | 7 | 15 | 20 | 6 | 10 | 1 | 1 | 19 | 3 | 22 |
| `resource_metadata_loading` | 3 | 9 | 7 | 1 | 1 | 5 | 3 | 7 | 10 | 1 | 12 |
| `serialize_format_render` | 3 | 16 | 6 | 7 | 0 | 13 | 10 | 2 | 17 | 3 | 19 |
| `validate_normalize_construct` | 3 | 14 | 3 | 4 | 3 | 11 | 4 | 0 | 12 | 1 | 15 |
| `workflow_session_orchestration` | 1 | 2 | 0 | 3 | 0 | 3 | 0 | 1 | 2 | 1 | 5 |

## Core100 × Hard50

| split | `algorithm_data_structure` | `cache_retry_policy` | `config_resolve_discover` | `parse_tokenize_decode` | `protocol_state_transition` | `registry_plugin_dispatch` | `resource_metadata_loading` | `serialize_format_render` | `validate_normalize_construct` | `workflow_session_orchestration` | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `core100` | 8 | 4 | 13 | 27 | 7 | 7 | 4 | 18 | 9 | 3 | 100 |
| `hard50` | 3 | 4 | 5 | 4 | 2 | 15 | 8 | 1 | 6 | 2 | 50 |

### Split totals

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `core100` | 100 | 66.7% |
| `hard50` | 50 | 33.3% |

Hard50 is not a scaled copy of Core100: registry/plugin features are 15/50 in Hard50 versus 7/100 in Core100, while parse/tokenize features are 4/50 versus 26/100. Any aggregate comparison must therefore report split- and feature-stratified results.

## Source repository concentration

There are **127** unique upstream source groups.

| Source repo | Tasks | Share |
|---|---:|---:|
| `coveragepy` | 5 | 3.3% |
| `jinja2` | 5 | 3.3% |
| `pytest` | 5 | 3.3% |
| `sqlparse` | 4 | 2.7% |
| `lark` | 3 | 2.0% |
| `pluggy` | 3 | 2.0% |
| `click` | 2 | 1.3% |
| `pydantic` | 2 | 1.3% |
| `pygments` | 2 | 1.3% |
| `python-dateutil` | 2 | 1.3% |
| `Faker` | 1 | 0.7% |
| `Markdown` | 1 | 0.7% |
| `PyYAML` | 1 | 0.7% |
| `aiohttp` | 1 | 0.7% |
| `alembic` | 1 | 0.7% |
| `apscheduler` | 1 | 0.7% |
| `arrow` | 1 | 0.7% |
| `astroid` | 1 | 0.7% |
| `attrs` | 1 | 0.7% |
| `babel` | 1 | 0.7% |
| `bidict` | 1 | 0.7% |
| `bleach` | 1 | 0.7% |
| `blinker` | 1 | 0.7% |
| `boltons` | 1 | 0.7% |
| `build` | 1 | 0.7% |
| `cachetools` | 1 | 0.7% |
| `cattrs` | 1 | 0.7% |
| `celery` | 1 | 0.7% |
| `cerberus` | 1 | 0.7% |
| `chameleon` | 1 | 0.7% |
| `configobj` | 1 | 0.7% |
| `cookiecutter` | 1 | 0.7% |
| `croniter` | 1 | 0.7% |
| `dataclasses-json` | 1 | 0.7% |
| `dateutil` | 1 | 0.7% |
| `decorator` | 1 | 0.7% |
| `deepdiff` | 1 | 0.7% |
| `diskcache` | 1 | 0.7% |
| `distlib` | 1 | 0.7% |
| `dynaconf` | 1 | 0.7% |
| `email-validator` | 1 | 0.7% |
| `environs` | 1 | 0.7% |
| `filelock` | 1 | 0.7% |
| `flake8` | 1 | 0.7% |
| `flask` | 1 | 0.7% |
| `fs` | 1 | 0.7% |
| `fsspec` | 1 | 0.7% |
| `glom` | 1 | 0.7% |
| `h11` | 1 | 0.7% |
| `h2` | 1 | 0.7% |
| `hatch` | 1 | 0.7% |
| `httpx` | 1 | 0.7% |
| `humanize` | 1 | 0.7% |
| `importlib_metadata` | 1 | 0.7% |
| `importlib_resources` | 1 | 0.7% |
| `installer` | 1 | 0.7% |
| `intervaltree` | 1 | 0.7% |
| `isodate` | 1 | 0.7% |
| `isort` | 1 | 0.7% |
| `itsdangerous` | 1 | 0.7% |
| `json5` | 1 | 0.7% |
| `json_logic` | 1 | 0.7% |
| `jsonpath-ng` | 1 | 0.7% |
| `jsonpointer` | 1 | 0.7% |
| `jsonschema` | 1 | 0.7% |
| `jupyter_core` | 1 | 0.7% |
| `jupyter_server` | 1 | 0.7% |
| `keyring` | 1 | 0.7% |
| `license_expression` | 1 | 0.7% |
| `mako` | 1 | 0.7% |
| `markdown-it-py` | 1 | 0.7% |
| `marshmallow` | 1 | 0.7% |
| `mkdocs` | 1 | 0.7% |
| `msgpack-python` | 1 | 0.7% |
| `multidict` | 1 | 0.7% |
| `networkx` | 1 | 0.7% |
| `packaging` | 1 | 0.7% |
| `parse` | 1 | 0.7% |
| `parsel` | 1 | 0.7% |
| `parso` | 1 | 0.7% |
| `passlib` | 1 | 0.7% |
| `pathvalidate` | 1 | 0.7% |
| `pendulum` | 1 | 0.7% |
| `phonenumbers` | 1 | 0.7% |
| `platformdirs` | 1 | 0.7% |
| `poetry_core` | 1 | 0.7% |
| `pydantic-settings` | 1 | 0.7% |
| `pyramid` | 1 | 0.7% |
| `python-box` | 1 | 0.7% |
| `python-decouple` | 1 | 0.7% |
| `python-dotenv` | 1 | 0.7% |
| `python-frontmatter` | 1 | 0.7% |
| `python-multipart` | 1 | 0.7% |
| `readme_renderer` | 1 | 0.7% |
| `redis` | 1 | 0.7% |
| `referencing` | 1 | 0.7% |
| `requests_cache` | 1 | 0.7% |
| `responses` | 1 | 0.7% |
| `returns` | 1 | 0.7% |
| `rfc3986` | 1 | 0.7% |
| `rich` | 1 | 0.7% |
| `ruamel.yaml` | 1 | 0.7% |
| `schema` | 1 | 0.7% |
| `scrapy` | 1 | 0.7% |
| `setuptools_scm` | 1 | 0.7% |
| `sortedcontainers` | 1 | 0.7% |
| `sphinx` | 1 | 0.7% |
| `sqlalchemy` | 1 | 0.7% |
| `starlette` | 1 | 0.7% |
| `stevedore` | 1 | 0.7% |
| `tabulate` | 1 | 0.7% |
| `tenacity` | 1 | 0.7% |
| `tomlkit` | 1 | 0.7% |
| `tox` | 1 | 0.7% |
| `trafaret` | 1 | 0.7% |
| `transitions` | 1 | 0.7% |
| `typer` | 1 | 0.7% |
| `urllib3` | 1 | 0.7% |
| `virtualenv` | 1 | 0.7% |
| `voluptuous` | 1 | 0.7% |
| `websockets` | 1 | 0.7% |
| `werkzeug` | 1 | 0.7% |
| `wheel` | 1 | 0.7% |
| `wsproto` | 1 | 0.7% |
| `xmltodict` | 1 | 0.7% |
| `yamale` | 1 | 0.7% |
| `yarl` | 1 | 0.7% |

## Static closure depth

Depth is the maximum shortest import path from located source entrypoint files, bounded by the explicit oracle source-file set when present. `NA` means entrypoints or reference closure could not be located reliably.

| 类别 | 任务数 | 占比 |
|---|---:|---:|
| `shallow_0_1` | 96 | 64.0% |
| `medium_2` | 32 | 21.3% |
| `deep_3_plus` | 22 | 14.7% |

## Dynamic import, global state, registry, and lifecycle signals

| Signal | true | false | NA |
|---|---:|---:|---:|
| `has_dynamic_import` | 50 | 100 | 0 |
| `has_global_state` | 52 | 98 | 0 |
| `has_registry` | 89 | 61 | 0 |
| `has_framework_lifecycle` | 58 | 92 | 0 |

## Sparse and imbalanced categories

A category with fewer than five tasks must not support a standalone performance claim.

| Field | Category | N | Allowed use |
|---|---|---:|---|
| `codebase_condition_tags` | `dead_code_distractors` | 1 | descriptive only |
| `codebase_condition_tags` | `duplicated_implementation` | 0 | descriptive only |
| `codebase_condition_tags` | `generated_code` | 0 | descriptive only |
| `codebase_condition_tags` | `legacy_clutter` | 0 | descriptive only |
| `repo_archetype_primary` | `application_service` | 2 | descriptive only |
| `repo_provenance` | `curated_vibe` | 0 | descriptive only |
| `repo_provenance` | `real_oss_legacy` | 0 | descriptive only |

The dominant feature family is `parse_tokenize_decode` (31/150); the dominant repository domain is `parsing` (41/150).
10 source repositories contribute more than one task. The largest single source contributes 5/150 tasks, below 5% but not independent for uncertainty estimates.
Paper-scale comparisons should cluster uncertainty by `source_group_id` and report source-disjoint sensitivity.

## Near-duplicate candidates

This is a conservative review queue: same source repository and same primary feature family. It does not assert semantic duplication.

| Candidate cluster | Tasks |
|---|---|
| `coveragepy / config_resolve_discover` | `coverage__config_merge_core__001`, `coverage__glob_matcher_core__001`, `coverage__path_remap_core__001`, `coverage__source_selection_core__001` |
| `jinja2 / serialize_format_render` | `jinja2__compile_render_core__001`, `jinja2__filters_tests_core__001` |
| `pluggy / registry_plugin_dispatch` | `pluggy__hook_call_order__001`, `pluggy__hook_specs_core__001`, `pluggy__hook_wrapper_core__hard3_001` |
| `pydantic / validate_normalize_construct` | `pydantic__field_validator_core__hard3_001`, `pydantic_v1__validation_error_core__001` |
| `pytest / registry_plugin_dispatch` | `pytest__fixture_resolve_core__001`, `pytest__marker_registry_core__hard3_001` |
| `sqlparse / parse_tokenize_decode` | `sqlparse__parse_format_core__001`, `sqlparse__parse_split_core__001`, `sqlparse__token_tree_core__001` |

## Review status

- reviewed without unresolved taxonomy ambiguity: **150**
- `needs_review`: **0**

The following tasks have cross-family/domain ambiguity. Their provisional labels are usable for pilot stratification but must be adjudicated before making a narrow per-category paper claim:


## Statistical-use guidance

- Categories with `N >= 5` may support descriptive slices; confirmatory method comparisons still require enough runs per arm and source-clustered uncertainty.
- Categories with `N < 5` are descriptive only and must be pooled into a preregistered broader mechanism for tests.
- Multi-label mechanism counts are not mutually exclusive; do not use a naive chi-square table that treats them as such.
- The 10-task pilot is mechanism-finding and cannot support population-level performance claims.
- Outcome fields must be joined later by `task_id`; they must never be copied into this taxonomy table.

## Missing measurements

| Field | NA rows | Reason |
|---|---:|---|
| `reference_file_count` | 28 | no explicit reliable evidence; not imputed |
| `reference_symbol_count` | 101 | no explicit reliable evidence; not imputed |
| `reference_loc` | 28 | no explicit reliable evidence; not imputed |
| `direct_internal_dependency_count` | 0 | no explicit reliable evidence; not imputed |
| `transitive_internal_dependency_count` | 0 | no explicit reliable evidence; not imputed |
| `external_dependency_count` | 0 | no explicit reliable evidence; not imputed |
| `static_file_closure_depth` | 0 | no explicit reliable evidence; not imputed |
| `resource_file_count` | 28 | no explicit reliable evidence; not imputed |
| `adapter_required` | 148 | no explicit reliable evidence; not imputed |

## Reproduction

```bash
python3 tools/research_analysis/build_benchmark_taxonomy.py --strict
```
