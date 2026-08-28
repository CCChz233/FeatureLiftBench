# Design card: cherrypy__dispatch_tool_core__001

**status:** `design_card_ready`  
**disposition:** `backup`  
**wave:** `backup`  
**package:** `CherryPy`  
**repository_url:** https://github.com/cherrypy/cherrypy  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `framework_coupling`, `implicit_dependency_coupling`  
**feature_one_liner:** CherryPy request dispatch and Tools hooks  
**commit:** `1f75bc9eed8e0e385f64f368bd69f58d96fb8c2b`  

## paper_fit

Backup framework dispatch if falcon/connexion blocked.

## why_hard

Tools registry + dispatch; huge unused servers.

## Balance Role

registry_plugin_dispatch / Composite / high entanglement.

## Pinned Source

- commit: `1f75bc9eed8e0e385f64f368bd69f58d96fb8c2b`
- license: BSD-3-Clause
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Application; _cptools; expose

## Included Behavior (draft)

URL dispatch; tool hook; 404

## Excluded Behavior

production server sockets

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
  commit: 1f75bc9eed8e0e385f64f368bd69f58d96fb8c2b
  license: BSD-3-Clause
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
