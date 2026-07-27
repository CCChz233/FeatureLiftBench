# FeatureLiftBench Python-150 Benchmark Taxonomy Specification

> Current v2 task taxonomy. It is an analysis layer, not a release gate:
> entrypoint counts and structural closure fields remain maintainer-only
> measurements and are never exposed to the Main Agent.

## Status and evidence boundary

- Version: `v2`
- Unit of analysis: one row per task under `benchmark/tasks/*/metadata.json`
- Frozen population: 150 Python External Main tasks (`core100=100`, `hard50=50`
  retained only as construction strata)
- Excluded directory: `benchmark/tasks/iniconfig__parse_config__001` because `benchmark/manifest.json` explicitly lists it as an empty legacy directory without metadata
- Allowed evidence: task metadata, oracle manifest, source snapshot, public tests, hidden tests
- Forbidden evidence for intrinsic classification: trajectories, submissions, evaluation results, public/hidden pass status, extraction ratio, copied files, or any historical failure label

The generated table is `artifacts/research_analysis/python150_task_taxonomy.csv`. The deterministic implementation and the frozen semantic maps are in `tools/research_analysis/build_benchmark_taxonomy.py`.

## Design rules

1. Repository, feature, entanglement, behavioral risk, and codebase condition are independent axes.
2. Repository and feature axes have exactly one primary label. Secondary labels are optional and capped at two.
3. Entanglement, behavioral risk, and codebase condition are multi-label.
4. Original metadata labels are preserved verbatim before normalization.
5. Automatically unavailable measurements are `NA`; zero is used only when the relevant scope was located and measured.
6. Every row records concrete evidence paths.
7. A semantic ambiguity is retained as a provisional label with
   `review_status=needs_review`; it is not silently resolved.
8. Categories with fewer than five tasks are descriptive only.

## Repository taxonomy

### `repo_archetype_primary`

| Label | Operational definition |
|---|---|
| `library` | Reusable Python API whose primary artifact is imported by other code |
| `framework_plugin` | Framework or plugin substrate whose core behavior depends on registration, dispatch, extension, or lifecycle |
| `developer_tooling` | Test, build, packaging, documentation, lint, format, migration, or environment tooling primarily invoked by developers |
| `application_service` | Runnable application/service or curated application-style repository |

The label describes the upstream repository, not the selected feature. For example, a parser feature extracted from a developer tool remains `developer_tooling` at the repository axis.

### `repo_provenance`

| Label | Operational definition |
|---|---|
| `real_oss_mature` | Commit/version-pinned upstream OSS snapshot with no explicit local legacy-provenance marker |
| `real_oss_legacy` | Upstream OSS explicitly marked as legacy by task-package provenance evidence |
| `curated_vibe` | Curated `vibe_app` benchmark repository |

`real_oss_legacy` is deliberately not inferred from project reputation, age, or current maintenance status. It has zero v2 tasks because the local task packages contain no explicit legacy-provenance marker for the real OSS snapshots. `curated_vibe` is reserved but has zero rows because Curated-7 is not part of External Main.

### `repo_domain_primary`

Allowed values are `parsing`, `data_modeling`, `testing`, `configuration`, `packaging`, `networking`, `general_utility`, and `application`. The primary label represents the upstream project's dominant problem domain. Up to two secondary labels may be used for durable cross-domain repositories.

Repository labels are frozen in an exhaustive source-name map. The build fails if a new source repository is not mapped or if one source has two primary domains.

## Feature taxonomy

### `feature_family_primary`

| Label | Included behavior |
|---|---|
| `parse_tokenize_decode` | Parse, tokenize, decode, expression interpretation, or syntax-tree construction |
| `protocol_state_transition` | Stateful protocol, recurrence, frame, handshake, or transition behavior |
| `validate_normalize_construct` | Validate input, normalize values, sanitize content, or construct constrained models |
| `serialize_format_render` | Serialize, dump, format, compile, or render output |
| `registry_plugin_dispatch` | Register, discover, select, order, or dispatch plugins/hooks/events |
| `config_resolve_discover` | Merge config, resolve environment/path, discover candidates, or select sources |
| `resource_metadata_loading` | Load package resources, grammars, locale data, distribution metadata, or records |
| `algorithm_data_structure` | Core data structure, graph, ordering, interval, iterator, or comparison algorithm |
| `cache_retry_policy` | Cache/eviction, retry/backoff, rule, predicate, or policy evaluation |
| `workflow_session_orchestration` | Multi-step workflow, session, command runner, pipeline, or configurator orchestration |

