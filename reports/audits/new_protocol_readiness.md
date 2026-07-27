# Test-Blind Task Content Readiness Audit

> Contract/test-blindness sub-audit only. The current v2 release decision is `reports/audits/v2_main_readiness.md`.

Protocol: complete generated TASK + canonical pinned source workspace; all benchmark-authored evaluator tests hidden until one-shot submission.

Scope note: this audit checks task content and test blindness; it does not certify Full-Repository source materialization or source digests.

## Summary

| Gate | Ready |
| --- | ---: |
| Engineering package/spec | 150/150 |
| Complete non-generic contract | 150/150 |
| Experiment-ready content | 150/150 |
| Upstream tests available in `repo/` (informational) | 48/150 |
| Task content ready (source scope excluded) | 150/150 |

## Issue Counts

| Issue | Tasks |
| --- | ---: |

## Per-task Queue

| Task | Repo files | Upstream tests | Contract | Issues |
| --- | ---: | ---: | --- | --- |
| `aiohttp__url_params_core__hard3_001` | 4 | 0 | ready | — |
| `alembic__revision_map_core__hard3_001` | 7 | 0 | ready | — |
| `apscheduler__cron_trigger_core__hard3_001` | 7 | 0 | ready | — |
| `arrow__parse_format_core__001` | 11 | 0 | ready | — |
| `astroid__nodes_core__001` | 155 | 1 | ready | — |
| `attrs__validators_core__001` | 32 | 0 | ready | — |
| `babel__plural_core__001` | 828 | 0 | ready | — |
| `bidict__bidirectional_map_core__001` | 86 | 3 | ready | — |
| `bleach__sanitize_core__001` | 94 | 0 | ready | — |
| `boltons__iterutils_core__001` | 9 | 0 | ready | — |
| `build__pyproject_backend_core__hard3_001` | 6 | 0 | ready | — |
| `cachetools__cache_eviction_core__001` | 43 | 14 | ready | — |
| `cattrs__structure_core__001` | 142 | 43 | ready | — |
| `celery__signal_dispatch_core__hard3_001` | 6 | 0 | ready | — |
| `cerberus__schema_validate_core__001` | 65 | 13 | ready | — |
| `chameleon__template_compile_core__001` | 31 | 0 | ready | — |
| `click__lazy_command_core__hard3_001` | 4 | 0 | ready | — |
| `click__option_parser__001` | 33 | 0 | ready | — |
| `configobj__roundtrip_config_core__001` | 12 | 8 | ready | — |
| `cookiecutter__repo_finder_core__hard3_001` | 4 | 0 | ready | — |
| `coverage__config_merge_core__001` | 404 | 197 | ready | — |
| `coverage__glob_matcher_core__001` | 404 | 197 | ready | — |
| `coverage__path_remap_core__001` | 404 | 197 | ready | — |
| `coverage__report_core__001` | 404 | 197 | ready | — |
| `coverage__source_selection_core__001` | 404 | 197 | ready | — |
| `croniter__cron_parse_core__001` | 10 | 7 | ready | — |
| `dataclasses_json__serde_core__001` | 51 | 30 | ready | — |
| `dateutil__zone_resolver_core__hard3_001` | 4 | 0 | ready | — |
| `deepdiff__deep_compare_core__001` | 51 | 0 | ready | — |
| `diskcache__eviction_policy_core__hard3_001` | 4 | 0 | ready | — |
| `distlib__wheel_metadata_core__hard3_001` | 8 | 0 | ready | — |
| `dynaconf__settings_merge_core__001` | 136 | 1 | ready | — |
| `email_validator__validate_core__001` | 28 | 7 | ready | — |
| `environs__typed_env_core__001` | 31 | 6 | ready | — |
| `faker__provider_core__001` | 727 | 0 | ready | — |
| `flake8__plugin_options_core__hard3_001` | 8 | 0 | ready | — |
| `fs__url_opener_core__hard3_001` | 5 | 0 | ready | — |
| `fsspec__url_chain_core__hard3_001` | 4 | 0 | ready | — |
| `glom__spec_eval_core__hard3_001` | 4 | 0 | ready | — |
| `h11__message_parse_core__001` | 46 | 23 | ready | — |
| `h2__frame_parse_core__001` | 18 | 0 | ready | — |
| `hatch__project_metadata_core__hard3_001` | 3 | 0 | ready | — |
| `httpx__request_model_core__001` | 26 | 0 | ready | — |
| `humanize__naturaltime_core__001` | 80 | 0 | ready | — |
| `importlib_metadata__entry_points_core__001` | 14 | 0 | ready | — |
| `importlib_resources__traversable_tree_core__hard3_001` | 8 | 0 | ready | — |
| `installer__wheel_record_core__hard3_001` | 4 | 0 | ready | — |
| `intervaltree__interval_tree_core__001` | 62 | 46 | ready | — |
| `isodate__duration_parse_core__001` | 17 | 0 | ready | — |
| `isort__settings_resolver_core__hard3_001` | 7 | 0 | ready | — |
| `jinja2__compile_render_core__001` | 117 | 33 | ready | — |
| `jinja2__extensions_core__001` | 117 | 33 | ready | — |
| `jinja2__filters_tests_core__001` | 117 | 33 | ready | — |
| `jinja2__lexer_parser_core__001` | 117 | 33 | ready | — |
| `jinja2__loader_inheritance_core__001` | 117 | 33 | ready | — |
| `json5__parse_core__001` | 4 | 0 | ready | — |
| `json_logic__evaluator_core__hard3_001` | 4 | 0 | ready | — |
| `jsonpath_ng__expression_eval_core__001` | 29 | 0 | ready | — |
| `jsonpointer__resolve_core__001` | 22 | 0 | ready | — |
| `jsonschema__validator_core__001` | 69 | 22 | ready | — |
| `jupyter_core__paths_resolver_core__hard3_001` | 7 | 0 | ready | — |
| `jupyter_server__extension_config_core__hard3_001` | 7 | 0 | ready | — |
| `keyring__backend_select_core__hard3_001` | 8 | 0 | ready | — |
| `lark__grammar_loader_core__001` | 40 | 0 | ready | — |
| `lark__parse_tree_core__001` | 35 | 0 | ready | — |
| `lark__visitor_transform_core__001` | 35 | 0 | ready | — |
| `license_expression__policy_core__hard3_001` | 5 | 0 | ready | — |
| `mako__lexer_expression_core__001` | 34 | 7 | ready | — |
| `markdown__extensions_core__001` | 52 | 1 | ready | — |
| `markdown_it__commonmark_render__001` | 130 | 0 | ready | — |
| `marshmallow__schema_core__001` | 15 | 0 | ready | — |
| `mkdocs__plugin_config_core__hard3_001` | 7 | 0 | ready | — |
| `msgpack__pack_unpack_core__001` | 61 | 19 | ready | — |
| `multidict__multidict_mutation_core__hard3_001` | 8 | 0 | ready | — |
| `networkx__dag_topo_core__001` | 26 | 0 | ready | — |
| `packaging__requirement_marker_specifier__001` | 30 | 0 | ready | — |
| `parsel__selector_namespace_core__hard3_001` | 4 | 0 | ready | — |
| `parso__python_parse_core__001` | 56 | 0 | ready | — |
| `passlib__hash_context_core__001` | 102 | 36 | ready | — |
| `pathvalidate__sanitize_core__001` | 96 | 12 | ready | — |
| `pendulum__parse_format_core__001` | 123 | 2 | ready | — |
| `phonenumbers__parse_format_core__001` | 45 | 0 | ready | — |
| `platformdirs__app_dirs_core__hard3_001` | 9 | 0 | ready | — |
| `pluggy__hook_call_order__001` | 14 | 0 | ready | — |
| `pluggy__hook_specs_core__001` | 7 | 0 | ready | — |
| `pluggy__hook_wrapper_core__hard3_001` | 6 | 0 | ready | — |
| `poetry_core__dependency_groups_core__hard3_001` | 7 | 0 | ready | — |
| `pydantic__field_validator_core__hard3_001` | 4 | 0 | ready | — |
| `pydantic_settings__env_source_core__001` | 23 | 0 | ready | — |
| `pydantic_v1__validation_error_core__001` | 77 | 0 | ready | — |
| `pygments__formatter_core__001` | 303 | 0 | ready | — |
| `pygments__lexer_core__001` | 316 | 0 | ready | — |
| `pyramid__configurator_action_core__hard3_001` | 7 | 0 | ready | — |
| `pytest__fixture_resolve_core__001` | 601 | 197 | ready | — |
| `pytest__ini_markers_core__001` | 601 | 197 | ready | — |
| `pytest__mark_expression_core__001` | 601 | 197 | ready | — |
| `pytest__marker_registry_core__hard3_001` | 4 | 0 | ready | — |
| `pytest__skipif_eval_core__001` | 601 | 197 | ready | — |
| `python_box__config_box_core__001` | 16 | 0 | ready | — |
| `python_dateutil__relativedelta_core__001` | 12 | 0 | ready | — |
| `python_dateutil__rrule_core__001` | 18 | 0 | ready | — |
| `python_dotenv__env_parse_core__001` | 46 | 12 | ready | — |
| `python_frontmatter__roundtrip_core__001` | 54 | 26 | ready | — |
| `python_multipart__form_parse_core__001` | 114 | 65 | ready | — |
| `pyyaml__safe_load_dump__001` | 35 | 0 | ready | — |
| `readme_renderer__content_type_core__hard3_001` | 4 | 0 | ready | — |
| `redis__resp_parser_core__001` | 13 | 0 | ready | — |
| `referencing__json_schema_refs_core__001` | 16 | 6 | ready | — |
| `requests_cache__cache_key_core__hard3_001` | 7 | 0 | ready | — |
| `responses__request_matcher_core__hard3_001` | 6 | 0 | ready | — |
| `returns__result_pipeline_core__hard3_001` | 4 | 0 | ready | — |
| `rfc3986__uri_parse_core__001` | 19 | 0 | ready | — |
| `rich__markup_parse_core__001` | 80 | 0 | ready | — |
| `ruamel_yaml__roundtrip_core__001` | 61 | 0 | ready | — |
| `schema__nested_validate_core__hard3_001` | 3 | 0 | ready | — |
| `scrapy__item_loader_core__hard3_001` | 4 | 0 | ready | — |
| `setuptools_scm__version_normalize_core__hard3_001` | 4 | 0 | ready | — |
| `sortedcontainers__sorted_list_core__001` | 260 | 33 | ready | — |
| `sphinx__extension_registry_core__hard3_001` | 6 | 0 | ready | — |
| `sqlalchemy__event_dispatch_core__hard3_001` | 7 | 0 | ready | — |
| `sqlparse__format_filters_core__001` | 86 | 29 | ready | — |
| `sqlparse__parse_format_core__001` | 86 | 29 | ready | — |
| `sqlparse__parse_split_core__001` | 86 | 29 | ready | — |
| `sqlparse__token_tree_core__001` | 86 | 29 | ready | — |
| `starlette__route_matching_core__hard3_001` | 7 | 0 | ready | — |
| `stevedore__extension_manager_core__hard3_001` | 8 | 0 | ready | — |
| `tabulate__table_format_core__001` | 26 | 9 | ready | — |
| `tenacity__retry_state_core__hard3_001` | 8 | 0 | ready | — |
| `tomlkit__roundtrip_document__001` | 80 | 43 | ready | — |
| `tox__factor_expression_core__hard3_001` | 5 | 0 | ready | — |
| `trafaret__validation_rules_core__hard3_001` | 8 | 0 | ready | — |
| `transitions__state_machine_core__hard3_001` | 5 | 0 | ready | — |
| `typer__command_parser_core__001` | 34 | 0 | ready | — |
| `urllib3__retry_backoff_core__001` | 16 | 0 | ready | — |
| `vibe_app__csv_transform_core__001` | 59 | 0 | ready | — |
| `vibe_app__orm_query_ast_core__001` | 75 | 0 | ready | — |
| `vibe_app__plugin_registry_core__001` | 75 | 0 | ready | — |
| `vibe_app__pricing_rules_core__001` | 59 | 0 | ready | — |
| `vibe_app__rules_engine_core__001` | 67 | 0 | ready | — |
| `vibe_app__session_registry_core__001` | 67 | 0 | ready | — |
| `vibe_app__yaml_config_bootstrap__001` | 59 | 0 | ready | — |
| `virtualenv__interpreter_spec_core__hard3_001` | 4 | 0 | ready | — |
| `voluptuous__schema_validate_core__001` | 11 | 3 | ready | — |
| `websockets__handshake_parse_core__001` | 52 | 0 | ready | — |
| `werkzeug__routing_core__001` | 120 | 0 | ready | — |
| `wheel__metadata_normalize_core__hard3_001` | 5 | 0 | ready | — |
| `wsproto__frame_parse_core__001` | 22 | 0 | ready | — |
| `xmltodict__xml_parse_core__001` | 6 | 3 | ready | — |
| `yamale__schema_validate_core__hard3_001` | 15 | 0 | ready | — |
| `yarl__url_model_core__001` | 126 | 30 | ready | — |
