# Design card: python_statemachine__json_workflow_core__001

**status:** `reference_static_validated`  
**wave:** R1  
**package:** `python-statemachine`  
**repository_url:** https://github.com/fgmacedo/python-statemachine  
**replacement_slot:** `workflow-composite-config-02`  
**final_lift_type:** Composite  
**feature_family:** workflow_session_orchestration  
**entanglement:** config_environment_coupling  
**feature_one_liner:** JSON-defined statechart workflow  
**lift_review_flag:** none

**source_review:** `pass` (2026-08-01)  
**contract_review:** `pass` (2026-08-01)  
**reference_review:** `pass` (2026-08-01)  
**isolation_review:** `static_pass`

## Balance Role

A session or workflow planner whose environment/config inputs can be frozen in tests.

## Pinned Source

- commit: `d911f537f557f0f6a5de2ceedd6fde9a451b6ada`
- license: `MIT`
- source kind: real external OSS repository
- network during evaluation: forbidden
- allowed runtime dependencies: none

## Required API

  - `featurelifted.load`
  - `featurelifted.StateChart`
  - `featurelifted.InvalidDefinition`

## Included Behavior

  - inline JSON loading
  - initial state selection
  - event-driven transitions
  - safe default expression mode

## Excluded Behavior

  - YAML and SCXML
  - schema validation
  - trusted eval
  - Django integration

## Gate Status

- package completeness: pass
- explicit public API contract: pass
- reference tests: pass
- static isolation and forbidden-import checks: pass
- Docker evaluation: pending
- promotion to `benchmark/tasks`: blocked until the complete External-50 gate passes
