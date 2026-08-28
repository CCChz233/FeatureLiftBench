# Design card: paste__dispatch_map_core__001

**status:** `pilot_materialized`  
**disposition:** `selected`  
**wave:** `pilot`  
**package:** `Paste`  
**repository_url:** https://github.com/cdent/paste  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `config_environment_coupling`  
**feature_one_liner:** URLMap / dispatch composite WSGI  
**commit:** pending pin  

## paper_fit

Backup composite WSGI dispatch.

## why_hard

Prefix matching + factory config.

## Balance Role

registry_plugin_dispatch / Adapted / high entanglement.

## Pinned Source

- commit: `28e461548498138b8814b243be432a04a7895dba`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

URLMap; parse_map_file subset

## Included Behavior (draft)

mount apps; longest prefix; 404

## Excluded Behavior

httpserver

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
