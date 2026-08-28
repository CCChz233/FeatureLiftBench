# Design card: webob__request_response_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `remaining_swap`  
**package:** `WebOb`  
**repository_url:** https://github.com/Pylons/webob  
**planned_lift_type:** Direct  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `direct_tooling_copytrap`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `data_model_coupling`  
**feature_one_liner:** WebOb Request/Response from environ  
**commit:** `c0d70f985ff6f04dcc59822ca5216cfd0ada666c`  

## paper_fit

Backup WSGI request object with Pyramid decoy nearby in ecosystem.

## why_hard

Ad-hoc dict environ vs Request API; Hidden header case.

## Balance Role

direct_tooling_copytrap / Direct / high entanglement.

## Pinned Source

- commit: `c0d70f985ff6f04dcc59822ca5216cfd0ada666c`
- license: MIT
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Request; Response; Request.blank

## Included Behavior (draft)

GET/POST; headers; json_body

## Excluded Behavior

full Pyramid (already in 150)

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

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/webob__request_response_core__001`
- local oracle/naive/copy-all: pass / fail / pass (RRES ≈ 1.94)
- Docker / Flash calibration: pending Phase 3
- promotion to `benchmark/hard50`: ready with the rest of the 50
