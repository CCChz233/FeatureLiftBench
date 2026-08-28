# Design card: oslo_config__opt_group_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `oslo.config`  
**repository_url:** https://github.com/openstack/oslo.config  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `config_environment_coupling`, `implicit_dependency_coupling`  
**feature_one_liner:** Cfg.CONF option groups with CLI and file overlay  
**commit:** pending pin  

## paper_fit

RQ4 global CONF + group registry, the classic implicit config closure.

## why_hard

Opts must be registered before parse; copy of cfg.py without Opt types fails.

## Balance Role

config_resolve_discover / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

ConfigOpts; Opt; OptGroup; CONF.register_opt; CONF

## Included Behavior (draft)

register opts; parse files; CLI override; default

## Excluded Behavior

OpenStack service projects; Oslo messaging

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
