# Python-200-prime repair ledger v2

> **Status: `frozen` · Ledger: `3eb3487d4ae387164512283b67bf4497c8dfa672a92650888d853727d03dffce`**

This is a generated view. The JSON ledger is authoritative.

## Summary

| Measure | Value |
| --- | ---: |
| Parent suite | 200 |
| Pre-repair meets standard | 168 |
| Post-repair mechanically meets standard | 200 |
| Changed tasks | 38 |
| Blocking tasks | 32 |
| Advisory-only tasks | 6 |
| C1 / C2 / C4 task counts | 21 / 12 / 6 |
| Mechanically closed changed tasks | 38 |
| Semantic reviews complete / pending | 38 / 0 |

## Claim boundary

Supported:

- All 38 changed tasks are tied to pre-repair rule findings.
- All relevant implemented gate rows pass after repair.
- All 38 changed tasks have stable three-repetition Oracle and isolation evidence in the repair gate ledger.
- All 38 repairs preserve semantic scope under AI-assisted review plus maintainer adjudication; this is not independent human gold.
- The repaired 200-task suite has a final candidate-bound Docker Oracle and freeze.

Not yet supported:

- All 200 Hidden evaluators are semantically fair.
- Predecessor Agent scores are valid for the repaired freeze.

## Changed tasks

| Task | Repair | Agent TASK changed | Evaluator changed | Mechanical | Oracle/isolation | Semantic review |
| --- | --- | --- | --- | --- | --- | --- |
| `aiohttp__url_params_core__hard3_001` | C1+C2 | yes | yes | pass | pass | pass |
| `anyio__task_group_core__001` | C4 | no | yes | pass | pass | pass |
| `apispec__plugin_documenter_core__001` | C1 | yes | yes | pass | pass | pass |
| `asttokens__token_annotate_core__001` | C1 | yes | yes | pass | pass | pass |
| `authlib__oauth2_server_core__001` | C1 | yes | yes | pass | pass | pass |
| `beaker__session_cache_core__001` | C1 | yes | yes | pass | pass | pass |
| `build__pyproject_backend_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `cachetools__cache_eviction_core__001` | C1 | yes | yes | pass | pass | pass |
| `click__lazy_command_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `configobj__roundtrip_config_core__001` | C1 | yes | yes | pass | pass | pass |
| `cookiecutter__repo_finder_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `copier__template_answers_core__001` | C4 | no | yes | pass | pass | pass |
| `dateutil__zone_resolver_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `deepdiff__deep_compare_core__001` | C1 | yes | yes | pass | pass | pass |
| `diskcache__eviction_policy_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `fs__url_opener_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `hatch__project_metadata_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `importlib_metadata__entry_points_core__001` | C1 | yes | yes | pass | pass | pass |
| `installer__wheel_record_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `intervaltree__interval_tree_core__001` | C1 | yes | yes | pass | pass | pass |
| `jsonpointer__resolve_core__001` | C1 | yes | yes | pass | pass | pass |
| `mitmproxy__url_parse_core__001` | C4 | no | yes | pass | pass | pass |
| `multidict__multidict_mutation_core__hard3_001` | C1 | yes | yes | pass | pass | pass |
| `oslo_config__opt_group_core__001` | C1 | yes | yes | pass | pass | pass |
| `packaging__requirement_marker_specifier__001` | C1 | yes | yes | pass | pass | pass |
| `pika__channel_spec_core__001` | C4 | no | yes | pass | pass | pass |
| `pre_commit__config_load_core__001` | C4 | no | yes | pass | pass | pass |
| `pylint__config_find_core__001` | C4 | no | yes | pass | pass | pass |
| `python_configuration__layered_config_core__001` | C1 | yes | yes | pass | pass | pass |
| `python_frontmatter__roundtrip_core__001` | C1 | yes | yes | pass | pass | pass |
| `readme_renderer__content_type_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `setuptools_scm__version_normalize_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `sortedcontainers__sorted_list_core__001` | C1 | yes | yes | pass | pass | pass |
| `spiffworkflow__bpmn_engine_core__001` | C1 | yes | yes | pass | pass | pass |
| `stevedore__extension_manager_core__hard3_001` | C1 | yes | yes | pass | pass | pass |
| `virtualenv__interpreter_spec_core__hard3_001` | C2 | no | no | pass | pass | pass |
| `webob__request_response_core__001` | C1 | yes | yes | pass | pass | pass |
| `websockets__handshake_parse_core__001` | C1 | yes | yes | pass | pass | pass |

## Evidence inputs

| Evidence | Path | SHA-256 |
| --- | --- | --- |
| `c1_repairs` | `experiments/validation/c1c2_repair_v2/c1_members_wrote.json` | `c3d08dc9f625db7e7aa5928c28d433869cda53e817c3daae155b0adbed01090c` |
| `c2_repairs` | `experiments/validation/c1c2_repair_v2/c2_mapping_wrote.json` | `dca7050049fde60241e893660875e5643e930f970858ea85bf7105a7656c28cb` |
| `c4_trial` | `experiments/registry/c4_overlap_trial_20260902.md` | `170179a3673dff53179a7fcda73d9886423c638f191cbd568f3b968014f4e827` |
| `maintainer_adjudication` | `artifacts/research_analysis/python200_prime/current_repair_maintainer_adjudication_v2.json` | `e1da5e4f2fa9c58211a922e6e6cdd8c865897a8e27fce0f296fe9814b1b7a90f` |
| `post_repair_gate` | `reports/benchmark_gate/python200_hard_20260903_v2_repair2/gate_report.json` | `adb94b0ff97d66c752a1f1dbc85f828c337936f25f0fbf12e4096dc9bf91504b` |
| `pre_repair_gate` | `reports/benchmark_gate/python200_hard_20260902_p1_l4l5/gate_report.json` | `a9cef91832fc3f5a9350c0512bad6ae6ebca4e2bf9db9285f500ea7a27b6f8d8` |
| `protocol` | `docs/BENCHMARK_REPAIR_PROTOCOL.md` | `dc0b7f1b9250b613ca86d66a289e9f890f697fd76241bf70343f8b6f5d7dd52f` |
| `semantic_review` | `artifacts/research_analysis/python200_prime/current_repair_semantic_review_v2_closed.json` | `c0bf94dc41165fe74a410f8d0f00ac2541f6f40294bf94396b025fb1fecbbde4` |

## Next gate

Freeze v2 is published. Paper Main/ablation scores must be collected on this freeze; predecessor Agent scores must not be transferred.
