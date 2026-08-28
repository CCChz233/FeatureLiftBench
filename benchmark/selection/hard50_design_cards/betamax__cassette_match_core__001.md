# Design card: betamax__cassette_match_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `betamax`  
**repository_url:** https://github.com/betamaxpy/betamax  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `direct_tooling_copytrap`  
**entanglement.level:** high  
**entanglement.types:** `resource_coupling`, `framework_coupling`  
**feature_one_liner:** Betamax cassette record/replay against a stubed session  
**commit:** pending pin  

## paper_fit

RQ5 vs E50 vcrpy: requests Session integration, still copy-trap on unused matchers.

## why_hard

Matcher set + cassette format; naive json dump fails Hidden matchers.

## Balance Role

direct_tooling_copytrap / Direct / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Betamax; use_cassette; configure

## Included Behavior (draft)

replay recorded json cassette; match uri; missing cassette error

## Excluded Behavior

live recording to network

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
