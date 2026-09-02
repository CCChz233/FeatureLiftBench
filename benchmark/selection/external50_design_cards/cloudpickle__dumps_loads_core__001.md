# Design card: cloudpickle__dumps_loads_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `cloudpickle`  
**repository_url:** https://github.com/cloudpipe/cloudpickle  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** data_model_coupling  
**feature_one_liner:** cloudpickle dumps/loads for dynamic callables  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.dumps(obj, protocol=None) -> bytes"
  - "featurelifted.loads(data: bytes) -> Any"
  - "featurelifted.CloudPickler if needed"
returns:
  - "bytes; objects"
exceptions:
  - "PicklingError"
defaults:
  - "protocol default"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "cloudpickle.dumps"
  - "cloudpickle.loads"
supporting_components:
semantic_delta:
  - "Dynamic function pickling adapted from pickle"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Roundtrip nested functions.
```

## scope

```yaml
included:
  - "dumps/loads for local functions and closures supported by cloudpickle"
excluded:
  - "interactive __main__ edge cases unless listed"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "bytes"
```

## acceptance

```yaml
closure_review: pending
reference_pass: pending
isolation_pass: pending
no_original_import: pending
overlap_check: pending
```

## agent_notes

- Staging path: `benchmark/staging/cloudpickle__dumps_loads_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
