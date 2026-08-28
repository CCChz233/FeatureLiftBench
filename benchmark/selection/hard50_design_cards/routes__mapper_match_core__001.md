# Design card: routes__mapper_match_core__001

**status:** `materialized_candidate`  
**disposition:** `backup`  
**wave:** `backup`  
**package:** `routes`  
**repository_url:** https://github.com/nandoflorestan/routes  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `framework_coupling`  
**feature_one_liner:** Mapper connect and match/generate  
**commit:** `7e82bd895a120cbf73f271c32ac289d51124303f`  

## paper_fit

Backup routing table if falcon blocked.

## why_hard

Match vs generate inverse; conditions.

## Balance Role

registry_plugin_dispatch / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Mapper; connect; match; generate

## Included Behavior (draft)

static route; wildcard; generate url

## Excluded Behavior

web frameworks

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
