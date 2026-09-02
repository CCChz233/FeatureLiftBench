# Design card: strictyaml__schema_load_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `strictyaml`  
**repository_url:** https://github.com/crdoconnor/strictyaml  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** validate_normalize_construct  
**entanglement:** data_model_coupling  
**feature_one_liner:** Typed YAML schema validators + load/roundtrip  
**lift_review_flag:** none

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.load(yaml_string: str, schema, label: str = 'string')"
  - "validators: Map, Seq, Str, Int, Bool, Optional, MapPattern \u2014 declare set"
  - "YAML result .data for plain python"
  - "exceptions: YAMLValidationError, YAMLParseError (exact names)"
returns:
  - "YAML object; .data returns primitives"
exceptions:
  - "YAMLValidationError, StrictYAMLError"
defaults:
  - "label='string'"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "strictyaml.load"
  - "strictyaml.Map"
  - "strictyaml.Seq"
supporting_components:
  - "strictyaml validators module"
semantic_delta:
  - "Schema combinators + load as one contract"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Composite validators+load.
```

## scope

```yaml
included:
  - "Map/Seq/scalars, optional keys, validation errors"
excluded:
  - "ruamel round-trip fancy types beyond strictyaml"
```

## feasibility

```yaml
commit: "f19d2815bb733e3bf709a34281a62a25ccdfdc3a"  # tag 1.7.3
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "YAML strings"
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

- Staging path: `benchmark/staging/strictyaml__schema_load_core__001/`
- Skim pass @ 1.7.3 (`f19d2815bb73…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
