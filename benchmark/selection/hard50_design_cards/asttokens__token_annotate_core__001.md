# Design card: asttokens__token_annotate_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `asttokens`  
**repository_url:** https://github.com/gristlabs/asttokens  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `parse_tokenize_decode`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`  
**feature_one_liner:** Annotate AST nodes with source tokens  
**commit:** pending pin  

## paper_fit

RQ1 parser-state Direct with real AST coupling.

## why_hard

Token/AST alignment is Hidden-sensitive; ast.parse alone fails.

## Balance Role

parse_tokenize_decode / Direct / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

ASTTokens; get_text; get_token

## Included Behavior (draft)

annotate tree; get_text for node; comment tokens optional if declared

## Excluded Behavior

executing/stack_data full traceback UX

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
