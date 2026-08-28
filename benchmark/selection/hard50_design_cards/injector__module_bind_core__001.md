# Design card: injector__module_bind_core__001

**status:** `swapped_out_pilot`  
**disposition:** `backup`  
**wave:** `pilot_swap`  
**package:** `injector`  
**repository_url:** https://github.com/python-injector/injector  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `implicit_dependency_coupling`, `data_model_coupling`  
**feature_one_liner:** Injector Module binder and get  
**commit:** pending pin  

## paper_fit

Backup DI if dependency-injector native bits block.

## why_hard

Binder graph; similar RQ4 construct+registry.

## Balance Role

validate_normalize_construct / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Injector; Module; inject; Binder

## Included Behavior (draft)

bind; singleton vs noscope; missing binding

## Excluded Behavior

thread locals extras

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
