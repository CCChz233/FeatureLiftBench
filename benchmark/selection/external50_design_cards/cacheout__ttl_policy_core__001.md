# Design card: cacheout__ttl_policy_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `cacheout`  
**repository_url:** https://github.com/dgilland/cacheout  
**replacement_slot:** `cache-direct-config-01`  
**final_lift_type:** Direct  
**feature_family:** cache_retry_policy  
**entanglement:** config_environment_coupling  
**feature_one_liner:** Configurable TTL and LRU cache policy  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

A deterministic cache or retry policy with explicit defaults and no service dependency.

## Pinned Source

- commit: `ab709979deafd7e241050a9fa8ce8463d70a10fb`
- license: `MIT`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: none

## Required API

  - `featurelifted.Cache`
  - `featurelifted.LRUCache`

## Included Behavior

  - cache get/set/delete
  - TTL expiry with an injected timer
  - LRU eviction and configure updates

## Excluded Behavior

  - async wrappers
  - global cache manager
  - random-replacement policies

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
