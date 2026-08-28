# Design card: zope_interface__adapter_registry_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `zope.interface`  
**repository_url:** https://github.com/zopefoundation/zope.interface  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `implicit_dependency_coupling`, `framework_coupling`  
**feature_one_liner:** Interface declarations plus adapter registry lookup  
**commit:** pending pin  

## paper_fit

RQ1/RQ4: implicit registry closure. Removing it leaves no ZCA-style dispatch evidence.

## why_hard

Lookup is global and interface-driven; copy of one module misses registration side effects.

## Balance Role

registry_plugin_dispatch / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

providedBy; implementer; adapter registry lookup

## Included Behavior (draft)

declare interfaces; register adapters; query adapters by interface

## Excluded Behavior

ZCA site managers beyond optional alias; persistent ZODB

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
