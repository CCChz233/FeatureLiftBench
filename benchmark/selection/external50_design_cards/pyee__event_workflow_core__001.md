# Design card: pyee__event_workflow_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `pyee`  
**repository_url:** https://github.com/jfhbrook/pyee  
**replacement_slot:** `workflow-composite-third-party-03`  
**final_lift_type:** Composite  
**feature_family:** workflow_session_orchestration  
**entanglement:** third_party_dependency_coupling  
**feature_one_liner:** Event-emitter workflow orchestration  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

An offline orchestration pipeline using one allowlisted pure-Python dependency.

## Pinned Source

- commit: `661fe6a4e144a0ce205d1e900836157208b79122`
- license: `MIT`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: typing-extensions

## Required API

  - `featurelifted.EventEmitter`
  - `featurelifted.PyeeError`

## Included Behavior

  - on/listens_to registration
  - ordered emit
  - once
  - listener removal
  - error event semantics

## Excluded Behavior

  - asyncio, Trio, Twisted, and executor emitters
  - thread scheduling
  - network integration

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
