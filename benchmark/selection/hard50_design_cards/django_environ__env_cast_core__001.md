# Design card: django_environ__env_cast_core__001

**status:** `design_card_ready`  
**disposition:** `backup`  
**wave:** `selected`  
**package:** `django-environ`  
**repository_url:** https://github.com/joke2k/django-environ  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Swapped out 2026-08-27: Flash copy_heavy_pass RRES≈0.99 on a slice-sized repo. Replaced by `dulwich__config_parse_core__001`.  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `config_environment_coupling`  
**feature_one_liner:** Env casts for Django-style settings from os.environ  
**commit:** `9c1fc30b2b2330f297187904190c3baf80919876`  

## paper_fit

RQ5 framework_coupling without vendoring Django.

## why_hard

Cast helpers encode Django URL dialects; naive getenv fails db/list.

## Balance Role

config_resolve_discover / Adapted / high entanglement.

## Pinned Source

- commit: `9c1fc30b2b2330f297187904190c3baf80919876`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Env; env.db; env.bool; env.list

## Included Behavior (draft)

bool/list/db url casts; missing required; prefix

## Excluded Behavior

running Django apps; migrate

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
  commit: 9c1fc30b2b2330f297187904190c3baf80919876
  license: MIT
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
