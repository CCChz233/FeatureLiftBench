# Design card: stamina__retry_context_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `stamina`  
**repository_url:** https://github.com/hynek/stamina  
**replacement_slot:** `cache-direct-third-party-02`  
**final_lift_type:** Direct  
**feature_family:** cache_retry_policy  
**entanglement:** third_party_dependency_coupling  
**feature_one_liner:** Retry decorator and context policy  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

A bounded policy feature with one allowlisted pure-Python dependency and offline wheels.

## Pinned Source

- commit: `ab12cbf7d5e06c31344f4d43246d4be9930245f7`
- license: `MIT`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: tenacity

## Required API

  - `featurelifted.retry`
  - `featurelifted.retry_context`
  - `featurelifted.Attempt`
  - `featurelifted.set_active`
  - `featurelifted.set_testing`

## Included Behavior

  - sync retry decorator
  - retry_context attempt iterator
  - global active/testing configuration

## Excluded Behavior

  - async and Trio integration
  - logging instrumentation adapters
  - non-zero sleeps in evaluator tests

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
