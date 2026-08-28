# Design card: pyhamcrest__matcher_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `PyHamcrest`  
**repository_url:** https://github.com/hamcrest/PyHamcrest  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `direct_tooling_copytrap`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `implicit_dependency_coupling`  
**feature_one_liner:** Matcher combinators equal_to/has_item/raises  
**commit:** pending pin  

## paper_fit

RQ2 matcher library with many unused combinators as decoy.

## why_hard

Mismatch descriptions and combinators; copying assertEqual fails Hidden.

## Balance Role

direct_tooling_copytrap / Direct / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

assert_that; equal_to; has_item; raises; described_as

## Included Behavior (draft)

combinators; mismatch description; raises

## Excluded Behavior

Java Hamcrest ports unused in Python tree

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
