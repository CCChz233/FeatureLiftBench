# Design card: fastjsonschema__compile_validate_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `fastjsonschema`  
**repository_url:** https://github.com/horejsek/python-fastjsonschema  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`  
**feature_one_liner:** Compile a JSON Schema into a validator callable  
**commit:** pending pin  

## paper_fit

RQ1 compiled validator vs jsonschema library already in 150.

## why_hard

Compiler output must match formats/required; wrong draft fails Hidden.

## Balance Role

validate_normalize_construct / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

compile; JsonSchemaValueException

## Included Behavior (draft)

draft-style required/type; compile once; invalid value exception

## Excluded Behavior

code-dump debugging CLI

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
