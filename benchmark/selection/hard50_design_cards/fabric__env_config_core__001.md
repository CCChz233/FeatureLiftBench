# Design card: fabric__env_config_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `fabric`  
**repository_url:** https://github.com/fabric/fabric  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `config_environment_coupling`  
**feature_one_liner:** Fabric Config load from files and runtime overrides  
**commit:** pending pin  

## paper_fit

RQ4 Invoke-adjacent config (invoke already in E50) at Fabric layer.

## why_hard

Config object is nested and SSH-flavored; tests must stay offline.

## Balance Role

config_resolve_discover / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Config; Connection constructor config=; load_ssh_config optional off

## Included Behavior (draft)

default config; file overlay; runtime override

## Excluded Behavior

real SSH; network; Paramiko auth

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
