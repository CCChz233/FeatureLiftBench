# Design card: trio__nursery_cancel_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `trio`  
**repository_url:** https://github.com/python-trio/trio  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `workflow_session_orchestration`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `data_model_coupling`  
**feature_one_liner:** Nursery start and CancelScope timeout/cancel  
**commit:** pending pin  

## paper_fit

RQ4 lifecycle/cancel Hidden. Distinct from tenacity retry in 150.

## why_hard

Structured concurrency invariants; copying trio.socket fails isolation.

## Balance Role

workflow_session_orchestration / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

trio.run; open_nursery; CancelScope; would_block clocks via trio.testing

## Included Behavior (draft)

child task complete; cancel scope; timeout

## Excluded Behavior

guest-mode; IOCP; real sockets

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
