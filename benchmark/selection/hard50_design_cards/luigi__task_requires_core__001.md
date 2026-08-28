# Design card: luigi__task_requires_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `luigi`  
**repository_url:** https://github.com/spotify/luigi  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `workflow_session_orchestration`  
**entanglement.level:** high  
**entanglement.types:** `implicit_dependency_coupling`, `resource_coupling`  
**feature_one_liner:** Task requires/output with local target and build  
**commit:** pending pin  

## paper_fit

RQ2+RQ4: DAG orchestration with a huge unused contrib/ tree.

## why_hard

requires() graph + complete() + targets; copy scheduler web fails compactness.

## Balance Role

workflow_session_orchestration / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Task; LocalTarget; build; requires

## Included Behavior (draft)

diamond requires; complete(); local file target

## Excluded Behavior

central scheduler HTTP; hdfs; spark

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
