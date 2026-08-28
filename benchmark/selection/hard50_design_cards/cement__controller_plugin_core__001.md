# Design card: cement__controller_plugin_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `cement`  
**repository_url:** https://github.com/datafolklabs/cement  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `config_environment_coupling`  
**feature_one_liner:** Cement App controller registration and plugin load  
**commit:** `b5af20431d4c50f0c1bfb7ed5544b620edbe4c73`  

## paper_fit

RQ4 framework plugin + hooks, a realistic extraction target.

## why_hard

App lifecycle registers handlers; missing hook registration fails Hidden.

## Balance Role

registry_plugin_dispatch / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

App; Controller; hook.register

## Included Behavior (draft)

register controller; run argv; hook callback

## Excluded Behavior

redis extensions; extra output handlers beyond declared

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