Task labels are explicit and exhaustive. Secondary labels capture a second externally visible behavior, not an implementation dependency. A task cannot receive two primary families.

### `feature_statefulness`

| Label | Operational definition |
|---|---|
| `stateless` | Output depends only on explicit inputs and immutable configuration |
| `local_state` | State is confined to one call/object/tree and is not a cross-call session |
| `session_state` | Behavior depends on a protocol/recurrence/retry/session history across operations |
| `global_state` | Behavior reads or mutates module/process-level shared state |
| `lifecycle_state` | Correctness depends on setup, class construction, registration, wrapper, or teardown phase |

Priority for overlapping cases is `global_state`, then `session_state`, then `lifecycle_state`, followed by local/stateless behavior. Explicit task exceptions are frozen in the script.

## Entanglement mechanism taxonomy

The original `entanglement.primary` and `entanglement.types` fields are retained. Normalized mechanisms are multi-label:

| Normalized label | Evidence rule |
|---|---|
| `static_transitive_dependency` | Explicit reference closure contains more than one file, or a reachable internal import exists beyond the located entrypoint |
| `implicit_runtime_dependency` | Original metadata contains `implicit_dependency_coupling` |
| `data_model_invariant` | Original metadata contains `data_model_coupling` |
| `parser_state` | Original metadata contains `parser_state_coupling` |
| `framework_lifecycle` | Original metadata contains `framework_coupling` |
| `global_state_registry` | Original metadata contains `global_state_registry_coupling` |
| `config_environment` | Original metadata contains `config_environment_coupling` |
| `resource_packaging` | Original metadata contains `resource_coupling` |
| `dynamic_import_plugin` | Scoped source uses dynamic-import/entry-point APIs, or metadata semantics explicitly describe dynamic loading/discovery |
| `third_party_contract` | Original metadata contains `third_party_dependency_coupling` |

`legacy_vibe_clutter` is not normalized as entanglement because the taxonomy
records it on the independent codebase-condition axis.

## Behavioral hidden-risk taxonomy

Behavioral risk describes what hidden tests exercise, never whether a submission passed:

| Label | Hidden-test evidence |
|---|---|
| `exception_semantics` | Raised exception, invalid input, missing requirement, conflict, or structured error assertions |
| `ordering_semantics` | Stable ordering, priority, precedence, before/after, first/last, or head semantics |
| `boundary_cases` | Empty/None/zero/unknown/missing/min/max or explicit edge/boundary cases |
| `mutation_side_effects` | Update, set, delete, append, pop, clear, mutation, counters, or side-effect assertions |
| `lifecycle_semantics` | Register/unregister, setup/teardown, enable/disable, start/stop, close, hook, or wrapper behavior |
| `platform_variation` | Environment variables, platform branches, XDG/home, Windows/POSIX/Linux/macOS behavior |

Tags are generated from deterministic source text/AST scans of `hidden_tests/**/*.py`. They are intentionally broad screening labels. A narrow contract claim requires reading the linked hidden-test evidence.

## Codebase-condition taxonomy

| Label | Evidence rule |
|---|---|
| `legacy_clutter` | Task metadata explicitly contains `legacy_vibe_clutter` |
| `duplicated_implementation` | Metadata explicitly identifies duplicate/wrong helper implementations |
| `dead_code_distractors` | Metadata explicitly identifies wrong/legacy helpers or clutter paths |
| `generated_code` | Explicit reference closure contains generated-named source artifacts |
| `weak_module_boundaries` | At least three explicit Python reference files and original implicit dependency coupling |

Absence of a tag is not proof that the repository lacks the condition; it means the operational evidence rule did not fire.

## Automatic structural metrics

### Reference closure

Main task packages do not expose `reference_solution/`. The taxonomy's legacy
structural closure fields therefore use explicit `required_source_files` or
`source_files` in `evaluation/oracle_manifest.json`. Paper compactness uses the
separate 150/150 frozen registry at `benchmark/references/compactness.json`.

