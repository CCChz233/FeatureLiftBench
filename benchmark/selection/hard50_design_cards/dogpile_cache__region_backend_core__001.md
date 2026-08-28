# Design card: dogpile_cache__region_backend_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `dogpile.cache`  
**repository_url:** https://github.com/sqlalchemy/dogpile.cache  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `implicit_dependency_coupling`, `resource_coupling`  
**feature_one_liner:** Cache region with pluggable backend and dogpile lock  
**commit:** pending pin  

## paper_fit

RQ2+RQ4: backend registry with a large unused backend tree as copy-all decoy.

## why_hard

Must wire region+backend+creator; copying redis backend fails isolation.

## Balance Role

registry_plugin_dispatch / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

make_region; CacheRegion.configure; get_or_create

## Included Behavior (draft)

memory backend; get_or_create; invalidate; missing key

## Excluded Behavior

memcached/redis backends; distributed locks

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
