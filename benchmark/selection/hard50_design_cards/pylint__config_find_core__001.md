# Design card: pylint__config_find_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `pylint`  
**repository_url:** https://github.com/pylint-dev/pylint  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `config_environment_coupling`, `parser_state_coupling`  
**feature_one_liner:** Find and merge pylint configuration from files  
**commit:** `46d7486dd3d1313165b901d52227037d14951495`  

## paper_fit

RQ1 discovery chain inside a large linter (copy-all trap).

## why_hard

Config search + checker enablement; extracting one checker misses merge order.

## Balance Role

config_resolve_discover / Adapted / high entanglement.

## Pinned Source

- commit: `46d7486dd3d1313165b901d52227037d14951495`
- license: GPL-2.0-or-later
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

find_default_config_files; PyLinter.load_commandline_configuration subset

## Included Behavior (draft)

discover pylintrc; disable messages from config; invalid option error

## Excluded Behavior

full lint of C extensions; rewrite checkers

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
  commit: 46d7486dd3d1313165b901d52227037d14951495
  license: GPL-2.0-or-later
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
