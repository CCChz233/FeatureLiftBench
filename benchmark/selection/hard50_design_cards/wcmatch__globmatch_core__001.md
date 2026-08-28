# Design card: wcmatch__globmatch_core__001

**status:** `design_card_ready`  
**disposition:** `backup`  
**wave:** `backup`  
**package:** `wcmatch`  
**repository_url:** https://github.com/facelessuser/wcmatch  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Swapped out 2026-08-27: Flash copy_heavy_pass RRES≈0.95 on a small Direct repo. Replaced by `mimesis__person_address_core__001`.  
**feature_family:** `direct_tooling_copytrap`  
**entanglement.level:** high  
**entanglement.types:** `parser_state_coupling`, `data_model_coupling`  
**feature_one_liner:** globmatch with flags and negate  
**commit:** pending pin  

## paper_fit

Backup Direct copy-trap if pathspec-like needed; larger than pathspec.

## why_hard

Flag combinations; Hidden brace/negate.

## Balance Role

direct_tooling_copytrap / Direct / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

glob.globmatch; globmatch; flags

## Included Behavior (draft)

globstar; negate; case flags

## Excluded Behavior

full directory walk of huge trees

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
