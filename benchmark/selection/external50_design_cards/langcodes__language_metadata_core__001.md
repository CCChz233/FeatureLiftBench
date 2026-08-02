# Design card: langcodes__language_metadata_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `langcodes`  
**repository_url:** https://github.com/rspeer/langcodes  
**replacement_slot:** `resource-composite-third-party-03`  
**final_lift_type:** Composite  
**feature_family:** resource_metadata_loading  
**entanglement:** third_party_dependency_coupling  
**feature_one_liner:** Language-tag normalization and CLDR metadata  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

Compose local metadata loading and resolution around one allowlisted pure-Python dependency.

## Pinned Source

- commit: `0aebfa862ed86d820d0c96ce311ef661cf0a798a`
- license: `MIT`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: language-data, marisa-trie

## Required API

  - `featurelifted.Language`
  - `featurelifted.standardize_tag`
  - `featurelifted.best_match`

## Included Behavior

  - BCP-47 normalization
  - Language objects
  - localized display names
  - likely subtag maximize
  - best-match scoring

## Excluded Behavior

  - data rebuild scripts
  - online registry updates
  - population statistics beyond the declared API

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
