# Trajectory statistics (generated)

Generated: `2026-07-13T13:13:17+00:00`

This file is generated only from `trajectory_records.csv`; do not edit percentages here by hand.

Inventory: 464 rows; primary analysis: 450; excluded supplementary rows: 14.

## Overall

| group | runs | suite pass | functional pass | public observed | P→H fail / total | env error | median ratio | median tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `all` | 450 | 218/450 (48.4%) | 220/450 (48.9%) | 351/450 (78.0%) | 98/450 (21.8%) | 62/450 (13.8%) | 0.282 | 1,705,146 |

## By model

| group | runs | suite pass | functional pass | public observed | P→H fail / total | env error | median ratio | median tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `deepseek/deepseek-v4-flash` | 150 | 91/150 (60.7%) | 93/150 (62.0%) | 141/150 (94.0%) | 48/150 (32.0%) | 2/150 (1.3%) | 0.363 | 1,649,321 |
| `openai/Qwen3-Coder-30B-A3B-Instruct` | 100 | 24/100 (24.0%) | 24/100 (24.0%) | 75/100 (75.0%) | 35/100 (35.0%) | 21/100 (21.0%) | 0.168 | 2,020,808 |
| `openai/Qwen3.6-27B-FP8` | 100 | 54/100 (54.0%) | 54/100 (54.0%) | 69/100 (69.0%) | 9/100 (9.0%) | 21/100 (21.0%) | 0.309 | 1,553,055 |
| `openai/Qwen3.6-35B-A3B-FP8` | 100 | 49/100 (49.0%) | 49/100 (49.0%) | 66/100 (66.0%) | 6/100 (6.0%) | 18/100 (18.0%) | 0.282 | 1,746,882 |

## By split

| group | runs | suite pass | functional pass | public observed | P→H fail / total | env error | median ratio | median tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `core100` | 400 | 210/400 (52.5%) | 212/400 (53.0%) | 306/400 (76.5%) | 61/400 (15.2%) | 60/400 (15.0%) | 0.261 | 1,698,568 |
| `hard50` | 50 | 8/50 (16.0%) | 8/50 (16.0%) | 45/50 (90.0%) | 37/50 (74.0%) | 2/50 (4.0%) | 0.508 | 1,771,924 |

## By task type

| group | runs | suite pass | functional pass | public observed | P→H fail / total | env error | median ratio | median tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `parser_state_coupling` | 161 | 82/161 (50.9%) | 82/161 (50.9%) | 123/161 (76.4%) | 24/161 (14.9%) | 23/161 (14.3%) | 0.307 | 1,758,497 |
| `data_model_coupling` | 113 | 50/113 (44.2%) | 52/113 (46.0%) | 81/113 (71.7%) | 21/113 (18.6%) | 18/113 (15.9%) | 0.276 | 2,206,378 |
| `framework_coupling` | 66 | 26/66 (39.4%) | 26/66 (39.4%) | 46/66 (69.7%) | 18/66 (27.3%) | 14/66 (21.2%) | 0.456 | 1,699,486 |
| `config_environment_coupling` | 51 | 24/51 (47.1%) | 24/51 (47.1%) | 45/51 (88.2%) | 18/51 (35.3%) | 6/51 (11.8%) | 0.252 | 1,352,342 |
| `resource_coupling` | 29 | 11/29 (37.9%) | 11/29 (37.9%) | 28/29 (96.6%) | 15/29 (51.7%) | 0/29 (0.0%) | 0.509 | 1,545,592 |
| `legacy_vibe_clutter` | 24 | 23/24 (95.8%) | 23/24 (95.8%) | 23/24 (95.8%) | 0/24 (0.0%) | 0/24 (0.0%) | 0.112 | 381,994 |
| `third_party_dependency_coupling` | 6 | 2/6 (33.3%) | 2/6 (33.3%) | 5/6 (83.3%) | 2/6 (33.3%) | 1/6 (16.7%) | 0.128 | 2,410,213 |

## Error-source separation

