# Design card: limits__strategy_storage_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `limits`  
**repository_url:** https://github.com/alisaifee/limits  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `resource_coupling`, `implicit_dependency_coupling`  
**feature_one_liner:** Rate-limit strategy over a storage backend  
**commit:** `cb0ff4294d1b713b7892f975443d04cd21d98dfa`  

## paper_fit

RQ4 strategy+storage registry with unused network backends as decoy.

## why_hard

Strategy objects are not a single function; wrong storage silently breaks windows.

## Balance Role

registry_plugin_dispatch / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

RateLimiter; MemoryStorage; parse; hit

## Included Behavior (draft)

fixed-window hit; remaining; reset; memory storage

## Excluded Behavior

Redis/Memcached storage

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
