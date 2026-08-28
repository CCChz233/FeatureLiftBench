# Design card: openapi_schema_validator__draft_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `openapi-schema-validator`  
**repository_url:** https://github.com/python-openapi/openapi-schema-validator  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `parser_state_coupling`  
**feature_one_liner:** OpenAPI-dialect JSON Schema validator  
**commit:** pending pin  

## paper_fit

RQ5 dialect validator vs jsonschema 150 and openapi-core companion.

## why_hard

OAS nullable/discriminator differ from JSON Schema; copy jsonschema fails.

## Balance Role

validate_normalize_construct / Direct / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

validate; OAS30/OAS31 format dialect

## Included Behavior (draft)

nullable; discriminator subset; invalid type

## Excluded Behavior

full OpenAPI document walk (that's openapi-core)

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
