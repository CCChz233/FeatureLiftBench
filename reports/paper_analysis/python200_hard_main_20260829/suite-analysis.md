# Mini-SWE-Agent Suite Analysis

Generated at: 2026-08-29T11:19:03+00:00
Source: `reports/paper_analysis/python200_hard_main_20260829/suite-comparison.json`

## Summary

| suite | model | endpoint | functional pass | workflow pass | avg final_score | steps | tokens | agent wall time |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `python200-hard-main-20260829` | `` | `` | 132/200 | 47/200 | 0.660000 | 11,701 | 806,307,663 |  |

## Findings

- python200-hard-main-20260829: 132/200 tasks passed.
- Observed failed runs: python200-hard-main-20260829::apischema__serialization_core__001, python200-hard-main-20260829::authlib__oauth2_server_core__001, python200-hard-main-20260829::betamax__cassette_match_core__001, python200-hard-main-20260829::connexion__openapi_resolver_core__001, python200-hard-main-20260829::copier__template_answers_core__001, python200-hard-main-20260829::goodconf__typed_env_core__001, python200-hard-main-20260829::hydra_core__compose_initialize_core__001, python200-hard-main-20260829::limits__strategy_storage_core__001, python200-hard-main-20260829::luigi__task_requires_core__001, python200-hard-main-20260829::openapi_schema_validator__draft_core__001, python200-hard-main-20260829::oslo_config__opt_group_core__001, python200-hard-main-20260829::oslo_policy__enforcer_core__001, python200-hard-main-20260829::pandera__dataframe_schema_core__001, python200-hard-main-20260829::paste__dispatch_map_core__001, python200-hard-main-20260829::pylint__config_find_core__001, python200-hard-main-20260829::quart__blueprint_dispatch_core__001, python200-hard-main-20260829::rocketry__cond_schedule_core__001, python200-hard-main-20260829::spiffworkflow__bpmn_engine_core__001, python200-hard-main-20260829::taskiq__broker_task_core__001, python200-hard-main-20260829::zope_component__site_lookup_core__001, python200-hard-main-20260829::zope_interface__adapter_registry_core__001, python200-hard-main-20260829::aiohttp__url_params_core__hard3_001, python200-hard-main-20260829::alembic__revision_map_core__hard3_001, python200-hard-main-20260829::build__pyproject_backend_core__hard3_001, python200-hard-main-20260829::celery__signal_dispatch_core__hard3_001, python200-hard-main-20260829::click__lazy_command_core__hard3_001, python200-hard-main-20260829::cookiecutter__repo_finder_core__hard3_001, python200-hard-main-20260829::dateutil__zone_resolver_core__hard3_001, python200-hard-main-20260829::decorator__signature_preserving_core__001, python200-hard-main-20260829::distlib__wheel_metadata_core__hard3_001, python200-hard-main-20260829::dynaconf__settings_merge_core__001, python200-hard-main-20260829::flake8__plugin_options_core__hard3_001, python200-hard-main-20260829::flask__route_dispatch_core__001, python200-hard-main-20260829::fs__url_opener_core__hard3_001, python200-hard-main-20260829::fsspec__url_chain_core__hard3_001, python200-hard-main-20260829::hatch__project_metadata_core__hard3_001, python200-hard-main-20260829::importlib_resources__traversable_tree_core__hard3_001, python200-hard-main-20260829::installer__wheel_record_core__hard3_001, python200-hard-main-20260829::jupyter_core__paths_resolver_core__hard3_001, python200-hard-main-20260829::jupyter_server__extension_config_core__hard3_001, python200-hard-main-20260829::keyring__backend_select_core__hard3_001, python200-hard-main-20260829::license_expression__policy_core__hard3_001, python200-hard-main-20260829::mkdocs__plugin_config_core__hard3_001, python200-hard-main-20260829::multidict__multidict_mutation_core__hard3_001, python200-hard-main-20260829::parsel__selector_namespace_core__hard3_001, python200-hard-main-20260829::pluggy__hook_wrapper_core__hard3_001, python200-hard-main-20260829::poetry_core__dependency_groups_core__hard3_001, python200-hard-main-20260829::pydantic__field_validator_core__hard3_001, python200-hard-main-20260829::pydantic_v1__validation_error_core__001, python200-hard-main-20260829::pygments__lexer_core__001, python200-hard-main-20260829::pyramid__configurator_action_core__hard3_001, python200-hard-main-20260829::pytest__ini_markers_core__001, python200-hard-main-20260829::pytest__marker_registry_core__hard3_001, python200-hard-main-20260829::python_decouple__config_repository_core__001, python200-hard-main-20260829::readme_renderer__content_type_core__hard3_001, python200-hard-main-20260829::requests_cache__cache_key_core__hard3_001, python200-hard-main-20260829::responses__request_matcher_core__hard3_001, python200-hard-main-20260829::schema__nested_validate_core__hard3_001, python200-hard-main-20260829::scrapy__item_loader_core__hard3_001, python200-hard-main-20260829::setuptools_scm__version_normalize_core__hard3_001, python200-hard-main-20260829::starlette__route_matching_core__hard3_001, python200-hard-main-20260829::tenacity__retry_state_core__hard3_001, python200-hard-main-20260829::tox__factor_expression_core__hard3_001, python200-hard-main-20260829::trafaret__validation_rules_core__hard3_001, python200-hard-main-20260829::typer__command_parser_core__001, python200-hard-main-20260829::virtualenv__interpreter_spec_core__hard3_001, python200-hard-main-20260829::wheel__metadata_normalize_core__hard3_001, python200-hard-main-20260829::yamale__schema_validate_core__hard3_001.
- High extraction-ratio passes indicate copy-heavy solutions on: apscheduler__cron_trigger_core__hard3_001, astroid__nodes_core__001, asttokens__token_annotate_core__001, attrs__validators_core__001, bidict__bidirectional_map_core__001, blinker__signal_registry_core__001, cattrs__structure_core__001, cerberus__schema_validate_core__001, chameleon__template_compile_core__001, click__option_parser__001, configobj__roundtrip_config_core__001, croniter__cron_parse_core__001, dataclasses_json__serde_core__001, deepdiff__deep_compare_core__001, diskcache__eviction_policy_core__hard3_001, email_validator__validate_core__001, environs__typed_env_core__001, filelock__reentrant_lock_core__001, glom__spec_eval_core__hard3_001, h11__message_parse_core__001, h2__frame_parse_core__001, httpx__request_model_core__001, intervaltree__interval_tree_core__001, isort__settings_resolver_core__hard3_001, itsdangerous__timed_serializer_core__001, jinja2__compile_render_core__001, jinja2__extensions_core__001, jinja2__filters_tests_core__001, jinja2__lexer_parser_core__001, jinja2__loader_inheritance_core__001, json5__parse_core__001, json_logic__evaluator_core__hard3_001, jsonpath_ng__expression_eval_core__001, lark__grammar_loader_core__001, lark__parse_tree_core__001, lark__visitor_transform_core__001, markdown__extensions_core__001, markdown_it__commonmark_render__001, marshmallow__schema_core__001, mistune__markdown_plugin_core__001, msgpack__pack_unpack_core__001, parse__format_parser_core__001, parso__python_parse_core__001, passlib__hash_context_core__001, pathvalidate__sanitize_core__001, pendulum__parse_format_core__001, phonenumbers__parse_format_core__001, pika__channel_spec_core__001, platformdirs__app_dirs_core__hard3_001, pluggy__hook_call_order__001, pluggy__hook_specs_core__001, pydantic_settings__env_source_core__001, pygments__formatter_core__001, pytest__fixture_resolve_core__001, pytest__mark_expression_core__001, pytest__skipif_eval_core__001, python_box__config_box_core__001, python_dateutil__relativedelta_core__001, python_dateutil__rrule_core__001, python_dotenv__env_parse_core__001, python_multipart__form_parse_core__001, pyyaml__safe_load_dump__001, redis__resp_parser_core__001, referencing__json_schema_refs_core__001, returns__result_pipeline_core__hard3_001, routes__mapper_match_core__001, ruamel_yaml__roundtrip_core__001, sortedcontainers__sorted_list_core__001, sphinx__extension_registry_core__hard3_001, sqlalchemy__event_dispatch_core__hard3_001, sqlparse__format_filters_core__001, sqlparse__parse_format_core__001, sqlparse__parse_split_core__001, sqlparse__token_tree_core__001, stevedore__extension_manager_core__hard3_001, tabulate__table_format_core__001, tomlkit__roundtrip_document__001, transitions__state_machine_core__hard3_001, urllib3__retry_backoff_core__001, voluptuous__schema_validate_core__001, websockets__handshake_parse_core__001, yarl__url_model_core__001.
- Largest token outlier: python200-hard-main-20260829::bleach__sanitize_core__001 used 11,718,807 tokens.
- Pro and Flash used different endpoints, so this is a pilot comparison rather than a controlled model benchmark.

