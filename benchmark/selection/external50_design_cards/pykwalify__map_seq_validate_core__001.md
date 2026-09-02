# Design card: pykwalify__map_seq_validate_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `pykwalify`  
**repository_url:** https://github.com/Grokzen/pykwalify  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** validate_normalize_construct  
**entanglement:** data_model_coupling  
**feature_one_liner:** Map/Seq schema validate + extension hooks  
**lift_review_flag:** none

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Core(source_data=dict, schema_data=dict).validate()"
  - "schema types map/seq/str/int/bool/any \u2014 declare"
  - "featurelifted.SchemaError / Core validation error reporting"
returns:
  - "validate returns True or raises; document"
exceptions:
  - "SchemaError, PyKwalifyException names as upstream"
defaults:
  - "declare"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "pykwalify.core.Core"
supporting_components:
  - "pykwalify.rule"
  - "pykwalify.errors"
semantic_delta:
  - "Rule tree + core validate composition"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Dict schema validation only.
```

## scope

```yaml
included:
  - "map/seq nested validate, required keys, type checks"
excluded:
  - "YAML file path loading from disk unless fixture; extensions ecosystem"
```

## feasibility

```yaml
commit: "4359ddf1edfe6cff13a183f3142c5970ed1dbbd7"  # tag 1.8.0
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "in-memory dict schemas"
```

## acceptance

```yaml
closure_review: pass
reference_pass: pass
isolation_pass: pass
no_original_import: pass
overlap_check: pass
```

## agent_notes

- Staging path: `benchmark/staging/pykwalify__map_seq_validate_core__001/`
- Skim pass @ 1.8.0 (`4359ddf1edfe…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
