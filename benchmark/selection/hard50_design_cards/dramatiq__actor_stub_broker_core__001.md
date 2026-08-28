# Design card: dramatiq__actor_stub_broker_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `dramatiq`  
**repository_url:** https://github.com/Bogdanp/dramatiq  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `workflow_session_orchestration`  
**entanglement.level:** high  
**entanglement.types:** `implicit_dependency_coupling`, `framework_coupling`  
**feature_one_liner:** Actor send/get with StubBroker middleware  
**commit:** pending pin  

## paper_fit

RQ4 actor registry + broker; unused brokers are copy-all decoy.

## why_hard

Global broker and middleware chain; extracting @actor decorator only fails.

## Balance Role

workflow_session_orchestration / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

actor; StubBroker; Middleware; get_broker

## Included Behavior (draft)

send message; middleware before/after; retries off

## Excluded Behavior

RabbitMQ/Redis brokers

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