## Per-Task Matrix

| task | python200-hard-main-20260829 status | ratio | score | tokens |
| --- | ---: | ---: | ---: | ---: |
| `aiohttp__url_params_core__hard3_001` | failed | 3.971429 | 0.000000 | 6,422,920 |
| `alembic__revision_map_core__hard3_001` | failed | 7.447005 | 0.000000 | 9,001,373 |
| `anyio__task_group_core__001` | passed | 0.071601 | 1.000000 | 6,329,848 |
| `apischema__serialization_core__001` | not-run |  | 0.000000 | 151,232 |
| `apispec__plugin_documenter_core__001` | passed | 0.349347 | 1.000000 | 1,357,825 |
| `apscheduler__cron_trigger_core__hard3_001` | passed | 9.322034 | 1.000000 | 4,818,009 |
| `arrow__parse_format_core__001` | passed | 0.704684 | 1.000000 | 11,536,103 |
| `astroid__nodes_core__001` | passed | 0.904536 | 1.000000 | 9,542,862 |
| `asttokens__token_annotate_core__001` | passed | 0.824125 | 1.000000 | 2,739,463 |
| `attrs__validators_core__001` | passed | 1.049042 | 1.000000 | 2,597,203 |
| `authlib__oauth2_server_core__001` | failed | 0.094630 | 0.000000 | 2,095,992 |
| `babel__plural_core__001` | passed | 0.681706 | 1.000000 | 3,381,155 |
| `bandit__config_plugin_core__001` | passed | 0.130927 | 1.000000 | 4,257,003 |
| `beaker__session_cache_core__001` | passed | 0.511703 | 1.000000 | 4,360,156 |
| `betamax__cassette_match_core__001` | failed | 0.531111 | 0.000000 | 5,461,117 |
| `bidict__bidirectional_map_core__001` | passed | 0.993359 | 1.000000 | 1,386,613 |
| `bleach__sanitize_core__001` | passed | 0.428124 | 1.000000 | 11,718,807 |
| `blinker__signal_registry_core__001` | passed | 12.441176 | 1.000000 | 2,376,536 |
| `boltons__iterutils_core__001` | passed | 0.507258 | 1.000000 | 2,708,511 |
| `build__pyproject_backend_core__hard3_001` | failed | 2.265306 | 0.000000 | 967,694 |
| `cachetools__cache_eviction_core__001` | passed | 0.765589 | 1.000000 | 1,999,364 |
| `cattrs__structure_core__001` | passed | 1.004365 | 1.000000 | 6,064,253 |
| `celery__signal_dispatch_core__hard3_001` | failed | 2.835821 | 0.000000 | 574,853 |
| `cement__controller_plugin_core__001` | passed | 0.218742 | 1.000000 | 7,430,519 |
| `cerberus__schema_validate_core__001` | passed | 0.925490 | 1.000000 | 6,776,210 |
| `chameleon__template_compile_core__001` | passed | 0.946282 | 1.000000 | 10,291,463 |
| `cherrypy__dispatch_tool_core__001` | passed | 0.126125 | 1.000000 | 8,762,858 |
| `click__lazy_command_core__hard3_001` | failed | 3.607143 | 0.000000 | 2,621,142 |
| `click__option_parser__001` | passed | 0.999870 | 1.000000 | 2,798,395 |
| `cliff__command_dispatch_core__001` | passed | 0.229823 | 1.000000 | 5,701,868 |
| `configobj__roundtrip_config_core__001` | passed | 0.990079 | 1.000000 | 1,626,910 |
| `connexion__openapi_resolver_core__001` | failed | 0.028501 | 0.000000 | 1,167,566 |
| `cookiecutter__repo_finder_core__hard3_001` | failed | 1.404494 | 0.000000 | 1,686,609 |
| `copier__template_answers_core__001` | failed | 0.149156 | 0.000000 | 6,853,133 |
| `coverage__config_merge_core__001` | passed | 0.757658 | 1.000000 | 2,309,618 |
| `coverage__glob_matcher_core__001` | passed | 0.244041 | 1.000000 | 1,345,785 |
| `coverage__path_remap_core__001` | passed | 0.401816 | 1.000000 | 1,209,608 |
| `coverage__report_core__001` | passed | 0.464871 | 1.000000 | 4,308,728 |
| `coverage__source_selection_core__001` | passed | 0.292755 | 1.000000 | 6,117,970 |
| `croniter__cron_parse_core__001` | passed | 0.850980 | 1.000000 | 3,068,019 |
| `dataclasses_json__serde_core__001` | passed | 0.872781 | 1.000000 | 4,900,932 |
| `dateutil__zone_resolver_core__hard3_001` | failed | 4.208955 | 0.000000 | 2,913,838 |
| `decorator__signature_preserving_core__001` | failed | 5.117647 | 0.000000 | 1,451,293 |
| `deepdiff__deep_compare_core__001` | passed | 0.889593 | 1.000000 | 8,952,538 |
| `diskcache__eviction_policy_core__hard3_001` | passed | 1.275000 | 1.000000 | 945,594 |
| `distlib__wheel_metadata_core__hard3_001` | not-run |  | 0.000000 |  |
| `dogpile_cache__region_backend_core__001` | passed | 0.192785 | 1.000000 | 3,379,676 |
| `dramatiq__actor_stub_broker_core__001` | passed | 0.150542 | 1.000000 | 2,369,033 |
| `dulwich__config_parse_core__001` | passed | 0.538985 | 1.000000 | 1,201,249 |
| `dynaconf__settings_merge_core__001` | not-run |  | 0.000000 | 737,886 |
| `email_validator__validate_core__001` | passed | 0.964809 | 1.000000 | 2,508,443 |
| `environs__typed_env_core__001` | passed | 0.988432 | 1.000000 | 2,450,576 |
| `faker__provider_core__001` | passed | 0.421739 | 1.000000 | 5,990,949 |
| `falcon__responder_routing_core__001` | passed | 0.137109 | 1.000000 | 9,862,532 |
| `filelock__reentrant_lock_core__001` | passed | 6.967742 | 1.000000 | 3,915,196 |
| `flake8__plugin_options_core__hard3_001` | failed | 3.723684 | 0.000000 | 3,148,387 |
| `flask__route_dispatch_core__001` | failed | 17.833333 | 0.000000 | 5,456,730 |
| `fs__url_opener_core__hard3_001` | not-run |  | 0.000000 |  |
| `fsspec__url_chain_core__hard3_001` | not-run |  | 0.000000 |  |
| `glom__spec_eval_core__hard3_001` | passed | 25.274510 | 1.000000 | 10,682,383 |
| `goodconf__typed_env_core__001` | failed | 0.658754 | 0.000000 | 2,490,633 |
| `graphene__schema_execute_core__001` | passed | 0.481152 | 1.000000 | 7,529,355 |
| `h11__message_parse_core__001` | passed | 1.000681 | 1.000000 | 1,091,625 |
| `h2__frame_parse_core__001` | passed | 0.924783 | 1.000000 | 2,572,185 |
| `hatch__project_metadata_core__hard3_001` | failed | 10.084337 | 0.000000 | 5,688,939 |
| `httpretty__uri_stub_core__001` | passed | 0.249504 | 1.000000 | 4,552,273 |
| `httpx__request_model_core__001` | passed | 1.043928 | 1.000000 | 4,821,858 |
| `humanize__naturaltime_core__001` | passed | 0.417459 | 1.000000 | 3,133,072 |
| `hydra_core__compose_initialize_core__001` | failed | 0.391476 | 0.000000 | 10,166,739 |
| `importlib_metadata__entry_points_core__001` | passed | 0.160272 | 1.000000 | 1,805,900 |
| `importlib_resources__traversable_tree_core__hard3_001` | failed | 1.607362 | 0.000000 | 7,874,061 |
| `installer__wheel_record_core__hard3_001` | failed | 2.757576 | 0.000000 | 1,320,223 |
| `intervaltree__interval_tree_core__001` | passed | 1.002287 | 1.000000 | 1,260,969 |
| `isodate__duration_parse_core__001` | passed | 0.674835 | 1.000000 | 3,028,237 |
| `isort__settings_resolver_core__hard3_001` | passed | 2.106618 | 1.000000 | 5,135,832 |
| `itsdangerous__timed_serializer_core__001` | passed | 13.974359 | 1.000000 | 1,874,892 |
| `jinja2__compile_render_core__001` | passed | 0.971665 | 1.000000 | 10,670,167 |
| `jinja2__extensions_core__001` | passed | 1.055694 | 1.000000 | 4,965,334 |
| `jinja2__filters_tests_core__001` | passed | 1.249328 | 1.000000 | 5,627,465 |
| `jinja2__lexer_parser_core__001` | passed | 0.915259 | 1.000000 | 8,789,722 |
| `jinja2__loader_inheritance_core__001` | passed | 1.024992 | 1.000000 | 2,633,622 |
| `json5__parse_core__001` | passed | 1.063047 | 1.000000 | 644,776 |
| `json_logic__evaluator_core__hard3_001` | passed | 1.290780 | 1.000000 | 679,432 |
| `jsonpath_ng__expression_eval_core__001` | passed | 2.915552 | 1.000000 | 2,316,882 |
| `jsonpointer__resolve_core__001` | passed | 0.764444 | 1.000000 | 498,245 |
| `jsonschema__validator_core__001` | passed | 0.620719 | 1.000000 | 8,576,213 |
| `jupyter_core__paths_resolver_core__hard3_001` | failed | 1.654930 | 0.000000 | 5,036,797 |
| `jupyter_server__extension_config_core__hard3_001` | not-run |  | 0.000000 |  |
| `keyring__backend_select_core__hard3_001` | failed | 2.019108 | 0.000000 | 2,245,247 |
| `lark__grammar_loader_core__001` | passed | 1.000000 | 1.000000 | 5,217,177 |
| `lark__parse_tree_core__001` | passed | 1.021574 | 1.000000 | 9,847,514 |
| `lark__visitor_transform_core__001` | passed | 0.991964 | 1.000000 | 3,599,759 |
| `license_expression__policy_core__hard3_001` | not-run |  | 0.000000 |  |
| `limits__strategy_storage_core__001` | failed | 0.197023 | 0.000000 | 2,386,526 |
| `luigi__task_requires_core__001` | failed | 0.008552 | 0.000000 | 1,340,154 |
| `mako__lexer_expression_core__001` | passed | 0.737599 | 1.000000 | 6,071,276 |
| `markdown__extensions_core__001` | passed | 1.072274 | 1.000000 | 3,987,401 |
| `markdown_it__commonmark_render__001` | passed | 1.000000 | 1.000000 | 1,960,811 |
| `marshmallow__schema_core__001` | passed | 0.997459 | 1.000000 | 4,441,976 |
| `mashumaro__dataclass_codec_core__001` | passed | 0.691577 | 1.000000 | 2,515,295 |
| `mimesis__person_address_core__001` | passed | 0.696503 | 1.000000 | 4,835,289 |
| `mistune__markdown_plugin_core__001` | passed | 0.948192 | 1.000000 | 1,285,500 |
| `mitmproxy__url_parse_core__001` | passed | 0.251781 | 1.000000 | 391,124 |
| `mkdocs__plugin_config_core__hard3_001` | failed | 3.000000 | 0.000000 | 974,467 |
| `msgpack__pack_unpack_core__001` | passed | 0.991168 | 1.000000 | 1,758,098 |
| `multidict__multidict_mutation_core__hard3_001` | failed | 4.543624 | 0.000000 | 10,811,213 |
| `networkx__dag_topo_core__001` | passed | 0.155261 | 1.000000 | 5,662,468 |
| `oauthlib__grant_dispatch_core__001` | passed | 0.189072 | 1.000000 | 11,465,347 |
| `openapi_schema_validator__draft_core__001` | failed | 0.767802 | 0.000000 | 5,286,048 |
| `oslo_config__opt_group_core__001` | failed | 0.699969 | 0.000000 | 9,508,733 |
| `oslo_policy__enforcer_core__001` | failed | 0.710359 | 0.000000 | 9,818,043 |
| `packaging__requirement_marker_specifier__001` | passed | 0.580190 | 1.000000 | 3,677,289 |
| `pandera__dataframe_schema_core__001` | failed | 0.048007 | 0.000000 | 10,840,830 |
| `parse__format_parser_core__001` | passed | 9.133333 | 1.000000 | 3,125,149 |
| `parsel__selector_namespace_core__hard3_001` | failed | 19.705882 | 0.000000 | 10,194,257 |
| `parso__python_parse_core__001` | passed | 1.006434 | 1.000000 | 6,617,837 |
| `passlib__hash_context_core__001` | passed | 1.882546 | 1.000000 | 1,601,986 |
| `paste__dispatch_map_core__001` | failed | 0.005993 | 0.000000 | 349,085 |
| `pathvalidate__sanitize_core__001` | passed | 0.861842 | 1.000000 | 2,793,157 |
| `pendulum__parse_format_core__001` | passed | 0.802653 | 1.000000 | 10,822,066 |
| `phonenumbers__parse_format_core__001` | passed | 1.140064 | 1.000000 | 5,017,953 |
| `pika__channel_spec_core__001` | passed | 0.979909 | 1.000000 | 1,202,706 |
| `platformdirs__app_dirs_core__hard3_001` | passed | 1.135338 | 1.000000 | 2,980,877 |
| `pluggy__hook_call_order__001` | passed | 0.992997 | 1.000000 | 1,368,593 |
| `pluggy__hook_specs_core__001` | passed | 0.943978 | 1.000000 | 1,215,212 |
| `pluggy__hook_wrapper_core__hard3_001` | failed | 2.813131 | 0.000000 | 3,799,997 |
| `poetry_core__dependency_groups_core__hard3_001` | not-run |  | 0.000000 |  |
| `polyfactory__model_factory_core__001` | passed | 0.633854 | 1.000000 | 6,143,303 |
| `pre_commit__config_load_core__001` | passed | 0.139435 | 1.000000 | 4,557,891 |
| `pydantic__field_validator_core__hard3_001` | not-run |  | 0.000000 |  |
| `pydantic_settings__env_source_core__001` | passed | 0.861684 | 1.000000 | 10,603,108 |
| `pydantic_v1__validation_error_core__001` | not-run |  | 0.000000 |  |
| `pygments__formatter_core__001` | passed | 1.364193 | 1.000000 | 6,196,125 |
| `pygments__lexer_core__001` | failed | 0.804445 | 0.000000 | 6,133,151 |
| `pylint__config_find_core__001` | failed | 0.032840 | 0.000000 | 10,056,126 |
| `pyramid__configurator_action_core__hard3_001` | not-run |  | 0.000000 |  |
| `pytest__fixture_resolve_core__001` | passed | 2.385827 | 1.000000 | 3,378,001 |
| `pytest__ini_markers_core__001` | failed | 4.441176 | 0.000000 | 3,700,211 |
| `pytest__mark_expression_core__001` | passed | 1.007519 | 1.000000 | 1,046,870 |
| `pytest__marker_registry_core__hard3_001` | failed | 1.921875 | 0.000000 | 1,728,058 |
| `pytest__skipif_eval_core__001` | passed | 1.580247 | 1.000000 | 1,479,642 |
| `python_box__config_box_core__001` | passed | 0.960956 | 1.000000 | 6,154,547 |
| `python_configuration__layered_config_core__001` | passed | 0.437618 | 1.000000 | 2,468,502 |
| `python_dateutil__relativedelta_core__001` | passed | 0.973404 | 1.000000 | 2,144,253 |
| `python_dateutil__rrule_core__001` | passed | 1.041640 | 1.000000 | 5,174,619 |
| `python_decouple__config_repository_core__001` | failed | 3.318182 | 0.000000 | 821,406 |
| `python_dotenv__env_parse_core__001` | passed | 0.804878 | 1.000000 | 954,960 |
| `python_frontmatter__roundtrip_core__001` | passed | 0.641473 | 1.000000 | 1,149,900 |
| `python_multipart__form_parse_core__001` | passed | 0.988506 | 1.000000 | 4,079,139 |
| `pyyaml__safe_load_dump__001` | passed | 0.871685 | 1.000000 | 2,599,562 |
| `quart__blueprint_dispatch_core__001` | failed | 0.243080 | 0.000000 | 7,217,525 |
| `readme_renderer__content_type_core__hard3_001` | failed | 8.416667 | 0.000000 | 4,124,148 |
| `redbaron__fst_mutate_core__001` | passed | 0.111238 | 1.000000 | 5,520,095 |
| `redis__resp_parser_core__001` | passed | 0.829238 | 1.000000 | 2,131,096 |
| `referencing__json_schema_refs_core__001` | passed | 0.980998 | 1.000000 | 3,626,491 |
| `requests_cache__cache_key_core__hard3_001` | not-run |  | 0.000000 |  |
| `responses__request_matcher_core__hard3_001` | failed | 3.870130 | 0.000000 | 2,410,391 |
| `returns__result_pipeline_core__hard3_001` | passed | 2.596154 | 1.000000 | 1,115,398 |
| `rfc3986__uri_parse_core__001` | passed | 0.626061 | 1.000000 | 2,903,135 |
| `rich__markup_parse_core__001` | passed | 0.310409 | 1.000000 | 7,429,301 |
| `rocketry__cond_schedule_core__001` | failed | 0.095058 | 0.000000 | 4,573,037 |
| `routes__mapper_match_core__001` | passed | 0.936452 | 1.000000 | 3,806,032 |
| `ruamel_yaml__roundtrip_core__001` | passed | 1.004734 | 1.000000 | 9,693,565 |
| `schema__nested_validate_core__hard3_001` | not-run |  | 0.000000 |  |
| `scrapy__item_loader_core__hard3_001` | failed | 6.578947 | 0.000000 | 8,902,139 |
| `setuptools_scm__version_normalize_core__hard3_001` | not-run |  | 0.000000 |  |
| `sortedcontainers__sorted_list_core__001` | passed | 0.934818 | 1.000000 | 1,732,685 |
| `sphinx__extension_registry_core__hard3_001` | passed | 5.500000 | 1.000000 | 790,051 |
| `spiffworkflow__bpmn_engine_core__001` | failed | 0.071957 | 0.000000 | 6,654,590 |
| `sqlalchemy__event_dispatch_core__hard3_001` | passed | 3.080645 | 1.000000 | 3,436,578 |
| `sqlparse__format_filters_core__001` | passed | 1.005190 | 1.000000 | 2,990,424 |
| `sqlparse__parse_format_core__001` | passed | 1.008953 | 1.000000 | 3,169,037 |
| `sqlparse__parse_split_core__001` | passed | 0.962947 | 1.000000 | 2,806,452 |
| `sqlparse__token_tree_core__001` | passed | 0.954465 | 1.000000 | 3,236,873 |
| `starlette__route_matching_core__hard3_001` | not-run |  | 0.000000 |  |
| `stdnum__isbn_validate_core__001` | passed | 0.481422 | 1.000000 | 1,939,880 |
| `stevedore__extension_manager_core__hard3_001` | passed | 2.281385 | 1.000000 | 2,999,190 |
| `tabulate__table_format_core__001` | passed | 1.003029 | 1.000000 | 4,293,461 |
| `taskiq__broker_task_core__001` | failed | 0.174238 | 0.000000 | 8,372,367 |
| `tenacity__retry_state_core__hard3_001` | not-run |  | 0.000000 |  |
| `tomlkit__roundtrip_document__001` | passed | 1.000000 | 1.000000 | 441,234 |
| `tornado__http_headers_core__001` | passed | 0.109709 | 1.000000 | 557,589 |
| `tox__factor_expression_core__hard3_001` | failed | 2.886076 | 0.000000 | 2,114,721 |
| `trafaret__validation_rules_core__hard3_001` | not-run |  | 0.000000 |  |
| `transitions__state_machine_core__hard3_001` | passed | 7.672000 | 1.000000 | 10,742,058 |
| `typedload__type_load_core__001` | passed | 0.736582 | 1.000000 | 2,556,086 |
| `typer__command_parser_core__001` | failed | 0.385053 | 0.000000 | 11,120,269 |
| `urllib3__retry_backoff_core__001` | passed | 1.010802 | 1.000000 | 2,485,999 |
| `virtualenv__interpreter_spec_core__hard3_001` | not-run |  | 0.000000 |  |
| `voluptuous__schema_validate_core__001` | passed | 0.863914 | 1.000000 | 4,948,894 |
| `webob__request_response_core__001` | passed | 0.286063 | 1.000000 | 11,122,182 |
| `websockets__handshake_parse_core__001` | passed | 1.210484 | 1.000000 | 5,129,554 |
| `werkzeug__routing_core__001` | passed | 0.405339 | 1.000000 | 7,353,191 |
| `wheel__metadata_normalize_core__hard3_001` | not-run |  | 0.000000 |  |
| `wsproto__frame_parse_core__001` | passed | 0.742068 | 1.000000 | 1,193,343 |
| `xmltodict__xml_parse_core__001` | passed | 0.581272 | 1.000000 | 1,936,451 |
| `yamale__schema_validate_core__hard3_001` | failed | 5.054054 | 0.000000 | 4,945,850 |
| `yarl__url_model_core__001` | passed | 0.995570 | 1.000000 | 4,677,498 |
| `zope_component__site_lookup_core__001` | failed | 0.484632 | 0.000000 | 7,136,890 |
| `zope_interface__adapter_registry_core__001` | failed | 0.596003 | 0.000000 | 8,808,103 |

