# Design card: docutils__rst_transform_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `docutils`  
**repository_url:** https://github.com/docutils/docutils  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `parse_tokenize_decode`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`  
**feature_one_liner:** Publish RST to doctree and apply a transform  
**commit:** pending pin  

## paper_fit

RQ5 deep parser state, not E50 tinycss2 roundtrip.

## why_hard

Settings+parser+transforms; copy rst2html launcher is the wrong closure.

## Balance Role

parse_tokenize_decode / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

publish_doctree; nodes; Transformer

## Included Behavior (draft)

parse paragraph/section; doctree walk; invalid RST error

## Excluded Behavior

full HTML writer themes; Sphinx (already in 150)

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
