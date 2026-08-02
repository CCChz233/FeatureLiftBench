# Python-200 Balance Design

Policy: `python200-balance-20260801-v2`
Frozen baseline: `846b814726217623fa205cb7688bee61e6c21c43efda1ebd05e79b5ed8cb4fbd` (150 tasks)

This is a selection-design artifact. It does not promote tasks or modify the frozen Python-150 baseline.

## Decision Summary

- keep: 40
- redesign: 0
- replacement_selected: 10
- replaced_candidates: 10
- replacement_slots: 10
- balance checks: PASS
- promotion ready: false

## Proposed Lift Distribution

| label | count | share |
| --- | ---: | ---: |
| Adapted | 89 | 44.5% |
| Composite | 43 | 21.5% |
| Direct | 68 | 34.0% |

## Proposed Feature-Family Distribution

| label | count | share |
| --- | ---: | ---: |
| algorithm_data_structure | 17 | 8.5% |
| cache_retry_policy | 12 | 6.0% |
| config_resolve_discover | 21 | 10.5% |
| parse_tokenize_decode | 36 | 18.0% |
| protocol_state_transition | 16 | 8.0% |
| registry_plugin_dispatch | 25 | 12.5% |
| resource_metadata_loading | 18 | 9.0% |
| serialize_format_render | 24 | 12.0% |
| validate_normalize_construct | 21 | 10.5% |
| workflow_session_orchestration | 10 | 5.0% |

## Proposed Primary-Coupling Distribution

| label | count | share |
| --- | ---: | ---: |
| config_environment_coupling | 22 | 11.0% |
| data_model_coupling | 60 | 30.0% |
| framework_coupling | 35 | 17.5% |
| parser_state_coupling | 55 | 27.5% |
| resource_coupling | 21 | 10.5% |
| third_party_dependency_coupling | 7 | 3.5% |

## Task Decisions

| task_id | decision | flags |
| --- | --- | --- |
| `anytree__tree_resolve_render_core__001` | keep | - |
| `automat__methodical_workflow_core__001` | replacement_selected | - |
| `boolean_py__expr_simplify_core__001` | keep | - |
| `cachecontrol__heuristic_store_core__001` | keep | - |
| `cacheout__ttl_policy_core__001` | replacement_selected | - |
| `cachier__memoize_backend_core__001` | replacement_selected | - |
| `configupdater__ini_roundtrip_core__001` | keep | - |
| `dateparser__parse_settings_pipeline_core__001` | keep | - |
| `fasteners__process_lock_core__001` | keep | - |
| `flask_cors__cors_options_core__001` | keep | - |
| `flask_login__session_guard_core__001` | keep | - |
| `freezegun__freeze_time_core__001` | keep | - |
| `ftfy__fix_text_core__001` | keep | - |
| `furl__url_mutate_core__001` | keep | - |
| `huey__task_schedule_core__001` | keep | - |
| `hyperlink__url_parse_core__001` | keep | - |
| `icalendar__component_roundtrip_core__001` | keep | - |
| `invoke__collection_context_core__001` | keep | - |
| `joserfc__jwt_claims_core__001` | keep | - |
| `jsonpickle__handler_roundtrip_core__001` | keep | - |
| `langcodes__language_metadata_core__001` | replacement_selected | - |
| `more_itertools__recipes_core__001` | keep | - |
| `omegaconf__merge_interpolate_core__001` | keep | - |
| `packageurl__purl_parse_core__001` | keep | - |
| `portalocker__file_lock_core__001` | keep | - |
| `publicsuffixlist__metadata_lookup_core__001` | replacement_selected | - |
| `puremagic__signature_resource_core__001` | replacement_selected | - |
| `pyee__event_workflow_core__001` | replacement_selected | - |
| `pyjwt__encode_decode_core__001` | keep | - |
| `pyotp__totp_hotp_core__001` | keep | - |
| `pyparsing__grammar_compose_core__001` | keep | - |
| `pyrsistent__pmap_pvector_core__001` | keep | - |
| `python_crontab__cron_item_core__001` | keep | - |
| `python_json_logger__json_formatter_core__001` | keep | - |
| `python_statemachine__json_workflow_core__001` | replacement_selected | - |
| `semver__version_core__001` | keep | - |
| `sqlglot__parse_transpile_core__001` | keep | - |
| `stamina__retry_context_core__001` | replacement_selected | - |
| `strictyaml__schema_load_core__001` | keep | - |
| `structlog__processor_chain_core__001` | keep | - |
| `tinycss2__stylesheet_roundtrip_core__001` | keep | - |
| `tinydb__query_storage_core__001` | keep | - |
| `tldextract__suffix_resolve_core__001` | keep | - |
| `toolz__compose_pipe_core__001` | keep | - |
| `typeguard__check_type_pipeline_core__001` | keep | - |
| `unidiff__patch_hunk_core__001` | keep | - |
| `uritools__uri_join_normalize_core__001` | keep | - |
| `vcrpy__cassette_match_core__001` | keep | - |
| `venusian__scan_dispatch_core__001` | replacement_selected | - |
| `watchdog__observer_dispatch_core__001` | keep | - |

