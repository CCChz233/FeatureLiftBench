# Design card: pre_commit__config_load_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `pre-commit`  
**repository_url:** https://github.com/pre-commit/pre-commit  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `config_environment_coupling`, `resource_coupling`  
**feature_one_liner:** Load .pre-commit-config.yaml into Hook/Repo objects  
**commit:** `a9bba55a3f74068b53f4bd4d831d7e05e34eae6c`  

## paper_fit

RQ2: huge installer/language tree is decoy around a bounded config slice.

## why_hard

Schema+normalization+language defaults; copy-all of pre-commit is RRES~1.

## Balance Role

config_resolve_discover / Adapted / high entanglement.

## Pinned Source

- commit: `a9bba55a3f74068b53f4bd4d831d7e05e34eae6c`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

load_config; validate; ManifestHook / ConfigHook subset

## Included Behavior (draft)

parse repos/hooks; local language; invalid schema error

## Excluded Behavior

git install; downloading hook repos; network

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
  commit: a9bba55a3f74068b53f4bd4d831d7e05e34eae6c
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
