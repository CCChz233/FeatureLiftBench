# Design card: frictionless__schema_resource_validate_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `frictionless`  
**repository_url:** https://github.com/frictionlessdata/frictionless-py  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** validate_normalize_construct  
**entanglement:** data_model_coupling  
**feature_one_liner:** Schema + Resource + checklist validate pipeline  
**lift_review_flag:** none

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Schema.from_descriptor(descriptor: dict) -> Schema"
  - "featurelifted.Resource(data=...|path=..., schema=...) "
  - "featurelifted.Resource.validate() -> Report"
  - "featurelifted.Checklist / validate helpers used \u2014 declare"
  - "Report.valid / Report.tasks / error list accessors"
returns:
  - "Report with valid bool and errors"
exceptions:
  - "FrictionlessException subset"
defaults:
  - "declare"
state_effects:
  - "may read local files if path used \u2014 prefer inline data"
```

## upstream_mapping

```yaml
primary_symbols:
  - "frictionless.Schema"
  - "frictionless.Resource"
  - "frictionless.Report"
supporting_components:
  - "frictionless.checklist"
  - "frictionless.errors"
semantic_delta:
  - "Schema+Resource+Report pipeline; keep descriptors JSON-serializable"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Heavy package — shrink to table schema validate on inline rows.
```

## scope

```yaml
included:
  - "schema descriptor load, resource validate inline data, error collection"
excluded:
  - "remote URLs, SQL dialects, pandas full stack if avoidable"
```

## feasibility

```yaml
commit: "43a63e0be8f332f82177f62e0099e667a93bd77b"  # tag v5.19.0
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none expected"
offline_resources: "inline Python data only; no HTTP"
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

- Staging path: `benchmark/staging/frictionless__schema_resource_validate_core__001/`
- Skim pass @ v5.19.0 (`43a63e0be8f3…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
