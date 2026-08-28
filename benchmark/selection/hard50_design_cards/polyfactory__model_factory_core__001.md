# Design card: polyfactory__model_factory_core__001

**status:** `pilot_materialized`  
**disposition:** `selected`  
**wave:** `pilot`  
**package:** `polyfactory`  
**repository_url:** https://github.com/litestar-org/polyfactory  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `implicit_dependency_coupling`  
**feature_one_liner:** ModelFactory build for dataclasses/pydantic-like models  
**commit:** pending pin  

## paper_fit

RQ5 construct factories; Litestar monorepo is a copy-all trap.

## why_hard

Factory metaclass + type inspection; copying faker calls is not the feature.

## Balance Role

validate_normalize_construct / Adapted / high entanglement.

## Pinned Source

- commit: `e420486b11b9f82b7816d86a8f53c20ce29df86f`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

DataclassFactory; build; coverage; use_args

## Included Behavior (draft)

build instance; overrides; collection fields

## Excluded Behavior

SQLAlchemy plugin; faker providers beyond declared

## YAML contract (to fill at pin time)

```yaml
target_api:
  module:
  signatures:
  returns:
  exceptions:
  defaults:
  state_effects:
upstream_mapping:
  primary_symbols:
  supporting_components:
  semantic_delta:
oracle_basis:
  basis: upstream
scope:
  included:
  excluded:
feasibility:
  commit:
  license:
  python_versions:
  native_or_heavy_dependencies:
  offline_resources:
acceptance:
  closure_review: pending
  reference_pass: pending
  isolation_pass: pending
  no_original_import: pending
  overlap_check: pass_name_screen
```

## Gate Status

- design card: ready for pin
- package completeness: pending
- Docker / Flash calibration: pending
- promotion to `benchmark/hard50`: blocked until Pilot gate (and then 50/50) passes
