# Python Repository and Task Inventory

## Purpose

This inventory is the management document for Python difficulty audit, task filtering, and main split selection. It is not a separate benchmark definition; it is the Python language split inventory for FeatureLiftBench.

Status enum:

- `candidate`
- `in_progress`
- `valid`
- `needs_hidden_tests`
- `too_easy`
- `too_hard`
- `rejected`

## Current Metadata Snapshot

Scanned from `benchmark/tasks/*/metadata.json` on 2026-07-19:

- Tasks: 150.
- Unique source names: 121.
- Metadata difficulty: 150 `hard`.
- `Ref LOC`: populated only when `metadata.scoring_reference.oracle_loc` exists; otherwise `TBD`.
- `Files`: count from `evaluation/oracle_manifest.json.required_source_files` when available; otherwise `TBD`.

## Repository Pool

| Repo ID | Repo | LOC | Tests | Install | Candidate Features | Score | Decision | Notes |
|---|---|---:|---|---|---|---:|---|---|
| coveragepy | https://github.com/coveragepy/coveragepy | TBD | yes | task lock | config merge; glob matcher; path remap; report; source selection | TBD | accepted | 5 tasks |
| jinja2 | https://github.com/pallets/jinja | TBD | yes | task lock | compile/render; extensions; filters/tests; lexer/parser; loader/inheritance | TBD | accepted | 5 tasks |
| pytest | https://github.com/pytest-dev/pytest | TBD | yes | task lock | fixture resolution; ini markers; mark expression; skipif eval | TBD | accepted | 4 tasks |
| sqlparse | https://github.com/andialbrecht/sqlparse | TBD | yes | task lock | format filters; parse/format; parse/split; token tree | TBD | accepted | 4 tasks |
| lark | https://github.com/lark-parser/lark | TBD | yes | task lock | grammar loader; parse tree; visitor/transformer | TBD | accepted | 3 tasks |
| vibe_app | sources/vibe_app/ | TBD | yes | task lock | csv transform; ORM query AST; plugin registry; pricing rules; rules engine; session registry; YAML bootstrap | TBD | accepted | 7 curated tasks |
| all single-task or two-task sources | See task inventory below | TBD | yes | task lock | parsers, validators, serializers, config loaders, data models, CLI core logic | TBD | accepted | Full source-level scoring TODO |

TODO: expand this repository pool into one row per source with LOC and repository score. The task inventory below is the current source of truth for accepted Python tasks.

## Task Inventory

