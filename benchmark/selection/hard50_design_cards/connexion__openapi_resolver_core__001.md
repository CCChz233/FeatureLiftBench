# Design card: connexion__openapi_resolver_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `connexion`  
**repository_url:** https://github.com/spec-first/connexion  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `implicit_dependency_coupling`  
**feature_one_liner:** OpenAPI operationId resolver to Python view  
**commit:** `a23d44e0e0421fd83f5ba132269bcfd04b855a16`  

## paper_fit

RQ1 framework_plugin: spec-driven dispatch, not greenfield Flask.

## why_hard

Resolver+spec+framework coupling; E50 flask_cors never required spec closure.

## Balance Role

registry_plugin_dispatch / Composite / high entanglement.

## Pinned Source

- commit: `a23d44e0e0421fd83f5ba132269bcfd04b855a16`
- license: Apache-2.0
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

ConnexionMiddleware or FlaskApp resolver; add_api

## Included Behavior (draft)

resolve operationId; validation error on missing required; mock backend

## Excluded Behavior

live HTTP servers; cloud auth

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
  commit: a23d44e0e0421fd83f5ba132269bcfd04b855a16
  license: Apache-2.0
  python_versions:
  native_or_heavy_dependencies:
  offline_resources:
acceptance:
  closure_review: pending
  reference_pass: pass
  isolation_pass: pass
  no_original_import: pass
  overlap_check: pass_name_screen
```

## Gate Status

- design card: ready for pin
- package completeness: pending
- Docker / Flash calibration: pending
- promotion to `benchmark/hard50`: blocked until Pilot gate (and then 50/50) passes
