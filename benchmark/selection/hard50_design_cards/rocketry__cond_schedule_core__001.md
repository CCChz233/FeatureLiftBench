# Design card: rocketry__cond_schedule_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `rocketry`  
**repository_url:** https://github.com/Miksus/rocketry  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `workflow_session_orchestration`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `config_environment_coupling`  
**feature_one_liner:** Condition parsing and Session task registration  
**commit:** pending pin  

## paper_fit

RQ5 Direct scheduler DSL inside a larger session object.

## why_hard

Condition language + session; Hidden checks combination operators.

## Balance Role

workflow_session_orchestration / Direct / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Session; task; time conditions; session.run(once)

## Included Behavior (draft)

true/false condition; register task; run once without sleep wall-clock via time mock if declared

## Excluded Behavior

production scheduler loops; remote

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