| Task ID | Repo | Commit | Feature | Type | Difficulty | Ref LOC | Files | Status | Notes |
|---|---|---|---|---|---|---:|---:|---|---|
| aiohttp__url_params_core__hard3_001 | aiohttp | 649887ca8604 | build_url normalize_headers | data_model_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| alembic__revision_map_core__hard3_001 | alembic | c88fa5afaf2b | RevisionMap graph, branch labels, and head resolution | data_model_coupling | hard | TBD | 6 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| apscheduler__cron_trigger_core__hard3_001 | apscheduler | 4de063392ff5 | Cron trigger next-fire-time state | parser_state_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash B-tier |
| arrow__parse_format_core__001 | arrow | 1.2.3-installed-snapshot | Arrow parse, format, and humanize subset | parser_state_coupling | hard | TBD | 8 | valid | current `benchmark/tasks` metadata |
| astroid__nodes_core__001 | astroid | 2.14.2-installed-snapshot | Astroid parse and nodes subset | data_model_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| attrs__validators_core__001 | attrs | 23.1.0 | attrs field validators | data_model_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| babel__plural_core__001 | babel | 2.11.0-installed-snapshot | CLDR plural rules subset | third_party_dependency_coupling | hard | TBD | 11 | valid | current `benchmark/tasks` metadata |
| bidict__bidirectional_map_core__001 | bidict | 393bcfdc8edb | Bidirectional mapping core | data_model_coupling | hard | TBD | 11 | valid | current `benchmark/tasks` metadata |
| bleach__sanitize_core__001 | bleach | 4.1.0-installed-snapshot | HTML sanitizer clean core | parser_state_coupling | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| boltons__iterutils_core__001 | boltons | 23.0.0-installed-snapshot | Iterutils iterator toolkit | data_model_coupling | hard | TBD | 1 | valid | current `benchmark/tasks` metadata |
| build__pyproject_backend_core__hard3_001 | build | 6c03264d186c | PEP 517 build-system table validation | data_model_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash B-tier |
| cachetools__cache_eviction_core__001 | cachetools | 48284d73d0a8 | Cache eviction core | data_model_coupling | hard | TBD | 3 | valid | current `benchmark/tasks` metadata |
| cattrs__structure_core__001 | cattrs | 5dc43b3f3887 | Structure/unstructure core | data_model_coupling | hard | TBD | 13 | valid | current `benchmark/tasks` metadata |
| celery__signal_dispatch_core__hard3_001 | celery | 201573a11fb8 | Signal registry and receiver dispatch | framework_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash B-tier |
| cerberus__schema_validate_core__001 | cerberus | f2221c5a901b | Schema validation core | data_model_coupling | hard | TBD | 6 | valid | current `benchmark/tasks` metadata |
| chameleon__template_compile_core__001 | chameleon | 4.6.0-installed-snapshot | ZPT template compile and render | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| click__lazy_command_core__hard3_001 | click | 16fc00e2f4a2 | LazyCommandCollection | framework_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| click__option_parser__001 | click | 8.1.7-installed-snapshot | Command line option parsing and invocation | framework_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| configobj__roundtrip_config_core__001 | configobj | b7707c94c031 | INI-like config round-trip and configspec validation | config_environment_coupling | hard | TBD | 3 | valid | current `benchmark/tasks` metadata |
| cookiecutter__repo_finder_core__hard3_001 | cookiecutter | c88fbe921c97 | RepoFinder | resource_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| coverage__config_merge_core__001 | coveragepy | f0dcf65f4712 | Run-section config merge | config_environment_coupling | hard | TBD | 6 | valid | current `benchmark/tasks` metadata |
| coverage__glob_matcher_core__001 | coveragepy | f0dcf65f4712 | Glob matcher core | resource_coupling | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| coverage__path_remap_core__001 | coveragepy | f0dcf65f4712 | Combine path remap | resource_coupling | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| coverage__report_core__001 | coveragepy | f0dcf65f4712 | Cobertura XML report writer | config_environment_coupling | hard | TBD | 12 | valid | current `benchmark/tasks` metadata |
| coverage__source_selection_core__001 | coveragepy | f0dcf65f4712 | Source/include/omit selection | config_environment_coupling | hard | TBD | 9 | valid | current `benchmark/tasks` metadata |
| croniter__cron_parse_core__001 | croniter | dc04395e2291 | Cron expression parse and next/prev iteration | parser_state_coupling | hard | TBD | 2 | valid | current `benchmark/tasks` metadata |
| dataclasses_json__serde_core__001 | dataclasses-json | dc63902eeb5e | Dataclass JSON serde core | data_model_coupling | hard | TBD | 8 | valid | current `benchmark/tasks` metadata |
| dateutil__zone_resolver_core__hard3_001 | dateutil | 48bd1af97e71 | ZoneResolver | resource_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| deepdiff__deep_compare_core__001 | deepdiff | 9.1.0-installed-snapshot | DeepDiff path and exclude subset | data_model_coupling | hard | TBD | 8 | valid | current `benchmark/tasks` metadata |
| diskcache__eviction_policy_core__hard3_001 | diskcache | ebfa37cd99d7 | EvictionPolicyPlanner | resource_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| distlib__wheel_metadata_core__hard3_001 | distlib | 454a87c64f0b | Resource finder and wheel RECORD path normalization | resource_coupling | hard | TBD | 3 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| dynaconf__settings_merge_core__001 | dynaconf | 3.3.1-installed-snapshot | Layered settings merge | config_environment_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| email_validator__validate_core__001 | email-validator | b73d010bb3db | Email syntax validation core | parser_state_coupling | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| environs__typed_env_core__001 | environs | 97f9b7065c75 | Typed environment variable parsing | config_environment_coupling | hard | TBD | 4 | valid | current `benchmark/tasks` metadata |
| faker__provider_core__001 | Faker | 40.23.0-installed-snapshot | Single-locale Faker providers | resource_coupling | hard | TBD | 24 | valid | current `benchmark/tasks` metadata |
| flake8__plugin_options_core__hard3_001 | flake8 | bb943328eff3 | Plugin option registration and checker selection | framework_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| fs__url_opener_core__hard3_001 | fs | 77a8562785fc | parse_fs_url FSOpenerRegistry | resource_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| fsspec__url_chain_core__hard3_001 | fsspec | 0907962e6b94 | url_to_fs | resource_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| glom__spec_eval_core__hard3_001 | glom | 6fd41340f305 | Spec evaluation with Coalesce, T, and error paths | parser_state_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| h11__message_parse_core__001 | h11 | 0.14.0-installed-snapshot | HTTP/1.1 message parse and state machine | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| h2__frame_parse_core__001 | h2 | 4.3.0-installed-snapshot | HTTP/2 frame parse and buffer | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| hatch__project_metadata_core__hard3_001 | hatch | 19ced89249f2 | normalize_project_metadata select_environment | data_model_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| httpx__request_model_core__001 | httpx | 326b9431c761 | HTTP request model and offline request builder | data_model_coupling | hard | TBD | 8 | valid | current `benchmark/tasks` metadata |
| humanize__naturaltime_core__001 | humanize | 4.15.0-installed-snapshot | Humanize natural time and delta formatting | data_model_coupling | hard | TBD | 4 | valid | current `benchmark/tasks` metadata |
| importlib_metadata__entry_points_core__001 | importlib_metadata | 7.0.1-installed-snapshot | Entry point discovery and selection | config_environment_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| importlib_resources__traversable_tree_core__hard3_001 | importlib_resources | 1d554758b0cb | Traversable resource tree and text/binary reader | resource_coupling | hard | TBD | 7 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| installer__wheel_record_core__hard3_001 | installer | c18863d235a9 | parse_wheel_record find_dist_info | resource_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| intervaltree__interval_tree_core__001 | intervaltree | 1bc406e1f441 | IntervalTree core | data_model_coupling | hard | TBD | 3 | valid | current `benchmark/tasks` metadata |
| isodate__duration_parse_core__001 | isodate | 0.7.2-installed-snapshot | ISO8601 duration parse and format | parser_state_coupling | hard | TBD | 9 | valid | current `benchmark/tasks` metadata |
| isort__settings_resolver_core__hard3_001 | isort | fd8bd075176d | Settings/profile resolution and skip matching | config_environment_coupling | hard | TBD | 6 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| jinja2__compile_render_core__001 | jinja2 | 15206881c006 | Jinja2 compile and render core | framework_coupling | hard | TBD | 17 | valid | current `benchmark/tasks` metadata |
| jinja2__extensions_core__001 | jinja2 | 15206881c006 | Jinja2 extension loading | framework_coupling | hard | TBD | 18 | valid | current `benchmark/tasks` metadata |
| jinja2__filters_tests_core__001 | jinja2 | 15206881c006 | Jinja2 filters and tests core | framework_coupling | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| jinja2__lexer_parser_core__001 | jinja2 | 15206881c006 | Jinja2 lexer and parser core | parser_state_coupling | hard | TBD | 8 | valid | current `benchmark/tasks` metadata |
| jinja2__loader_inheritance_core__001 | jinja2 | 15206881c006 | Jinja2 loader and inheritance core | framework_coupling | hard | TBD | 7 | valid | current `benchmark/tasks` metadata |
| json_logic__evaluator_core__hard3_001 | json_logic | 5fda9125eab4 | JSON logic evaluator with variable resolution | parser_state_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| json5__parse_core__001 | json5 | 0.9.25-installed-snapshot | JSON5 parse and loads | parser_state_coupling | hard | TBD | 4 | valid | current `benchmark/tasks` metadata |
| jsonpath_ng__expression_eval_core__001 | jsonpath-ng | e59ead334ac4 | JSONPath parse, find, and update core | parser_state_coupling | hard | TBD | 9 | valid | current `benchmark/tasks` metadata |
| jsonpointer__resolve_core__001 | jsonpointer | 5998f951dcc5 | JSON Pointer resolve and set | parser_state_coupling | hard | TBD | 1 | valid | current `benchmark/tasks` metadata |
| jsonschema__validator_core__001 | jsonschema | 4.23.0-installed-snapshot | JSON Schema Draft 2020-12 validation core | data_model_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| jupyter_core__paths_resolver_core__hard3_001 | jupyter_core | ad6b4aea233a | Jupyter config/data/runtime path resolution | config_environment_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| jupyter_server__extension_config_core__hard3_001 | jupyter_server | c8bbb1a77a1d | Server extension discovery and enable/disable config merge | framework_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| keyring__backend_select_core__hard3_001 | keyring | 7603e7cadc25 | Backend discovery, priority sorting, and failover selection | framework_coupling | hard | TBD | 7 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| lark__grammar_loader_core__001 | lark | 1.3.1-installed-snapshot | Grammar file loading | resource_coupling | hard | TBD | 34 | valid | current `benchmark/tasks` metadata |
| lark__parse_tree_core__001 | lark | 1.2.2 | LALR parse tree core | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| lark__visitor_transform_core__001 | lark | 1.2.2 | Parse tree visitor and transformer | data_model_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| license_expression__policy_core__hard3_001 | license_expression | 2efada20a058 | License expression parse and policy evaluation | parser_state_coupling | hard | TBD | 4 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| mako__lexer_expression_core__001 | mako | d58a9208fd62 | Mako template lexer and expression parse core | parser_state_coupling | hard | 2782 | 10 | valid | current `benchmark/tasks` metadata |
| markdown__extensions_core__001 | Markdown | 3.7-installed-snapshot | Markdown tables and footnotes extensions | parser_state_coupling | hard | TBD | 15 | valid | current `benchmark/tasks` metadata |
| markdown_it__commonmark_render__001 | markdown-it-py | 2.2.0-installed-snapshot | CommonMark block/inline parsing and HTML rendering | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| marshmallow__schema_core__001 | marshmallow | 4.3.0-installed-snapshot | Schema load and dump | data_model_coupling | hard | TBD | 15 | valid | current `benchmark/tasks` metadata |
| mkdocs__plugin_config_core__hard3_001 | mkdocs | 2862536793b3 | Plugin config loading and event dispatch plan | framework_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| msgpack__pack_unpack_core__001 | msgpack-python | 2de627311fb1 | MessagePack pack/unpack core | parser_state_coupling | hard | 1019 | 4 | valid | current `benchmark/tasks` metadata |
| multidict__multidict_mutation_core__hard3_001 | multidict | 2aed5c21c349 | Case-insensitive multidict mutation and proxy behavior | data_model_coupling | hard | TBD | 4 | valid | promoted from batch3_pilot 2026-07-08; Flash B-tier |
| networkx__dag_topo_core__001 | networkx | 3.3-curated-dag-snapshot | DAG topological sorting | data_model_coupling | hard | TBD | 26 | valid | current `benchmark/tasks` metadata |
| packaging__requirement_marker_specifier__001 | packaging | 24.1-installed-snapshot | Python package requirement, marker, specifier, and version semantics | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| parsel__selector_namespace_core__hard3_001 | parsel | 05b3d37bf292 | Selector namespaces | data_model_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| parso__python_parse_core__001 | parso | 0.8.3-installed-snapshot | Python parser grammar core | parser_state_coupling | hard | TBD | 26 | valid | current `benchmark/tasks` metadata |
| passlib__hash_context_core__001 | passlib | 1.7.4-installed-snapshot | CryptContext hash and verify | data_model_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| pathvalidate__sanitize_core__001 | pathvalidate | 1ca0a50fce51 | Filename and filepath sanitization core | config_environment_coupling | hard | TBD | 9 | valid | current `benchmark/tasks` metadata |
| pendulum__parse_format_core__001 | pendulum | b99bd1468b55 | Datetime parse, format, and duration core | parser_state_coupling | hard | 4976 | 28 | valid | current `benchmark/tasks` metadata |
| phonenumbers__parse_format_core__001 | phonenumbers | 9.0.33-installed-snapshot | Phone number parse and format | resource_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| platformdirs__app_dirs_core__hard3_001 | platformdirs | 4bd7bb307292 | User/cache/config/data path resolver | config_environment_coupling | hard | TBD | 6 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| pluggy__hook_call_order__001 | pluggy | 1.0.0-installed-snapshot | Hook specification, registration, and call ordering | framework_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| pluggy__hook_wrapper_core__hard3_001 | pluggy | 6b0f3293895e | HookCaller historic wrapper ordering | framework_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| pluggy__hook_specs_core__001 | pluggy | 1.0.0-installed-snapshot | Hook specification validation and discovery | framework_coupling | hard | TBD | 7 | valid | current `benchmark/tasks` metadata |
| poetry_core__dependency_groups_core__hard3_001 | poetry_core | 5de24118d23a | PEP 621 metadata and dependency group resolver | data_model_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| pydantic__field_validator_core__hard3_001 | pydantic | 652a61ce4f9d | field_validator before/after and structured ValidationError behavior | data_model_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-11; Docker reference pass; Flash rerun public-pass/hidden-fail on structured error field metadata, extraction ratio 0.148390 |
| pydantic_settings__env_source_core__001 | pydantic-settings | 2.14.2-installed-snapshot | Environment settings source | config_environment_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| pydantic_v1__validation_error_core__001 | pydantic | 5ebcdc13b83f | BaseModel validation and structured ValidationError core | framework_coupling | hard | TBD | 15 | valid | current `benchmark/tasks` metadata |
| pyramid__configurator_action_core__hard3_001 | pyramid | 5b13e4a61b47 | Configurator action conflict resolver | framework_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| pygments__formatter_core__001 | pygments | 2.15.1 | HTML formatter core | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| pygments__lexer_core__001 | pygments | 2.15.1 | Regex lexer core | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| pytest__fixture_resolve_core__001 | pytest | b55ab2aabb68 | pytest fixture name resolution | framework_coupling | hard | TBD | 1 | valid | current `benchmark/tasks` metadata |
| pytest__ini_markers_core__001 | pytest | b55ab2aabb68 | pytest ini markers parsing | config_environment_coupling | hard | TBD | 2 | valid | current `benchmark/tasks` metadata |
| pytest__marker_registry_core__hard3_001 | pytest | 83b022078855 | Marker registry configuration and plugin marker merge | framework_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-11; Docker reference pass; Flash public-pass/hidden-fail on documented `merge_plugin_markers` behavior |
| pytest__mark_expression_core__001 | pytest | b55ab2aabb68 | pytest mark expression evaluator | parser_state_coupling | hard | TBD | 1 | valid | current `benchmark/tasks` metadata |
| pytest__skipif_eval_core__001 | pytest | b55ab2aabb68 | pytest skipif condition evaluator | framework_coupling | hard | TBD | 1 | valid | current `benchmark/tasks` metadata |
| python_box__config_box_core__001 | python-box | 7.4.1-installed-snapshot | ConfigBox dot-access config transforms | data_model_coupling | hard | TBD | 3 | valid | current `benchmark/tasks` metadata |
| python_dateutil__relativedelta_core__001 | python-dateutil | 1ae807774053 | relativedelta arithmetic core | data_model_coupling | hard | TBD | 2 | valid | current `benchmark/tasks` metadata |
| python_dateutil__rrule_core__001 | python-dateutil | 1ae807774053 | iCalendar recurrence (rrule) core | parser_state_coupling | hard | TBD | 3 | valid | current `benchmark/tasks` metadata |
| python_dotenv__env_parse_core__001 | python-dotenv | 751f8c148222 | Dotenv parse and set_key core | config_environment_coupling | hard | TBD | 3 | valid | current `benchmark/tasks` metadata |
| python_frontmatter__roundtrip_core__001 | python-frontmatter | dc7c0af5466b | YAML front matter round-trip | parser_state_coupling | hard | TBD | 4 | valid | current `benchmark/tasks` metadata |
| python_multipart__form_parse_core__001 | python-multipart | 98080c5de45b | Multipart form-data parse core | parser_state_coupling | hard | 1218 | 4 | valid | current `benchmark/tasks` metadata |
| pyyaml__safe_load_dump__001 | PyYAML | 6.0.1-installed-snapshot | Safe YAML load and dump | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| readme_renderer__content_type_core__hard3_001 | readme_renderer | 84183e882684 | Content-type parsing and renderer selection | data_model_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-11; Docker reference pass; Flash packaging/over-copy failure from undeclared `nh3` dependency |
| redis__resp_parser_core__001 | redis | 8.0.1-installed-snapshot | RESP2/RESP3 wire parser | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| referencing__json_schema_refs_core__001 | referencing | 0.30.2-installed-snapshot | JSON Schema $ref resolution | data_model_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| requests_cache__cache_key_core__hard3_001 | requests_cache | df44b695a314 | HTTP request cache key and expiration policy | third_party_dependency_coupling | hard | TBD | 6 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| responses__request_matcher_core__hard3_001 | responses | 983a4975c969 | Request matcher registry and call history | third_party_dependency_coupling | hard | TBD | 3 | valid | promoted from batch3_pilot 2026-07-11; Docker reference pass; saved Flash submission public-pass/hidden-fail on documented `once=True` consumption behavior |
| returns__result_pipeline_core__hard3_001 | returns | b158f518a6a3 | Result Success Failure safe | data_model_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| rfc3986__uri_parse_core__001 | rfc3986 | 2.0.0-installed-snapshot | RFC3986 URI parse, build, and validate subset | parser_state_coupling | hard | TBD | 10 | valid | current `benchmark/tasks` metadata |
| rich__markup_parse_core__001 | rich | 13.7.1-installed-snapshot | Console markup parsing | parser_state_coupling | hard | TBD | 79 | valid | current `benchmark/tasks` metadata |
| ruamel_yaml__roundtrip_core__001 | ruamel.yaml | 0.18.6-installed-snapshot | YAML roundtrip with comments | parser_state_coupling | hard | TBD | 29 | valid | current `benchmark/tasks` metadata |
| schema__nested_validate_core__hard3_001 | schema | 310a1239b62f | Schema Optional Or And | data_model_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| scrapy__item_loader_core__hard3_001 | scrapy | dd10cb8e9a98 | Item loader processor registry | framework_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| setuptools_scm__version_normalize_core__hard3_001 | setuptools_scm | 5b91e2faf007 | version_from_scm | data_model_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| sortedcontainers__sorted_list_core__001 | sortedcontainers | a1f52d6713dd | SortedList core | data_model_coupling | hard | TBD | 1 | valid | current `benchmark/tasks` metadata |
| sphinx__extension_registry_core__hard3_001 | sphinx | c1b618c559e6 | Directive/role registry and extension setup loader | framework_coupling | hard | TBD | 3 | valid | promoted from batch3_pilot 2026-07-11; Docker reference pass; Flash Python 3.11 packaging failure from Python 3.12-only type alias syntax |
| sqlalchemy__event_dispatch_core__hard3_001 | sqlalchemy | d59159ca08cd | Event registry dispatch core | framework_coupling | hard | TBD | 3 | valid | promoted from batch3_pilot 2026-07-08; Flash B-tier |
| starlette__route_matching_core__hard3_001 | starlette | 5174d4c8358a | Route matching and URL path convertor registry | framework_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| sqlparse__format_filters_core__001 | sqlparse | f80af6a4007f | SQL format and filters core | parser_state_coupling | hard | TBD | 19 | valid | current `benchmark/tasks` metadata |
| sqlparse__parse_format_core__001 | sqlparse | f80af6a4007f | SQL parse, split, and format core | parser_state_coupling | hard | 2930 | TBD | valid | current `benchmark/tasks` metadata |
| sqlparse__parse_split_core__001 | sqlparse | f80af6a4007f | SQL parse and split core | parser_state_coupling | hard | TBD | 12 | valid | current `benchmark/tasks` metadata |
| sqlparse__token_tree_core__001 | sqlparse | f80af6a4007f | SQL token tree navigation core | parser_state_coupling | hard | TBD | 12 | valid | current `benchmark/tasks` metadata |
| stevedore__extension_manager_core__hard3_001 | stevedore | 8550c66a2e774f97e2f8459265ed3ea8017603f1 | ExtensionManager entry point discovery and loading | framework_coupling | hard | TBD | 5 | valid | promoted from batch3_pilot 2026-07-08; Flash B-tier |
| tabulate__table_format_core__001 | tabulate | 268615a5c27d | Table formatting core | data_model_coupling | hard | 2311 | 1 | valid | current `benchmark/tasks` metadata |
| tenacity__retry_state_core__hard3_001 | tenacity | b2cd0274c67610d615019ab4745f521504a0576d | Retry state machine with stop/wait/retry predicates | data_model_coupling | hard | TBD | 5 | valid | promoted from batch3_pilot 2026-07-08; Flash B-tier |
| tomlkit__roundtrip_document__001 | tomlkit | 9ac3f98214db | TOML document parse and round-trip editing | data_model_coupling | hard | 4528 | 12 | valid | current `benchmark/tasks` metadata |
| tox__factor_expression_core__hard3_001 | tox | 5458a28f15a3 | Environment factor expression and ini filtering | parser_state_coupling | hard | TBD | 1 | valid | promoted from batch3_pilot 2026-07-08; Flash B-tier |
| trafaret__validation_rules_core__hard3_001 | trafaret | 4ac577155c93 | Composable trafaret validation rules | data_model_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| transitions__state_machine_core__hard3_001 | transitions | bd42b38f3627 | Hierarchical state machine transition core | data_model_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| typer__command_parser_core__001 | typer | 0.20.0-installed-snapshot | Typer command parser and CLI runner | framework_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| urllib3__retry_backoff_core__001 | urllib3 | 2f68c5363ef6 | Retry backoff policy core | config_environment_coupling | hard | TBD | 3 | valid | current `benchmark/tasks` metadata |
| virtualenv__interpreter_spec_core__hard3_001 | virtualenv | 57c8dc69a908 | parse_spec match_version | resource_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| vibe_app__csv_transform_core__001 | vibe_app | curated | CSV transform pipeline | legacy_vibe_clutter | hard | TBD | 14 | valid | current `benchmark/tasks` metadata |
| vibe_app__orm_query_ast_core__001 | vibe_app | curated | ORM query builder and SQL AST | framework_coupling | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| vibe_app__plugin_registry_core__001 | vibe_app | curated | Plugin registry and metaclass discovery | legacy_vibe_clutter | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| vibe_app__pricing_rules_core__001 | vibe_app | curated | Pricing rules engine | legacy_vibe_clutter | hard | TBD | 7 | valid | current `benchmark/tasks` metadata |
| vibe_app__rules_engine_core__001 | vibe_app | curated | Business rules engine | legacy_vibe_clutter | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| vibe_app__session_registry_core__001 | vibe_app | curated | Session token registry | legacy_vibe_clutter | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| vibe_app__yaml_config_bootstrap__001 | vibe_app | curated | YAML config bootstrap | legacy_vibe_clutter | hard | TBD | 4 | valid | current `benchmark/tasks` metadata |
| voluptuous__schema_validate_core__001 | voluptuous | 87825d6dbdab | Schema validation core | data_model_coupling | hard | TBD | 5 | valid | current `benchmark/tasks` metadata |
| websockets__handshake_parse_core__001 | websockets | d4303a5d3e37 | WebSocket HTTP upgrade handshake parsing | parser_state_coupling | hard | TBD | 7 | valid | current `benchmark/tasks` metadata |
| werkzeug__routing_core__001 | werkzeug | 3.0.3-installed-snapshot | URL routing map and adapter | framework_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| wheel__metadata_normalize_core__hard3_001 | wheel | 197012dcb8a9 | Wheel metadata normalization helpers | data_model_coupling | hard | TBD | 2 | valid | promoted from batch3_pilot 2026-07-08; Flash public-only hard calibration |
| wsproto__frame_parse_core__001 | wsproto | 1.3.2-installed-snapshot | WebSocket frame protocol | parser_state_coupling | hard | TBD | TBD | valid | current `benchmark/tasks` metadata |
| xmltodict__xml_parse_core__001 | xmltodict | 966b903e4441 | XML parse and unparse core | parser_state_coupling | hard | 566 | 1 | valid | current `benchmark/tasks` metadata |
| yamale__schema_validate_core__hard3_001 | yamale | c203d14bface | YAML schema rule validation core | data_model_coupling | hard | TBD | 4 | valid | promoted from batch3_pilot 2026-07-11; Docker reference pass; saved Flash submission public-pass/hidden-fail on non-strict bool coercion with extraction ratio 1.298456 |
| yarl__url_model_core__001 | yarl | b0d27e478c54 | URL parse, join, query, and path model | parser_state_coupling | hard | TBD | 7 | valid | current `benchmark/tasks` metadata |

## TODO

- Compute repository LOC and per-repo score for the repository pool.
- Populate `Ref LOC` consistently from oracle/reference data or remove the column from future canonical inventory.
- Add difficulty audit status separate from metadata difficulty.
- Link each task to its design note under `docs/task_designs/` after the docs index is updated.