## High Extraction-Ratio Passes

Threshold: `extraction_ratio >= 0.8` and functional pass.

| suite | task | ratio | final_score | submission_loc | source_loc |
| --- | --- | ---: | ---: | ---: | ---: |
| `python200-hard-main-20260829` | `glom__spec_eval_core__hard3_001` | 25.274510 | 1.000000 | 1,289 | 0 |
| `python200-hard-main-20260829` | `itsdangerous__timed_serializer_core__001` | 13.974359 | 1.000000 | 545 | 0 |
| `python200-hard-main-20260829` | `blinker__signal_registry_core__001` | 12.441176 | 1.000000 | 423 | 0 |
| `python200-hard-main-20260829` | `apscheduler__cron_trigger_core__hard3_001` | 9.322034 | 1.000000 | 550 | 0 |
| `python200-hard-main-20260829` | `parse__format_parser_core__001` | 9.133333 | 1.000000 | 411 | 0 |
| `python200-hard-main-20260829` | `transitions__state_machine_core__hard3_001` | 7.672000 | 1.000000 | 959 | 0 |
| `python200-hard-main-20260829` | `filelock__reentrant_lock_core__001` | 6.967742 | 1.000000 | 216 | 0 |
| `python200-hard-main-20260829` | `sphinx__extension_registry_core__hard3_001` | 5.500000 | 1.000000 | 165 | 0 |
| `python200-hard-main-20260829` | `sqlalchemy__event_dispatch_core__hard3_001` | 3.080645 | 1.000000 | 191 | 0 |
| `python200-hard-main-20260829` | `jsonpath_ng__expression_eval_core__001` | 2.915552 | 1.000000 | 4,143 | 0 |
| `python200-hard-main-20260829` | `returns__result_pipeline_core__hard3_001` | 2.596154 | 1.000000 | 135 | 0 |
| `python200-hard-main-20260829` | `pytest__fixture_resolve_core__001` | 2.385827 | 1.000000 | 303 | 0 |
| `python200-hard-main-20260829` | `stevedore__extension_manager_core__hard3_001` | 2.281385 | 1.000000 | 527 | 0 |
| `python200-hard-main-20260829` | `isort__settings_resolver_core__hard3_001` | 2.106618 | 1.000000 | 573 | 0 |
| `python200-hard-main-20260829` | `passlib__hash_context_core__001` | 1.882546 | 1.000000 | 13,784 | 0 |
| `python200-hard-main-20260829` | `pytest__skipif_eval_core__001` | 1.580247 | 1.000000 | 128 | 0 |
| `python200-hard-main-20260829` | `pygments__formatter_core__001` | 1.364193 | 1.000000 | 7,574 | 0 |
| `python200-hard-main-20260829` | `json_logic__evaluator_core__hard3_001` | 1.290780 | 1.000000 | 182 | 0 |
| `python200-hard-main-20260829` | `diskcache__eviction_policy_core__hard3_001` | 1.275000 | 1.000000 | 102 | 0 |
| `python200-hard-main-20260829` | `jinja2__filters_tests_core__001` | 1.249328 | 1.000000 | 11,154 | 0 |
| `python200-hard-main-20260829` | `websockets__handshake_parse_core__001` | 1.210484 | 1.000000 | 1,501 | 0 |
| `python200-hard-main-20260829` | `phonenumbers__parse_format_core__001` | 1.140064 | 1.000000 | 3,907 | 0 |
| `python200-hard-main-20260829` | `platformdirs__app_dirs_core__hard3_001` | 1.135338 | 1.000000 | 151 | 0 |
| `python200-hard-main-20260829` | `markdown__extensions_core__001` | 1.072274 | 1.000000 | 3,353 | 0 |
| `python200-hard-main-20260829` | `json5__parse_core__001` | 1.063047 | 1.000000 | 1,214 | 0 |
| `python200-hard-main-20260829` | `jinja2__extensions_core__001` | 1.055694 | 1.000000 | 10,141 | 0 |
| `python200-hard-main-20260829` | `attrs__validators_core__001` | 1.049042 | 1.000000 | 4,107 | 0 |
| `python200-hard-main-20260829` | `httpx__request_model_core__001` | 1.043928 | 1.000000 | 2,424 | 0 |
| `python200-hard-main-20260829` | `python_dateutil__rrule_core__001` | 1.041640 | 1.000000 | 1,651 | 0 |
| `python200-hard-main-20260829` | `jinja2__loader_inheritance_core__001` | 1.024992 | 1.000000 | 9,679 | 0 |
| `python200-hard-main-20260829` | `lark__parse_tree_core__001` | 1.021574 | 1.000000 | 5,919 | 0 |
| `python200-hard-main-20260829` | `urllib3__retry_backoff_core__001` | 1.010802 | 1.000000 | 655 | 0 |
| `python200-hard-main-20260829` | `sqlparse__parse_format_core__001` | 1.008953 | 1.000000 | 2,930 | 0 |
| `python200-hard-main-20260829` | `pytest__mark_expression_core__001` | 1.007519 | 1.000000 | 268 | 0 |
| `python200-hard-main-20260829` | `parso__python_parse_core__001` | 1.006434 | 1.000000 | 4,536 | 0 |
| `python200-hard-main-20260829` | `sqlparse__format_filters_core__001` | 1.005190 | 1.000000 | 2,905 | 0 |
| `python200-hard-main-20260829` | `ruamel_yaml__roundtrip_core__001` | 1.004734 | 1.000000 | 11,460 | 0 |
| `python200-hard-main-20260829` | `cattrs__structure_core__001` | 1.004365 | 1.000000 | 2,991 | 0 |
| `python200-hard-main-20260829` | `tabulate__table_format_core__001` | 1.003029 | 1.000000 | 2,318 | 0 |
| `python200-hard-main-20260829` | `intervaltree__interval_tree_core__001` | 1.002287 | 1.000000 | 1,753 | 0 |
| `python200-hard-main-20260829` | `h11__message_parse_core__001` | 1.000681 | 1.000000 | 1,470 | 0 |
| `python200-hard-main-20260829` | `lark__grammar_loader_core__001` | 1.000000 | 1.000000 | 6,450 | 0 |
| `python200-hard-main-20260829` | `markdown_it__commonmark_render__001` | 1.000000 | 1.000000 | 4,412 | 0 |
| `python200-hard-main-20260829` | `tomlkit__roundtrip_document__001` | 1.000000 | 1.000000 | 4,528 | 0 |
| `python200-hard-main-20260829` | `click__option_parser__001` | 0.999870 | 1.000000 | 7,682 | 0 |
| `python200-hard-main-20260829` | `marshmallow__schema_core__001` | 0.997459 | 1.000000 | 3,926 | 0 |
| `python200-hard-main-20260829` | `yarl__url_model_core__001` | 0.995570 | 1.000000 | 1,798 | 0 |
| `python200-hard-main-20260829` | `bidict__bidirectional_map_core__001` | 0.993359 | 1.000000 | 1,047 | 0 |
| `python200-hard-main-20260829` | `pluggy__hook_call_order__001` | 0.992997 | 1.000000 | 709 | 0 |
| `python200-hard-main-20260829` | `lark__visitor_transform_core__001` | 0.991964 | 1.000000 | 5,925 | 0 |
| `python200-hard-main-20260829` | `msgpack__pack_unpack_core__001` | 0.991168 | 1.000000 | 1,010 | 0 |
| `python200-hard-main-20260829` | `configobj__roundtrip_config_core__001` | 0.990079 | 1.000000 | 2,994 | 0 |
| `python200-hard-main-20260829` | `python_multipart__form_parse_core__001` | 0.988506 | 1.000000 | 1,204 | 0 |
| `python200-hard-main-20260829` | `environs__typed_env_core__001` | 0.988432 | 1.000000 | 769 | 0 |
| `python200-hard-main-20260829` | `referencing__json_schema_refs_core__001` | 0.980998 | 1.000000 | 1,239 | 0 |
| `python200-hard-main-20260829` | `pika__channel_spec_core__001` | 0.979909 | 1.000000 | 3,024 | 0 |
| `python200-hard-main-20260829` | `python_dateutil__relativedelta_core__001` | 0.973404 | 1.000000 | 549 | 0 |
| `python200-hard-main-20260829` | `jinja2__compile_render_core__001` | 0.971665 | 1.000000 | 8,676 | 0 |
| `python200-hard-main-20260829` | `email_validator__validate_core__001` | 0.964809 | 1.000000 | 658 | 0 |
| `python200-hard-main-20260829` | `sqlparse__parse_split_core__001` | 0.962947 | 1.000000 | 2,183 | 0 |
| `python200-hard-main-20260829` | `python_box__config_box_core__001` | 0.960956 | 1.000000 | 1,206 | 0 |
| `python200-hard-main-20260829` | `sqlparse__token_tree_core__001` | 0.954465 | 1.000000 | 2,159 | 0 |
| `python200-hard-main-20260829` | `mistune__markdown_plugin_core__001` | 0.948192 | 1.000000 | 4,850 | 0 |
| `python200-hard-main-20260829` | `chameleon__template_compile_core__001` | 0.946282 | 1.000000 | 5,179 | 0 |
| `python200-hard-main-20260829` | `pluggy__hook_specs_core__001` | 0.943978 | 1.000000 | 674 | 0 |
| `python200-hard-main-20260829` | `routes__mapper_match_core__001` | 0.936452 | 1.000000 | 2,122 | 0 |
| `python200-hard-main-20260829` | `sortedcontainers__sorted_list_core__001` | 0.934818 | 1.000000 | 1,133 | 0 |
| `python200-hard-main-20260829` | `cerberus__schema_validate_core__001` | 0.925490 | 1.000000 | 2,360 | 0 |
| `python200-hard-main-20260829` | `h2__frame_parse_core__001` | 0.924783 | 1.000000 | 959 | 0 |
| `python200-hard-main-20260829` | `jinja2__lexer_parser_core__001` | 0.915259 | 1.000000 | 3,251 | 0 |
| `python200-hard-main-20260829` | `astroid__nodes_core__001` | 0.904536 | 1.000000 | 15,094 | 0 |
| `python200-hard-main-20260829` | `deepdiff__deep_compare_core__001` | 0.889593 | 1.000000 | 6,317 | 0 |
| `python200-hard-main-20260829` | `dataclasses_json__serde_core__001` | 0.872781 | 1.000000 | 885 | 0 |
| `python200-hard-main-20260829` | `pyyaml__safe_load_dump__001` | 0.871685 | 1.000000 | 3,879 | 0 |
| `python200-hard-main-20260829` | `voluptuous__schema_validate_core__001` | 0.863914 | 1.000000 | 1,130 | 0 |
| `python200-hard-main-20260829` | `pathvalidate__sanitize_core__001` | 0.861842 | 1.000000 | 1,310 | 0 |
| `python200-hard-main-20260829` | `pydantic_settings__env_source_core__001` | 0.861684 | 1.000000 | 1,545 | 0 |
| `python200-hard-main-20260829` | `croniter__cron_parse_core__001` | 0.850980 | 1.000000 | 651 | 0 |
| `python200-hard-main-20260829` | `redis__resp_parser_core__001` | 0.829238 | 1.000000 | 675 | 0 |
| `python200-hard-main-20260829` | `asttokens__token_annotate_core__001` | 0.824125 | 1.000000 | 1,059 | 0 |
| `python200-hard-main-20260829` | `python_dotenv__env_parse_core__001` | 0.804878 | 1.000000 | 495 | 0 |
| `python200-hard-main-20260829` | `pendulum__parse_format_core__001` | 0.802653 | 1.000000 | 3,994 | 0 |

