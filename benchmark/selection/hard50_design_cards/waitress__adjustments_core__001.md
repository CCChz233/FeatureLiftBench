# Design card: waitress__adjustments_core__001

**status:** `isolation_blocked`  
**disposition:** `backup`  
**wave:** `pilot_swap`  
**package:** `waitress`  
**repository_url:** https://github.com/Pylons/waitress  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `config_environment_coupling`, `framework_coupling`  
**feature_one_liner:** Waitress Adjustments from kwargs/env  
**commit:** `7a855a2d36e4a672b4ff2db8c8483dde3de590dd`  

## paper_fit

Backup config object inside a server (copy-all trap).

## why_hard

Many knobs; Hidden checks aliases and validation.

## Balance Role

config_resolve_discover / Adapted / high entanglement.

## Pinned Source

- commit: `7a855a2d36e4a672b4ff2db8c8483dde3de590dd`
- license: ZPL-2.1
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

Adjustments; parse_args subset

## Included Behavior (draft)

host/port/threads; invalid value

## Excluded Behavior

real listen sockets

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