- `reference_file_count`: number of resolved files after expanding explicitly listed directories
- `reference_loc`: nonblank physical lines in resolved Python files
- `resource_file_count`: resolved non-Python files in the explicit reference closure
- `reference_symbol_count`: count of explicit oracle `target_symbols` or `target_api`; otherwise `NA`

If the oracle list is empty or any listed path cannot be resolved, file/LOC/resource metrics are `NA`. No trajectory or submission is used to fill them.

### Entrypoints and dependency graph

- `source_entrypoint_count`: number of metadata `feature.source_entrypoints`
- Entrypoint files are located by longest module-prefix match, then by top-level AST symbol match; explicit reference files are preferred.
- Internal imports are resolved against a module index built from the task source snapshot.
- When an explicit reference closure exists, graph traversal is bounded to its Python files; otherwise traversal starts from located entrypoints in the source snapshot.
- `direct_internal_dependency_count`: unique internal files imported directly by located entrypoint files
- `transitive_internal_dependency_count`: reachable internal files excluding entrypoint and direct files
- `static_file_closure_depth`: maximum shortest internal-import distance from an entrypoint
- `external_dependency_count`: distinct non-stdlib top-level imports in the traversed source scope

If no entrypoint file can be located, graph metrics and source booleans are `NA`.

### Source signals

- `has_dynamic_import`: scoped AST calls to `__import__`, `importlib.import_module`, entry-point APIs, or explicit metadata dynamic-loading semantics
- `has_global_state`: scoped `global` statements, state/registry/cache-named mutable module assignments, or original global-state/registry metadata
- `has_registry`: scoped registry/plugin/hook/entry-point identifiers or explicit registry semantics
- `has_framework_lifecycle`: normalized framework coupling or explicit setup/register/teardown lifecycle semantics
- `adapter_required`: `true` only when metadata/oracle text explicitly requires an adapter/shim/facade; otherwise `NA`, not false

### Test counts

`public_test_count` and `hidden_test_count` count statically declared functions/methods whose names start with `test`. Parametrized expansions are not multiplied because collecting them would execute task code and make the structural scan environment-dependent.

## Twenty-task trial audit

The trial set was selected before the full semantic map to span different source repositories and all original primary entanglement types:

1. `alembic__revision_map_core__hard3_001`
2. `attrs__validators_core__001`
3. `babel__plural_core__001`
4. `build__pyproject_backend_core__hard3_001`
5. `celery__signal_dispatch_core__hard3_001`
6. `coverage__config_merge_core__001`
7. `dynaconf__settings_merge_core__001`
8. `h11__message_parse_core__001`
9. `importlib_resources__traversable_tree_core__hard3_001`
10. `jinja2__lexer_parser_core__001`
11. `keyring__backend_select_core__hard3_001`
12. `lark__grammar_loader_core__001`
13. `networkx__dag_topo_core__001`
14. `phonenumbers__parse_format_core__001`
15. `pluggy__hook_call_order__001`
16. `pydantic_v1__validation_error_core__001`
17. `requests_cache__cache_key_core__hard3_001`
18. `sqlparse__parse_format_core__001`
19. `blinker__signal_registry_core__001`
20. `yarl__url_model_core__001`

The trial produced four revisions:

1. Repository domain and feature family were separated because a developer tool can expose a parser feature.
2. Protocol/session behavior was separated from generic parse/tokenize behavior.
3. Dynamic import detection was split into AST-call and metadata-semantic rules so the JSON field name `source_entrypoints` cannot create a false positive.
4. Legacy/clutter was moved out of entanglement into codebase condition.

## Review and freeze protocol

Every v2 task has an explicit repository source map and task-level feature-family
assignment. Rows distinguish maintainer review from AI-assisted adjudication;
neither is described as independent human gold. The current generated report
contains zero unresolved `needs_review` rows.

The build runs the following invariants:

- exactly 150 metadata-backed rows;
- exactly one primary repository domain and feature family;
- no unmapped or multiply mapped task/source;
- labels belong to the controlled vocabulary;
- every evidence path exists;
- all 20 trial tasks remain present;
- taxonomy version is `v2` for every row.

## Reproduction

```bash
python3 tools/research_analysis/build_benchmark_taxonomy.py --strict
```

The command regenerates both the CSV and `docs/research_analysis/BENCHMARK_TAXONOMY_REPORT.md`. It does not read any path under `experiments/python`, trajectory tables, submissions, or evaluation results.