| source | affected | events | definition |
| --- | --- | --- | --- |
| `agent_reasoning_unsupported_completion_claim` | 68/450 (15.1%) | — | FinishAction asserts completion/test success but final functional gate is 0, excluding evaluator/environment errors. |
| `tool_execution_error` | 187/450 (41.6%) | 465 | OpenHands ObservationEvent has is_error=true, excluding tool-schema validation errors. |
| `harness_format_error` | 193/450 (42.9%) | 589 | Agent/Conversation error explicitly reports tool validation/schema/required-parameter failure. |
| `evaluator_environment_error` | 62/450 (13.8%) | 62 | Dependency installation, evaluator tooling, or Docker sandbox fails before a valid test outcome. |

## Primary failure labels

| label | count / 450 |
| --- | --- |
| `passed` | 220/450 (48.9%) |
| `evaluator_or_environment_error` | 62/450 (13.8%) |
| `hidden_behavior_contract_failure` | 57/450 (12.7%) |
| `hidden_interface_or_closure_failure` | 39/450 (8.7%) |
| `dependency_closure_omission` | 22/450 (4.9%) |
| `public_api_or_interface_failure` | 17/450 (3.8%) |
| `public_behavior_failure` | 11/450 (2.4%) |
| `missing_submission` | 10/450 (2.2%) |
| `isolation_or_forbidden_import_failure` | 8/450 (1.8%) |
| `build_syntax_or_version_failure` | 3/450 (0.7%) |
| `packaging_or_build_failure` | 1/450 (0.2%) |

## Extraction buckets

| bucket | known-ratio runs | functional pass | P→H fail | median ratio |
| --- | --- | --- | --- | --- |
| `under_proxy_le_0_25` | 197 | 88/197 (44.7%) | 53/197 (26.9%) | 0.132 |
| `middle_0_25_to_0_80` | 188 | 101/188 (53.7%) | 31/188 (16.5%) | 0.420 |
| `over_proxy_gt_0_80` | 55 | 31/55 (56.4%) | 14/55 (25.5%) | 0.990 |

### Under/over trajectory features

| bucket | closure plan | self tests | hidden risk | explicit finish | repeat-read affected | unsupported claim | median files | median tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `under_proxy_le_0_25` | 19/197 (9.6%) | 23/197 (11.7%) | 142/197 (72.1%) | 132/197 (67.0%) | 131/197 (66.5%) | 37/197 (18.8%) | 5.0 | 1705916.0 |
| `over_proxy_gt_0_80` | 6/55 (10.9%) | 9/55 (16.4%) | 43/55 (78.2%) | 35/55 (63.6%) | 23/55 (41.8%) | 10/55 (18.2%) | 6.0 | 1513048.0 |

## Repetition and error events

| metric | affected runs | event count | median among affected |
| --- | --- | --- | --- |
| `repeated_file_reads` | 295/450 (65.6%) | 1844 | 4.0 |
| `repeated_line_reads` | 143/450 (31.8%) | 394 | 1.0 |
| `repeated_terminal_commands` | 308/450 (68.4%) | 1446 | 3.0 |
| `tool_error_count` | 187/450 (41.6%) | 465 | 2.0 |
| `harness_format_error_count` | 193/450 (42.9%) | 589 | 2.0 |
| `agent_reasoning_error_count` | 68/450 (15.1%) | 68 | 1.0 |
| `evaluator_environment_error_count` | 62/450 (13.8%) | 62 | 1.0 |

## Auditable cases

