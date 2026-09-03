# Python-200-prime repair semantic review

> **Status: `complete` · publication ready: `false`**

This is an AI-assisted semantic audit, not independent human gold.
The JSON report is authoritative.

## Summary

| Measure | Value |
| --- | ---: |
| Expected repaired tasks | 38 |
| Tasks with review attempts | 38 |
| Missing tasks | 0 |
| Scope preserved | 32 |
| Scope changed | 3 |
| Insufficient/conflicting | 3 |

## Task verdicts

| Task | Status | Repair scope | Hidden fairness |
| --- | --- | --- | --- |
| `aiohttp__url_params_core__hard3_001` | pass | scope_preserved | fair |
| `anyio__task_group_core__001` | pass | scope_preserved | fair |
| `apispec__plugin_documenter_core__001` | pass | scope_preserved | fair |
| `asttokens__token_annotate_core__001` | pass | scope_preserved | fair |
| `authlib__oauth2_server_core__001` | undetermined | scope_changed | fair |
| `beaker__session_cache_core__001` | undetermined | scope_changed | fair |
| `build__pyproject_backend_core__hard3_001` | pass | scope_preserved | fair |
| `cachetools__cache_eviction_core__001` | pass | scope_preserved | fair |
| `click__lazy_command_core__hard3_001` | pass | scope_preserved | fair |
| `configobj__roundtrip_config_core__001` | pass | scope_preserved | fair |
| `cookiecutter__repo_finder_core__hard3_001` | undetermined | scope_preserved | underdetermined |
| `copier__template_answers_core__001` | pass | scope_preserved | fair |
| `dateutil__zone_resolver_core__hard3_001` | pass | scope_preserved | fair |
| `deepdiff__deep_compare_core__001` | undetermined | scope_changed | fair |
| `diskcache__eviction_policy_core__hard3_001` | pass | scope_preserved | fair |
| `fs__url_opener_core__hard3_001` | pass | scope_preserved | fair |
| `hatch__project_metadata_core__hard3_001` | pass | scope_preserved | fair |
| `importlib_metadata__entry_points_core__001` | pass | scope_preserved | fair |
| `installer__wheel_record_core__hard3_001` | undetermined | insufficient_evidence | None |
| `intervaltree__interval_tree_core__001` | undetermined | scope_preserved | fair |
| `jsonpointer__resolve_core__001` | pass | scope_preserved | fair |
| `mitmproxy__url_parse_core__001` | pass | scope_preserved | fair |
| `multidict__multidict_mutation_core__hard3_001` | pass | scope_preserved | fair |
| `oslo_config__opt_group_core__001` | pass | scope_preserved | fair |
| `packaging__requirement_marker_specifier__001` | pass | scope_preserved | fair |
| `pika__channel_spec_core__001` | undetermined | scope_preserved | fair |
| `pre_commit__config_load_core__001` | pass | scope_preserved | fair |
| `pylint__config_find_core__001` | pass | scope_preserved | fair |
| `python_configuration__layered_config_core__001` | pass | scope_preserved | fair |
| `python_frontmatter__roundtrip_core__001` | undetermined | insufficient_evidence | None |
| `readme_renderer__content_type_core__hard3_001` | pass | scope_preserved | fair |
| `setuptools_scm__version_normalize_core__hard3_001` | pass | scope_preserved | fair |
| `sortedcontainers__sorted_list_core__001` | undetermined | scope_preserved | underdetermined |
| `spiffworkflow__bpmn_engine_core__001` | pass | scope_preserved | fair |
| `stevedore__extension_manager_core__hard3_001` | pass | scope_preserved | fair |
| `virtualenv__interpreter_spec_core__hard3_001` | pass | scope_preserved | fair |
| `webob__request_response_core__001` | undetermined | scope_preserved | fair |
| `websockets__handshake_parse_core__001` | undetermined | insufficient_evidence | None |

## Claim boundary

A positive AI review supports maintainer adjudication but does not replace the independent review required for a human-gold claim. Candidate creation remains blocked until every changed task is scope-preserved and the remaining release gates pass.
