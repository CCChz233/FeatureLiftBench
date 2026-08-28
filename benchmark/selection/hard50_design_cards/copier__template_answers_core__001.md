# Design card: copier__template_answers_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `copier`  
**repository_url:** https://github.com/copier-org/copier  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `config_environment_coupling`, `resource_coupling`  
**feature_one_liner:** Load copier.yml questions and compute answers  
**commit:** `5f71fad40920cd03f0fe6bf2292daa43cf089fff`  

## paper_fit

RQ2 large template engine with a bounded answers/config slice.

## why_hard

Question schema + exclusion + answers file; copy-all of jinja render is wrong closure.

## Balance Role

config_resolve_discover / Adapted / high entanglement.

## Pinned Source

- commit: `5f71fad40920cd03f0fe6bf2292daa43cf089fff`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Worker or run_copy dry subset; load answers; questions

## Included Behavior (draft)

yaml questions; default answers; invalid choice

## Excluded Behavior

git clone templates; network; full project render

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
  commit: 5f71fad40920cd03f0fe6bf2292daa43cf089fff
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
