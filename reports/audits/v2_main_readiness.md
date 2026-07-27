# Python-150 v2 Main Readiness Audit

**Overall verdict:** `pass`  
**Policy:** `featureliftbench.full_repository_no_hint_main.v2`  
**Generated:** 2026-07-26T14:52:02+00:00

## Acceptance decision

- Retain as v1 engineering/spec pool: **150/150**.
- No-Hint workspace pass: **150/150**.
- Canonical source mapping: **150/150**.
- Admit to v2 Full-Repository / No-Hint Main now: **150/150**.
- Reject for a demonstrated task defect: **0/150**.

All 150 retained task definitions now satisfy the v2 source, contract, No-Hint, Oracle/isolation, compactness and freeze gates. Historical v1 results remain a separate evidence version.

## Eight principles

| Principle | Pass | Partial | Pending | Fail |
| --- | ---: | ---: | ---: | ---: |
| 1. Full-Repository input | 150 | 0 | 0 | 0 |
| 2. Complete public contract | 150 | 0 | 0 | 0 |
| 3. No source-location hints | 150 | 0 | 0 | 0 |
| 4. Autonomous workflow | 150 | 0 | 0 | 0 |
| 5. Independent submission | 150 | 0 | 0 | 0 |
| 6. Functional Pass@1 primary | 150 | 0 | 0 | 0 |
| 7. Reference-relative compactness | 150 | 0 | 0 | 0 |
| 8. Explicit frozen conditions | 150 | 0 | 0 | 0 |

## Main blockers

| Blocker | Tasks |
| --- | ---: |
| none | 0 |

## Canonical source status

| Registry source status | Tasks | Meaning |
| --- | ---: | --- |
| `ready` | 150 | Canonical full source evidence complete. |

## Evidence boundary

- Legacy spec freeze: `f7c616edb47ea533`.
- Legacy Oracle freeze: `7c042d5528b7d0fd`.
- Those freezes prove the mixed-snapshot v1 task/evaluator state, not the post-migration v2 source context.
- Active v2 benchmark freeze: `bbbd01c81638586c360efacbaa37b52d5ae8e6dd3b183dc5e824f5f562c8e751`.
- Functional Pass@1 and reference-relative compactness are implemented as separate metrics.
- Current `hard` labels are design labels; empirical difficulty should be recalibrated after the first frozen v2 baseline.

## Per-task verdicts