## Compact Functional Passes

Threshold: `extraction_ratio <= 0.25` and functional pass.

| suite | task | ratio | final_score | submission_loc | source_loc |
| --- | --- | ---: | ---: | ---: | ---: |
| `python200-hard-main-20260829` | `anyio__task_group_core__001` | 0.071601 | 1.000000 | 919 | 0 |
| `python200-hard-main-20260829` | `tornado__http_headers_core__001` | 0.109709 | 1.000000 | 200 | 0 |
| `python200-hard-main-20260829` | `redbaron__fst_mutate_core__001` | 0.111238 | 1.000000 | 293 | 0 |
| `python200-hard-main-20260829` | `cherrypy__dispatch_tool_core__001` | 0.126125 | 1.000000 | 1,682 | 0 |
| `python200-hard-main-20260829` | `bandit__config_plugin_core__001` | 0.130927 | 1.000000 | 1,146 | 0 |
| `python200-hard-main-20260829` | `falcon__responder_routing_core__001` | 0.137109 | 1.000000 | 2,576 | 0 |
| `python200-hard-main-20260829` | `pre_commit__config_load_core__001` | 0.139435 | 1.000000 | 780 | 0 |
| `python200-hard-main-20260829` | `dramatiq__actor_stub_broker_core__001` | 0.150542 | 1.000000 | 806 | 0 |
| `python200-hard-main-20260829` | `networkx__dag_topo_core__001` | 0.155261 | 1.000000 | 1,688 | 0 |
| `python200-hard-main-20260829` | `importlib_metadata__entry_points_core__001` | 0.160272 | 1.000000 | 259 | 0 |
| `python200-hard-main-20260829` | `oauthlib__grant_dispatch_core__001` | 0.189072 | 1.000000 | 1,737 | 0 |
| `python200-hard-main-20260829` | `dogpile_cache__region_backend_core__001` | 0.192785 | 1.000000 | 994 | 0 |
| `python200-hard-main-20260829` | `cement__controller_plugin_core__001` | 0.218742 | 1.000000 | 1,704 | 0 |
| `python200-hard-main-20260829` | `cliff__command_dispatch_core__001` | 0.229823 | 1.000000 | 598 | 0 |
| `python200-hard-main-20260829` | `coverage__glob_matcher_core__001` | 0.244041 | 1.000000 | 215 | 0 |
| `python200-hard-main-20260829` | `httpretty__uri_stub_core__001` | 0.249504 | 1.000000 | 503 | 0 |

