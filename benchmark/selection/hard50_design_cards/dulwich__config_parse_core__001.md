# Design card: dulwich__config_parse_core__001

**status:** `materialized_candidate`  
**disposition:** `selected`  
**wave:** `copyheavy_swap`  
**package:** `dulwich`  
**repository_url:** https://github.com/jelmer/dulwich  
**planned_lift_type:** Adapted  
**final_lift_type:** pending_source_review  
**reclassification_reason:** Replaces `django_environ__env_cast_core__001` (Flash copy_heavy_pass, RRES≈0.99 on a slice-sized repo).  
**feature_family:** `config_resolve_discover`  
**entanglement.level:** high  
**entanglement.types:** `config_environment_coupling`, `data_model_coupling`  
**feature_one_liner:** Git config file parse without porcelain, pack, or network  
**commit:** `2f039e67903559e279cb61250c6ea31bfa5f727c`  

## paper_fit

RQ2: Git config slice inside a large porcelain/pack tree. Copy-all of the rewritten Dulwich package is a real unused decoy, not padding.

## why_hard

Section tuples, subsections, and boolean values live in `ConfigFile`; copying porcelain/pack/network modules is the wrong closure and should inflate RRES.

## Balance Role

config_resolve_discover / Adapted / high entanglement. Swap-in for a small-repo copy-heavy Flash pass.

## Pinned Source

- commit: `2f039e67903559e279cb61250c6ea31bfa5f727c`
- license: Apache-2.0 OR GPL-2.0-or-later
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

ConfigFile; from_file; from_path; get; get_boolean

## Included Behavior (draft)

core filemode; remote origin url subsection; boolean true; missing key KeyError

## Excluded Behavior

git protocol; pack files; working trees; network; runtime import of dulwich

## YAML contract (to fill at pin time)

```yaml
target_api:
  module: featurelifted
  signatures:
    - ConfigFile.from_file
    - ConfigFile.from_path
    - ConfigFile.get
    - ConfigFile.get_boolean
  returns:
  exceptions:
    - KeyError
  defaults:
  state_effects:
upstream_mapping:
  primary_symbols:
    - dulwich.config.ConfigFile
  supporting_components:
    - dulwich.file
    - dulwich._typing
  semantic_delta: package renamed to featurelifted; porcelain/pack unused
oracle_basis:
  basis: upstream
scope:
  included:
    - from_file core values
    - subsection keys
    - boolean values
    - missing key KeyError
  excluded:
    - git protocol
    - pack files
    - network
feasibility:
  commit: 2f039e67903559e279cb61250c6ea31bfa5f727c
  license: Apache-2.0 OR GPL-2.0-or-later
  python_versions: "3.12"
  native_or_heavy_dependencies: rust crates unused by this slice
  offline_resources: none
acceptance:
  closure_review: pending
  reference_pass: pending
  isolation_pass: pending
  no_original_import: pending
  overlap_check: pass_name_screen
```

## Gate Status

- design card: pinned
- package completeness: materialized in `benchmark/hard50_pilot/dulwich__config_parse_core__001`
- local oracle/naive/copy-all: pass / fail / pass (RRES ≈ 34.7; true rewritten Dulwich package, not padding)
- Docker / Flash calibration: pending after remaining compactness swaps
- promotion to `benchmark/hard50`: blocked until compactness swaps finish
