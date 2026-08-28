# Design card: dependency_injector__container_core__001

**status:** `design_card_ready`  
**disposition:** `selected`  
**wave:** `selected`  
**package:** `dependency-injector`  
**repository_url:** https://github.com/ets-labs/python-dependency-injector  
**planned_lift_type:** Composite  
**final_lift_type:** pending_source_review  
**reclassification_reason:**  
**feature_family:** `validate_normalize_construct`  
**entanglement.level:** high  
**entanglement.types:** `implicit_dependency_coupling`, `framework_coupling`  
**feature_one_liner:** Declarative container providers and wiring  
**commit:** pending pin  

## paper_fit

RQ4 construct+registry: DI graph is the extraction target.

## why_hard

Provider graph and wiring by name; copying examples/flask fails isolation.

## Balance Role

validate_normalize_construct / Composite / high entanglement.

## Pinned Source

- commit: *pending pin — do not materialize until a real revision is recorded*
- license: *pending pin*
- source kind: real external OSS repository
- network during evaluation: forbidden
- overlap_check: not in Python-150 or External-50 registries (2026-08-27 name/url screen)

## Required API (draft)

DeclarativeContainer; providers.Factory; providers.Singleton; container.wire

## Included Behavior (draft)

factory vs singleton identity; override; missing provider

## Excluded Behavior

Flask/Django wiring extras beyond declared

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