## Token Outliers

| suite | task | tokens | steps | agent wall time |
| --- | --- | ---: | ---: | ---: |
| `python200-hard-main-20260829` | `bleach__sanitize_core__001` | 11,718,807 | 130 | 1039.0s |
| `python200-hard-main-20260829` | `arrow__parse_format_core__001` | 11,536,103 | 121 | 797.9s |
| `python200-hard-main-20260829` | `oauthlib__grant_dispatch_core__001` | 11,465,347 | 123 | 785.0s |
| `python200-hard-main-20260829` | `webob__request_response_core__001` | 11,122,182 | 122 | 819.5s |
| `python200-hard-main-20260829` | `typer__command_parser_core__001` | 11,120,269 | 124 | 1012.0s |

## Failures

| suite | task | status | functional_gate | test_pass | trajectory |
| --- | --- | --- | ---: | --- | --- |
| `python200-hard-main-20260829` | `apischema__serialization_core__001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/apischema__serialization_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `authlib__oauth2_server_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/authlib__oauth2_server_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `betamax__cassette_match_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/betamax__cassette_match_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `connexion__openapi_resolver_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/connexion__openapi_resolver_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `copier__template_answers_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/copier__template_answers_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `goodconf__typed_env_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/goodconf__typed_env_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `hydra_core__compose_initialize_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/hydra_core__compose_initialize_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `limits__strategy_storage_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/limits__strategy_storage_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `luigi__task_requires_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/luigi__task_requires_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `openapi_schema_validator__draft_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/openapi_schema_validator__draft_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `oslo_config__opt_group_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/oslo_config__opt_group_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `oslo_policy__enforcer_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/oslo_policy__enforcer_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pandera__dataframe_schema_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pandera__dataframe_schema_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `paste__dispatch_map_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/paste__dispatch_map_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pylint__config_find_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pylint__config_find_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `quart__blueprint_dispatch_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/quart__blueprint_dispatch_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `rocketry__cond_schedule_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/rocketry__cond_schedule_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `spiffworkflow__bpmn_engine_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/spiffworkflow__bpmn_engine_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `taskiq__broker_task_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/taskiq__broker_task_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `zope_component__site_lookup_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/zope_component__site_lookup_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `zope_interface__adapter_registry_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/zope_interface__adapter_registry_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `aiohttp__url_params_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/aiohttp__url_params_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `alembic__revision_map_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/alembic__revision_map_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `build__pyproject_backend_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/build__pyproject_backend_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `celery__signal_dispatch_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/celery__signal_dispatch_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `click__lazy_command_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/click__lazy_command_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `cookiecutter__repo_finder_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/cookiecutter__repo_finder_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `dateutil__zone_resolver_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/dateutil__zone_resolver_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `decorator__signature_preserving_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/decorator__signature_preserving_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `distlib__wheel_metadata_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/distlib__wheel_metadata_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `dynaconf__settings_merge_core__001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/dynaconf__settings_merge_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `flake8__plugin_options_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/flake8__plugin_options_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `flask__route_dispatch_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/flask__route_dispatch_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `fs__url_opener_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/fs__url_opener_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `fsspec__url_chain_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/fsspec__url_chain_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `hatch__project_metadata_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/hatch__project_metadata_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `importlib_resources__traversable_tree_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/importlib_resources__traversable_tree_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `installer__wheel_record_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/installer__wheel_record_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `jupyter_core__paths_resolver_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/jupyter_core__paths_resolver_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `jupyter_server__extension_config_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/jupyter_server__extension_config_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `keyring__backend_select_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/keyring__backend_select_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `license_expression__policy_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/license_expression__policy_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `mkdocs__plugin_config_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/mkdocs__plugin_config_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `multidict__multidict_mutation_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/multidict__multidict_mutation_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `parsel__selector_namespace_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/parsel__selector_namespace_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pluggy__hook_wrapper_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pluggy__hook_wrapper_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `poetry_core__dependency_groups_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/poetry_core__dependency_groups_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pydantic__field_validator_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pydantic__field_validator_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pydantic_v1__validation_error_core__001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pydantic_v1__validation_error_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pygments__lexer_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pygments__lexer_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pyramid__configurator_action_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pyramid__configurator_action_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pytest__ini_markers_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pytest__ini_markers_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `pytest__marker_registry_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/pytest__marker_registry_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `python_decouple__config_repository_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/python_decouple__config_repository_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `readme_renderer__content_type_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/readme_renderer__content_type_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `requests_cache__cache_key_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/requests_cache__cache_key_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `responses__request_matcher_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/responses__request_matcher_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `schema__nested_validate_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/schema__nested_validate_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `scrapy__item_loader_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/scrapy__item_loader_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `setuptools_scm__version_normalize_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/setuptools_scm__version_normalize_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `starlette__route_matching_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/starlette__route_matching_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `tenacity__retry_state_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/tenacity__retry_state_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `tox__factor_expression_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/tox__factor_expression_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `trafaret__validation_rules_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/trafaret__validation_rules_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `typer__command_parser_core__001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/typer__command_parser_core__001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `virtualenv__interpreter_spec_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/virtualenv__interpreter_spec_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `wheel__metadata_normalize_core__hard3_001` | not-run |  | None | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/wheel__metadata_normalize_core__hard3_001/agent/trajectory.json` |
| `python200-hard-main-20260829` | `yamale__schema_validate_core__hard3_001` | failed | 0.0 | False | `experiments/python/openhands/deepseek-v4-flash/python200-hard-main-20260829/yamale__schema_validate_core__hard3_001/agent/trajectory.json` |

## Recommendations

- Inspect high extraction-ratio passes first: click, markdown_it, pluggy, and pyyaml are functional but copy-heavy.
- Use the Flash jsonschema hidden-test failure as the first concrete failure-mode case study.
- Add property-style or migrated edge tests only after confirming each high-ratio task is passing by broad copying rather than legitimate large closure.
- Move trajectory step/token aggregation into run-agent output once the current analysis format looks right.
