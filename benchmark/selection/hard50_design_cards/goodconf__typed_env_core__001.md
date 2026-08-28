# Design card: goodconf__typed_env_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `goodconf`  
**repository_url:** https://github.com/lincolnloop/goodconf  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `config_environment_coupling`, `data_model_coupling`  
**feature_one_liner:** Typed GoodConf model loaded from env and files  
**commit:** pending pin  

## paper_fit

RQ1 typed settings object (not pydantic-settings, already in 150).

## why_hard

Field env aliases + file overlay; copying pydantic-settings mental model fails.

## Balance Role

config_resolve_discover / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

GoodConf; Field; load; dump

## Included Behavior (draft)

env names; file overlay; validation error

## Excluded Behavior

Django integration extras beyond declared

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
