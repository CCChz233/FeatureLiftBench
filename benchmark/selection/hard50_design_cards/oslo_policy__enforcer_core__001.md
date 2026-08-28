# Design card: oslo_policy__enforcer_core__001

**status:** `materialized_candidate`  
**disposition:** `backup`  
**wave:** `backup`  
**package:** `oslo.policy`  
**repository_url:** https://github.com/openstack/oslo.policy  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `registry_plugin_dispatch`  
**entanglement.level:** high  
**entanglement.types:** `implicit_dependency_coupling`, `config_environment_coupling`  
**feature_one_liner:** Policy enforcer with registered rules  
**commit:** `69890e47048014944c80aae27f82941a598fb573`  

## paper_fit

Backup for registry slot: policy rule registry.

## why_hard

Rule parsers + enforcer; same family as oslo.config.

## Balance Role

registry_plugin_dispatch / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Enforcer; Rule; register

## Included Behavior (draft)

load rules; enforce; default rule

## Excluded Behavior

OpenStack service policy.json farms

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
