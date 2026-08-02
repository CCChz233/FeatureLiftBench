# Design card: puremagic__signature_resource_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `puremagic`  
**repository_url:** https://github.com/cdgriffith/puremagic  
**replacement_slot:** `resource-direct-02`  
**final_lift_type:** Direct  
**feature_family:** resource_metadata_loading  
**entanglement:** resource_coupling  
**feature_one_liner:** Bundled file-signature metadata detection  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

A separate resource-backed lookup feature with pinned local data and no network refresh.

## Pinned Source

- commit: `57bed56ef669132c0f906e1d064680bf2c4b2205`
- license: `MIT`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: none

## Required API

  - `featurelifted.from_string`
  - `featurelifted.from_stream`
  - `featurelifted.magic_string`
  - `featurelifted.from_extension`
  - `featurelifted.PureError`

## Included Behavior

  - byte-string detection
  - stream detection
  - MIME selection
  - extension metadata lookup
  - unknown input errors

## Excluded Behavior

  - CLI
  - deep archive scanners
  - large fixture corpus
  - network lookups

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
