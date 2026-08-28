# Design card: authlib__oauth2_server_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `authlib`  
**repository_url:** https://github.com/lepture/authlib  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `workflow_session_orchestration`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `data_model_coupling`  
**feature_one_liner:** OAuth2 authorization-code token issuance with in-memory grants  
**commit:** pending pin  

## paper_fit

RQ1 session protocol. joserfc/pyjwt in E50 are token codecs, not grant workflow.

## why_hard

Grant registry + validator + token mixing; token-only extract fails Hidden.

## Balance Role

workflow_session_orchestration / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

AuthorizationServer; AuthorizationCodeGrant; save_token

## Included Behavior (draft)

create_authorization_response; create_token_response; invalid client

## Excluded Behavior

Flask/Django full apps; JWK cloud KMS

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
