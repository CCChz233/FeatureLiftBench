# Design card: publicsuffixlist__metadata_lookup_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `publicsuffixlist`  
**repository_url:** https://github.com/ko-zu/psl  
**replacement_slot:** `resource-direct-01`  
**final_lift_type:** Direct  
**feature_family:** resource_metadata_loading  
**entanglement:** resource_coupling  
**feature_one_liner:** Bundled public-suffix metadata lookup  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

Load and resolve a small redistributable metadata resource with deterministic fallbacks.

## Pinned Source

- commit: `7d4d0d0db229f996824bd65741ed285ebb466d87`
- license: `MPL-2.0`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: none

## Required API

  - `featurelifted.PublicSuffixList`

## Included Behavior

  - bundled list loading
  - public and private suffix lookup
  - registrable-domain lookup
  - IDN handling

## Excluded Behavior

  - updatePSL network refresh
  - command-line updates
  - live publicsuffix.org access

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
