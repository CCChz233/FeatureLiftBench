# Design card: typeguard__check_type_pipeline_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `typeguard`  
**repository_url:** https://github.com/agronholm/typeguard  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** validate_normalize_construct  
**entanglement:** data_model_coupling  
**feature_one_liner:** check_type + collection/origin handling + forward refs  
**lift_review_flag:** none

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.check_type(value, expected_type, *, collection_check_strategy=...)"
  - "featurelifted.TypeCheckError"
  - "featurelifted.typechecked decorator (optional if included)"
  - "CollectionCheckStrategy; string-form forward refs may warn/skip — prefer typing constructs"
returns:
  - "check_type returns value on success"
exceptions:
  - "TypeCheckError with details"
defaults:
  - "strategy defaults per typeguard version \u2014 pin and declare"
state_effects:
  - "none unless typechecked wraps functions"
```

## upstream_mapping

```yaml
primary_symbols:
  - "typeguard.check_type"
  - "typeguard.TypeCheckError"
supporting_components:
  - "typeguard._transformers / collection checks"
semantic_delta:
  - "Nested collection + Union + Optional checking treated as composed checkers"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Pin typeguard major; API shifted across v2/v4.
```

## scope

```yaml
included:
  - "check_type for builtins, Optional, Union, list/dict nesting"
excluded:
  - "pytest plugin, import hook instrumentation"
```

## feasibility

```yaml
commit: "9f289c7fca68097542d3bde9d59496ad42e58251"  # tag 4.6.0
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "pure type checks"
```

## acceptance

```yaml
closure_review: pass
reference_pass: pass
isolation_pass: pass
no_original_import: pass
overlap_check: pass
```

## agent_notes

- Staging path: `benchmark/staging/typeguard__check_type_pipeline_core__001/`
- Skim pass @ 4.6.0 (`9f289c7fca68…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
