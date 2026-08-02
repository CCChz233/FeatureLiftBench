# Design card: venusian__scan_dispatch_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `venusian`  
**repository_url:** https://github.com/Pylons/venusian  
**replacement_slot:** `registry-composite-framework-01`  
**final_lift_type:** Composite  
**feature_family:** registry_plugin_dispatch  
**entanglement:** framework_coupling  
**feature_one_liner:** Decorator registry and scanner dispatch  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

A registry plus selection/dispatch flow with deterministic in-process plugins.

## Pinned Source

- commit: `d036c00afa4e8c3077ab53a22290ac19fed652b2`
- license: `BSD-derived`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: none

## Required API

  - `featurelifted.attach`
  - `featurelifted.Scanner`
  - `featurelifted.AttachInfo`
  - `featurelifted.lift`

## Included Behavior

  - attach callback metadata
  - module scanning
  - category filtering
  - scanner context injection

## Excluded Behavior

  - filesystem package walks in evaluator cases
  - zip imports
  - namespace package edge cases

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