## Replacement Slots

- `cache-direct-config-01`: Direct / cache_retry_policy / config_environment_coupling - A deterministic cache or retry policy with explicit defaults and no service dependency.
- `cache-direct-third-party-02`: Direct / cache_retry_policy / third_party_dependency_coupling - A bounded policy feature with one allowlisted pure-Python dependency and offline wheels.
- `cache-composite-third-party-03`: Composite / cache_retry_policy / third_party_dependency_coupling - Compose keying, expiration, and retry/eviction decisions without a live cache service.
- `workflow-composite-framework-01`: Composite / workflow_session_orchestration / framework_coupling - A deterministic in-process workflow with explicit state transitions and no worker service.
- `workflow-composite-config-02`: Composite / workflow_session_orchestration / config_environment_coupling - A session or workflow planner whose environment/config inputs can be frozen in tests.
- `workflow-composite-third-party-03`: Composite / workflow_session_orchestration / third_party_dependency_coupling - An offline orchestration pipeline using one allowlisted pure-Python dependency.
- `resource-direct-01`: Direct / resource_metadata_loading / resource_coupling - Load and resolve a small redistributable metadata resource with deterministic fallbacks.
- `resource-direct-02`: Direct / resource_metadata_loading / resource_coupling - A separate resource-backed lookup feature with pinned local data and no network refresh.
- `resource-composite-third-party-03`: Composite / resource_metadata_loading / third_party_dependency_coupling - Compose local metadata loading and resolution around one allowlisted pure-Python dependency.
- `registry-composite-framework-01`: Composite / registry_plugin_dispatch / framework_coupling - A registry plus selection/dispatch flow with deterministic in-process plugins.

## Checks

- PASS `baseline_task_count`: expected 150, found 150
- PASS `selected_task_count`: expected 50, found 50
- PASS `selected_task_ids_unique`: unique=50 selected=50
- PASS `no_baseline_overlap`: overlap=[]
- PASS `replacement_slots_match_candidates`: slots=10 candidates=10
- PASS `replacement_assignments_complete`: assignments=10 candidates=10 slots=10
- PASS `replacement_tasks_selected`: selected_replacements=10 selected_candidates=[]
- PASS `proposed_expansion_count`: proposed=50
- PASS `lift_type_share:Direct`: share=34.0% bounds=30.0%-36.0%
- PASS `lift_type_share:Adapted`: share=44.5% bounds=38.0%-45.0%
- PASS `lift_type_share:Composite`: share=21.5% bounds=20.0%-28.0%
- PASS `feature_family_share:algorithm_data_structure`: share=8.5% bounds=5.0%-18.0%
- PASS `feature_family_share:cache_retry_policy`: share=6.0% bounds=5.0%-18.0%
- PASS `feature_family_share:config_resolve_discover`: share=10.5% bounds=5.0%-18.0%
- PASS `feature_family_share:parse_tokenize_decode`: share=18.0% bounds=5.0%-18.0%
- PASS `feature_family_share:protocol_state_transition`: share=8.0% bounds=5.0%-18.0%
- PASS `feature_family_share:registry_plugin_dispatch`: share=12.5% bounds=5.0%-18.0%
- PASS `feature_family_share:resource_metadata_loading`: share=9.0% bounds=5.0%-18.0%
- PASS `feature_family_share:serialize_format_render`: share=12.0% bounds=5.0%-18.0%
- PASS `feature_family_share:validate_normalize_construct`: share=10.5% bounds=5.0%-18.0%
- PASS `feature_family_share:workflow_session_orchestration`: share=5.0% bounds=5.0%-18.0%
- PASS `entanglement_share:config_environment_coupling`: share=11.0% bounds=8.0%-18.0%
- PASS `entanglement_share:data_model_coupling`: share=30.0% bounds=15.0%-30.0%
- PASS `entanglement_share:framework_coupling`: share=17.5% bounds=12.0%-22.0%
- PASS `entanglement_share:parser_state_coupling`: share=27.5% bounds=15.0%-30.0%
- PASS `entanglement_share:resource_coupling`: share=10.5% bounds=8.0%-18.0%
- PASS `entanglement_share:third_party_dependency_coupling`: share=3.5% bounds=3.0%-12.0%

Next gate: Run offline reference, isolation, Docker, and lifecycle gates for the realized External-50 selection.
