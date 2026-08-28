# Design card: mashumaro__dataclass_codec_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `mashumaro`  
**repository_url:** https://github.com/Fatal1ty/mashumaro  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `implicit_dependency_coupling`  
**feature_one_liner:** DataClassDictMixin to_dict/from_dict with aliases  
**commit:** pending pin  

## paper_fit

RQ5 Adapted codec distinct from marshmallow/pydantic/cattrs already used.

## why_hard

Mixin codegen and config; copying mashumaro/json only fails dialects.

## Balance Role

validate_normalize_construct / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

DataClassDictMixin; field metadata; to_dict; from_dict

## Included Behavior (draft)

alias; omit_none; missing required; nested

## Excluded Behavior

orjson/msgpack engines

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