| Task | Source kind | Source status | Contract | No-Hint | v2 Oracle/isolation | Compactness | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `aiohttp__url_params_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `alembic__revision_map_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `apscheduler__cron_trigger_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `arrow__parse_format_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `astroid__nodes_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `attrs__validators_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `babel__plural_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `bidict__bidirectional_map_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `bleach__sanitize_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `boltons__iterutils_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `build__pyproject_backend_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `cachetools__cache_eviction_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `cattrs__structure_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `celery__signal_dispatch_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `cerberus__schema_validate_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `chameleon__template_compile_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `click__lazy_command_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `click__option_parser__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `configobj__roundtrip_config_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `cookiecutter__repo_finder_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `coverage__config_merge_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `coverage__glob_matcher_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `coverage__path_remap_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `coverage__report_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `coverage__source_selection_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `croniter__cron_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `dataclasses_json__serde_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `dateutil__zone_resolver_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `deepdiff__deep_compare_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `diskcache__eviction_policy_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `distlib__wheel_metadata_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `dynaconf__settings_merge_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `email_validator__validate_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `environs__typed_env_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `faker__provider_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `flake8__plugin_options_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `fs__url_opener_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `fsspec__url_chain_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `glom__spec_eval_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `h11__message_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `h2__frame_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `hatch__project_metadata_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `httpx__request_model_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `humanize__naturaltime_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `importlib_metadata__entry_points_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `importlib_resources__traversable_tree_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `installer__wheel_record_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `intervaltree__interval_tree_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `isodate__duration_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `isort__settings_resolver_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jinja2__compile_render_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jinja2__extensions_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jinja2__filters_tests_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jinja2__lexer_parser_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jinja2__loader_inheritance_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `json5__parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `json_logic__evaluator_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jsonpath_ng__expression_eval_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jsonpointer__resolve_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jsonschema__validator_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jupyter_core__paths_resolver_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `jupyter_server__extension_config_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `keyring__backend_select_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `lark__grammar_loader_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `lark__parse_tree_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `lark__visitor_transform_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `license_expression__policy_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `mako__lexer_expression_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `markdown__extensions_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `markdown_it__commonmark_render__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `marshmallow__schema_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `mkdocs__plugin_config_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `msgpack__pack_unpack_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `multidict__multidict_mutation_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `networkx__dag_topo_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `packaging__requirement_marker_specifier__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `parsel__selector_namespace_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `parso__python_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `passlib__hash_context_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pathvalidate__sanitize_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pendulum__parse_format_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `phonenumbers__parse_format_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `platformdirs__app_dirs_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pluggy__hook_call_order__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pluggy__hook_specs_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pluggy__hook_wrapper_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `poetry_core__dependency_groups_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pydantic__field_validator_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pydantic_settings__env_source_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pydantic_v1__validation_error_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pygments__formatter_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pygments__lexer_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pyramid__configurator_action_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pytest__fixture_resolve_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pytest__ini_markers_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pytest__mark_expression_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pytest__marker_registry_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pytest__skipif_eval_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `python_box__config_box_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `python_dateutil__relativedelta_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `python_dateutil__rrule_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `python_dotenv__env_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `python_frontmatter__roundtrip_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `python_multipart__form_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `pyyaml__safe_load_dump__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `readme_renderer__content_type_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `redis__resp_parser_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `referencing__json_schema_refs_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `requests_cache__cache_key_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `responses__request_matcher_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `returns__result_pipeline_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `rfc3986__uri_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `rich__markup_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `ruamel_yaml__roundtrip_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `schema__nested_validate_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `scrapy__item_loader_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `setuptools_scm__version_normalize_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `sortedcontainers__sorted_list_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `sphinx__extension_registry_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `sqlalchemy__event_dispatch_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `sqlparse__format_filters_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `sqlparse__parse_format_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `sqlparse__parse_split_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `sqlparse__token_tree_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `starlette__route_matching_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `stevedore__extension_manager_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `tabulate__table_format_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `tenacity__retry_state_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `tomlkit__roundtrip_document__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `tox__factor_expression_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `trafaret__validation_rules_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `transitions__state_machine_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `typer__command_parser_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `urllib3__retry_backoff_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `vibe_app__csv_transform_core__001` | curated | `ready` | pass | pass | pass | pass | `pass` |
| `vibe_app__orm_query_ast_core__001` | curated | `ready` | pass | pass | pass | pass | `pass` |
| `vibe_app__plugin_registry_core__001` | curated | `ready` | pass | pass | pass | pass | `pass` |
| `vibe_app__pricing_rules_core__001` | curated | `ready` | pass | pass | pass | pass | `pass` |
| `vibe_app__rules_engine_core__001` | curated | `ready` | pass | pass | pass | pass | `pass` |
| `vibe_app__session_registry_core__001` | curated | `ready` | pass | pass | pass | pass | `pass` |
| `vibe_app__yaml_config_bootstrap__001` | curated | `ready` | pass | pass | pass | pass | `pass` |
| `virtualenv__interpreter_spec_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `voluptuous__schema_validate_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `websockets__handshake_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `werkzeug__routing_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `wheel__metadata_normalize_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `wsproto__frame_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `xmltodict__xml_parse_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `yamale__schema_validate_core__hard3_001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |
| `yarl__url_model_core__001` | external_oss | `ready` | pass | pass | pass | pass | `pass` |

## Next operational steps

1. Run the Full-Repository / No-Hint Python-150 model baseline against the active freeze.
2. Report evaluator Functional Pass@1 separately from Agent completion and process failures.
3. Generate reference-relative compactness, token, step, latency and failure analyses.
4. Recalibrate empirical difficulty after the frozen baseline.
