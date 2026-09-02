# Design card: jsonpickle__handler_roundtrip_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `jsonpickle`  
**repository_url:** https://github.com/jsonpickle/jsonpickle  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** data_model_coupling  
**feature_one_liner:** encode/decode with handler registration facade  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.encode(obj, unpicklable: bool = True, make_refs: bool = True) -> str"
  - "featurelifted.decode(string: str) -> Any"
  - "featurelifted.register(cls, handler)"
  - "featurelifted.handlers.BaseHandler"
returns:
  - "JSON string; decoded objects"
exceptions:
  - "declare"
defaults:
  - "unpicklable=True"
state_effects:
  - "global handler registry \u2014 reset between tests"
```

## upstream_mapping

```yaml
primary_symbols:
  - "jsonpickle.encode"
  - "jsonpickle.decode"
  - "jsonpickle.register"
supporting_components:
  - "jsonpickle.handlers"
semantic_delta:
  - "Handler registration adapted surface"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Reset handlers in fixtures.
```

## scope

```yaml
included:
  - "encode/decode, custom handler for a sample class"
excluded:
  - "numpy/pandas backends"
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
offline_resources: "in-memory"
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

- Staging path: `benchmark/staging/jsonpickle__handler_roundtrip_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
