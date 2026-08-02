# Design card: cachier__memoize_backend_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `cachier`  
**repository_url:** https://github.com/python-cachier/cachier  
**replacement_slot:** `cache-composite-third-party-03`  
**final_lift_type:** Composite  
**feature_family:** cache_retry_policy  
**entanglement:** third_party_dependency_coupling  
**feature_one_liner:** Memoization decorator and backend policy  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

Compose keying, expiration, and retry/eviction decisions without a live cache service.

## Pinned Source

- commit: `e5fd990d646b05764977fe20f3e846c9e3d59076`
- license: `MIT`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: portalocker, pympler, watchdog

## Required API

  - `featurelifted.cachier`
  - `featurelifted.set_default_params`
  - `featurelifted.get_default_params`
  - `featurelifted.enable_caching`
  - `featurelifted.disable_caching`

## Included Behavior

  - memory backend memoization
  - skip and overwrite controls
  - clear/precache methods
  - global enable/disable policy

## Excluded Behavior

  - MongoDB, Redis, SQL, and S3 services
  - background timing assertions
  - network access

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
