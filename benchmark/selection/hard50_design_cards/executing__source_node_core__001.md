# Design card: executing__source_node_core__001

**status:** `design_card_ready`  
**disposition:** `backup`  
**wave:** `backup`  
**package:** `executing`  
**repository_url:** https://github.com/alexmojaki/executing  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `parse_tokenize_decode`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `resource_coupling`  
**feature_one_liner:** Map a frame to the AST node being executed  
**commit:** pending pin  

## paper_fit

Backup parser-state Direct.

## why_hard

Frame/AST mapping is fragile; naive inspect.getsource fails.

## Balance Role

parse_tokenize_decode / Direct / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Source.executing; node; text

## Included Behavior (draft)

simple call frame; node type; source text

## Excluded Behavior

ipython display

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
