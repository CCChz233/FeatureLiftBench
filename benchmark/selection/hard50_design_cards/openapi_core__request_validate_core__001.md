# Design card: openapi_core__request_validate_core__001

**status:** `swapped_out_pilot`  
**disposition:** `backup`  
**wave:** `pilot_swap`  
**package:** `openapi-core`  
**repository_url:** https://github.com/python-openapi/openapi-core  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `framework_coupling`  
**feature_one_liner:** Validate request/response against an OpenAPI spec  
**commit:** pending pin  

## paper_fit

RQ4 unmarshalling vs jsonschema-only (jsonschema already in 150).

## why_hard

Spec+request+unmarshal types; naive jsonschema.validate misses media types.

## Balance Role

validate_normalize_construct / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

OpenAPI.from_dict; unmarshal_request; validate_response

## Included Behavior (draft)

valid request; missing required; response schema error

## Excluded Behavior

live servers; full Starlette integration extras

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
