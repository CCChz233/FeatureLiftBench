# Design card: mimesis__person_address_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `mimesis`  
**repository_url:** https://github.com/lk-geimfari/mimesis  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `wcmatch__globmatch_core__001` (Flash copy_heavy_pass, RRES≈0.95 on a small Direct repo).  
**feature_family:** `direct_tooling_copytrap`  
**entanglement.level:** high  
**entanglement.types:** `data_model_coupling`, `resource_coupling`  
**feature_one_liner:** English Person/Address fake data without the remaining locale tree  
**commit:** `b285fd17ada4c916338c08fc105b8b72bda0630a`  

## paper_fit

RQ2: Person/Address vs dozens of unused locale JSON trees and unused providers. Copy-all of the rewritten Mimesis package is a real unused decoy, not padding.

## why_hard

Must load the right dataset files for the English locale; copying Generic pulls unused providers and locale JSON.

## Balance Role

direct_tooling_copytrap / Direct / high entanglement. Swap-in for a small-repo copy-heavy Flash pass.

## Pinned Source

- commit: `b285fd17ada4c916338c08fc105b8b72bda0630a`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Person; Person.name; Person.full_name; Address; Address.city; Locale; LocaleError

## Included Behavior (draft)

seeded English name; city; invalid locale raises LocaleError; full_name contains first and last

## Excluded Behavior

Generic all-providers; binary file providers; schema builder; runtime import of mimesis

## YAML contract (to fill at pin time)

```yaml
target_api:
  module: featurelifted
  signatures:
    - Person
    - Person.name
    - Person.full_name
    - Address.city
    - Locale
    - LocaleError
  returns:
  exceptions:
    - LocaleError
  defaults:
  state_effects:
upstream_mapping:
  primary_symbols:
    - mimesis.Person
    - mimesis.Address
  supporting_components:
    - mimesis.locales
    - mimesis.datasets
  semantic_delta: package renamed to featurelifted; unused locales remain repo decoy
oracle_basis:
  basis: upstream
scope:
  included:
    - seeded name
    - city
    - invalid locale
    - full_name
  excluded:
    - Generic all-providers
    - binary file providers
    - schema builder
feasibility:
  commit: b285fd17ada4c916338c08fc105b8b72bda0630a
  license: MIT
  python_versions: "3.12"
  native_or_heavy_dependencies: none
  offline_resources: locale JSON datasets
acceptance:
  closure_review: pending
  reference_pass: pending
  isolation_pass: pending
  no_original_import: pending
  overlap_check: pass_name_screen
```

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/mimesis__person_address_core__001`
- local oracle/naive/copy-all: pass / fail / pass (RRES ≈ 35.5; true rewritten Mimesis package, not padding)
- Docker / Flash calibration: pending after remaining compactness swaps
- promotion to `benchmark/hard50`: blocked until compactness swaps finish