| task | model | public | hidden | ratio | score | files | tokens | stop | primary failure | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `requests_cache__cache_key_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | false | 0.963 | 0.000 | 6 | 1,651,172 | completion_signal | `hidden_interface_or_closure_failure` | `ad2fc573-1401-4d53-8856-ab4034c217d6`<br>`eval:hidden_tests` |
| `pydantic_v1__validation_error_core__001` | `deepseek/deepseek-v4-flash` | NA | NA | 0.535 | 0.000 | 15 | 5,096,343 | step_limit_exceeded | `dependency_closure_omission` | `16766354-cedc-406d-8563-ff18729b377a`<br>`997b5fdc-5360-4686-ad4e-9d63812d4c09`<br>`dd118e51-8dc2-4e9c-b076-c3a91c83247c`<br>`70c1a821-fd37-47cd-99b6-df6fd517088c` |
| `phonenumbers__parse_format_core__001` | `deepseek/deepseek-v4-flash` | true | false | 0.426 | 0.000 | 10 | 5,142,307 | step_limit_exceeded | `hidden_interface_or_closure_failure` | `bf656a8c-c910-4f9b-8f78-05723b8a1682`<br>`27ac166f-127f-4c68-bf47-80a3d4d89e9b`<br>`bf595ff8-e45f-4f66-afc6-86533a6183b1`<br>`0cf51515-3320-4b6e-ae72-8f921be8511c` |
| `diskcache__eviction_policy_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | false | 0.042 | 0.000 | 2 | 1,497,118 | completion_signal | `hidden_interface_or_closure_failure` | `f5b4b21a-19fd-4434-bc05-d5de5cc5f52e`<br>`6a5dd66b-3680-4910-aa2c-26de02794acb`<br>`8983822d-0773-4a70-b596-104bb30fcb8b`<br>`eval:hidden_tests` |
| `click__lazy_command_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | false | 0.094 | 0.000 | 4 | 2,601,067 | completion_signal | `hidden_interface_or_closure_failure` | `8493e436-818c-4cb1-9f5e-cd46f19ed74e`<br>`13d8c1ac-7416-4e9a-9d83-9d44babba949`<br>`3a7f3fcd-bdc9-4a00-85d8-0e32c8016d0e`<br>`4b66f5b9-0288-48d3-a025-a9b594eb447c` |
| `pytest__marker_registry_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | false | 0.102 | 0.000 | 4 | 1,679,652 | completion_signal | `hidden_interface_or_closure_failure` | `af1d46e2-7746-4cdc-987a-a51865f978f2`<br>`14dbc6b4-e2ee-435d-b093-d24bb403c0a1`<br>`e16547b0-aff1-4e70-a9ac-536911810b40`<br>`03b0dc44-9d97-4a8d-804e-61cdf42d1e29` |
| `jupyter_server__extension_config_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | false | 0.598 | 0.000 | 2 | 1,020,785 | completion_signal | `hidden_interface_or_closure_failure` | `6682d720-653d-4c41-9e00-24ff374d85f1`<br>`cf06bb8e-1745-4663-97d0-10393c87192b`<br>`3e138020-326f-4bc7-9144-4387766f98f7`<br>`eval:hidden_tests` |
| `parsel__selector_namespace_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | false | 1.034 | 0.000 | 5 | 1,248,192 | explicit_finish | `hidden_interface_or_closure_failure` | `ba17601f-4bae-49b5-833a-f7ac8bb9ac9e`<br>`f9de7651-56da-42fa-af18-4f72ece24075`<br>`ecfdd1ca-b4f5-4a8c-a302-3d947930dadf`<br>`525c3a9e-dfbb-49f9-9f4d-44e1a37247bb` |
| `sqlalchemy__event_dispatch_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | true | 1.140 | 0.000 | 8 | 4,307,124 | explicit_finish | `passed` | `c46dddd1-b647-45aa-9784-4c584e29461c`<br>`ebb5381a-141c-4303-847b-b0132febea20`<br>`06778ac4-d540-49f4-98c1-574539ec120c`<br>`73e62f4b-7fe3-49a7-b393-473575b9ea84` |
| `stevedore__extension_manager_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | true | 0.879 | 0.121 | 4 | 1,113,070 | completion_signal | `passed` | `c98c6e5a-d4b1-45f8-8a7d-cde36690b202` |
| `pluggy__hook_wrapper_core__hard3_001` | `deepseek/deepseek-v4-flash` | true | false | 0.387 | 0.000 | 5 | 1,719,320 | completion_signal | `hidden_behavior_contract_failure` | `532fa682-0eea-4a3f-9258-390009b27fd0`<br>`2f60e1d2-0955-4484-941d-14ad65fe6ce5`<br>`2af74bd3-8b88-491b-9177-229e620a9c10`<br>`de336333-b4de-4cb8-ac54-52a4f932bd01` |
| `pydantic__field_validator_core__hard3_001` | `deepseek/deepseek-v4-flash` | NA | NA | NA | 0.000 | 0 | 35,316 | missing_submission_after_agent_exit | `missing_submission` | `31f49cae-d932-478e-b085-9ea747031afb`<br>`e7db6b9b-d9f9-42fe-9c7d-bef038fa8a75`<br>`7ad35608-7fc0-4456-8a66-9b09f605ec5c` |
| `coverage__config_merge_core__001` | `deepseek/deepseek-v4-flash` | true | false | 1.000 | 0.000 | 2 | 1,354,848 | explicit_finish | `hidden_behavior_contract_failure` | `89c4db31-c9c8-483e-8b1d-cf9d53395808`<br>`3b5cf3a1-ab42-4e7d-a4bb-13cf9ac4058c`<br>`eval:hidden_tests` |
| `dynaconf__settings_merge_core__001` | `deepseek/deepseek-v4-flash` | true | true | 0.178 | 0.822 | 14 | 11,474,158 | explicit_finish | `passed` | `e30b970e-e5ee-41f7-8db9-ae18dd2e177d`<br>`a2186545-7309-498a-a0e5-7f98a6b4331f`<br>`998202f5-1c38-4b58-9ac6-0a6dce5afcf0`<br>`7b53e3b4-9c8a-404b-a7f2-4b6e1ffdcfe5` |
| `sphinx__extension_registry_core__hard3_001` | `deepseek/deepseek-v4-flash` | NA | NA | 0.115 | 0.000 | 5 | 1,860,449 | completion_signal | `build_syntax_or_version_failure` | `64906364-b28d-43f3-95c9-3f58f081d8b8`<br>`03da34c1-c7d4-497f-a431-d664ba3baa2b`<br>`eval:build` |
| `readme_renderer__content_type_core__hard3_001` | `deepseek/deepseek-v4-flash` | NA | NA | 3.044 | 0.000 | 5 | 3,778,387 | completion_signal | `dependency_closure_omission` | `c5208f5e-528b-4d64-ba6d-ef42395f252b`<br>`3040bfc9-df69-4263-acf0-2e4454ec221d`<br>`f274ab53-2a2a-4bc0-9f08-0d1a68cc0b8a`<br>`c27b24cb-6d6d-4f13-a746-f5ddf3eeac11` |
| `bleach__sanitize_core__001` | `deepseek/deepseek-v4-flash` | NA | NA | 0.506 | 0.000 | 36 | 2,005,228 | completion_signal | `dependency_closure_omission` | `14a279c3-172d-486b-aad4-efec65f14628`<br>`b38c1249-27ba-425c-b459-ff3839259165`<br>`e1f713d4-1f5c-4e6d-b95d-ba08ebdb971a`<br>`a798783a-9e8e-43f8-b42f-df9167da7a13` |
| `responses__request_matcher_core__hard3_001` | `deepseek/deepseek-v4-flash` | NA | NA | 0.311 | 0.000 | 3 | 1,277,571 | completion_signal | `evaluator_or_environment_error` | `b135beca-fec3-49a3-85f1-f81db6c13e44`<br>`c0dbe9f4-bcb7-46d2-b997-1b23d35f78da`<br>`d45122ae-c345-4c36-af03-1200ca011f68`<br>`9664ab72-299d-4ba7-a400-7ccc5fff384f` |
| `yamale__schema_validate_core__hard3_001` | `deepseek/deepseek-v4-flash` | NA | NA | 1.298 | 0.000 | 16 | 2,679,835 | completion_signal | `evaluator_or_environment_error` | `ee3433b3-5447-4827-85bf-80d78e697ee8`<br>`cba1c648-5bf8-492f-824b-a9a173f14558`<br>`eval:build`<br>`eval:dependency_install_failed` |
| `pyyaml__safe_load_dump__001` | `openai/Qwen3-Coder-30B-A3B-Instruct` | true | true | 1.002 | 0.000 | 17 | 2,217,561 | explicit_finish | `isolation_or_forbidden_import_failure` | `e355fb56-3a68-4c5d-88d7-f33498675e8e`<br>`043fd0df-7da6-4c20-82da-0af4d49ca216`<br>`61e3efb5-ff31-4183-9ede-f91e33e1deb5`<br>`2d95128b-1926-44f3-a5d0-cc5502f4f82a` |
