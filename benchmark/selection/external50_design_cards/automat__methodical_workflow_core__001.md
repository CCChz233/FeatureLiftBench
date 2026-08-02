# Design card: automat__methodical_workflow_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `Automat`  
**repository_url:** https://github.com/glyph/automat  
**replacement_slot:** `workflow-composite-framework-01`  
**final_lift_type:** Composite  
**feature_family:** workflow_session_orchestration  
**entanglement:** framework_coupling  
**feature_one_liner:** Methodical state-machine workflow  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

A deterministic in-process workflow with explicit state transitions and no worker service.

## Pinned Source

- commit: `bd5651c7970d2b4bfaa197f23777e469c5060e81`
- license: `MIT`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: none

## Required API

  - `featurelifted.MethodicalMachine`
  - `featurelifted.NoTransition`

## Included Behavior

  - state/input/output decorators
  - upon transition wiring
  - serializer and unserializer
  - unhandled input errors

## Excluded Behavior

  - Graphviz rendering
  - Twisted integration
  - command-line visualization

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
