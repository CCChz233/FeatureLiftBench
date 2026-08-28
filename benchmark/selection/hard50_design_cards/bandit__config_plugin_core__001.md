# Design card: bandit__config_plugin_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `bandit`  
**repository_url:** https://github.com/PyCQA/bandit  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `config_environment_coupling`, `implicit_dependency_coupling`  
**feature_one_liner:** Bandit config load plus plugin test-id selection  
**commit:** `f8b9f1a2210f50539d0e28b1b457462cdb4036a1`  

## paper_fit

RQ2: security scanner repo as decoy around config+plugin ids.

## why_hard

Plugin ids are registered dynamically; config skip lists are Hidden-sensitive.

## Balance Role

config_resolve_discover / Direct / high entanglement.

## Pinned Source

- commit: `f8b9f1a2210f50539d0e28b1b457462cdb4036a1`
- license: Apache-2.0
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

BanditConfig; manager get_tests; config file

## Included Behavior (draft)

skip tests from config; include tests; invalid yaml

## Excluded Behavior

full AST vulnerability scan of CPython

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
  commit: f8b9f1a2210f50539d0e28b1b457462cdb4036a1
  license: Apache-2.0
  python_versions:
  native_or_heavy_dependencies:
  offline_resources:
acceptance:
  closure_review: pending
  reference_pass: pass
  isolation_pass: pass
  no_original_import: pass
  overlap_check: pass_name_screen
```

## Gate Status

- design card: ready for pin
- package completeness: pending
- Docker / Flash calibration: pending
- promotion to `benchmark/hard50`: blocked until Pilot gate (and then 50/50) passes
