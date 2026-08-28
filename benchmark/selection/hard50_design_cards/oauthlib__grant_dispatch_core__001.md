# Design card: oauthlib__grant_dispatch_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `oauthlib`  
**repository_url:** https://github.com/oauthlib/oauthlib  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `data_model_coupling`  
**feature_one_liner:** OAuth2 grant-type request validator dispatch  
**commit:** `40b0ab56da3682c2484a4b78bbff309f8025d950`  

## paper_fit

RQ1 protocol dispatch: grant type is a registry of handlers.

## why_hard

Validator callbacks and grant classes are split; copy of tokens.py is insufficient.

## Balance Role

registry_plugin_dispatch / Adapted / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

WebApplicationServer or Server; create_token_response

## Included Behavior (draft)

authorization code grant happy path with stub validator; invalid grant error

## Excluded Behavior

JWT/OIDC extras; HTTP servers

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
