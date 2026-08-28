# Design card: zope_component__site_lookup_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `zope.component`  
**repository_url:** https://github.com/zopefoundation/zope.component  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `implicit_dependency_coupling`, `framework_coupling`  
**feature_one_liner:** Component site manager get/query utilities  
**commit:** `bb12836f35b40f427fc313a0bc033816c30d890d`  

## paper_fit

RQ4: site-manager closure on top of zope.interface.

## why_hard

Depends on interface identities and a global site; naive extract misses get/query semantics.

## Balance Role

registry_plugin_dispatch / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

getUtility; queryUtility; provideUtility; getGlobalSiteManager

## Included Behavior (draft)

register utilities; lookup by interface; missing utility behavior

## Excluded Behavior

persistent local sites; ZODB

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
