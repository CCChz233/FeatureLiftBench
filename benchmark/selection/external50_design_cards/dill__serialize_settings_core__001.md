# Design card: dill__serialize_settings_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `dill`  
**repository_url:** https://github.com/uqfoundation/dill  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** data_model_coupling  
**feature_one_liner:** dill dumps/loads with settings/recurse facade  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.dumps(obj, protocol=None, byref=None, fmode=None, recurse=None) -> bytes"
  - "featurelifted.loads(s: bytes) -> Any"
  - "featurelifted.dump/load file variants if included"
  - "featurelifted.settings / detect as needed \u2014 declare"
returns:
  - "bytes; reconstituted objects"
exceptions:
  - "PicklingError"
defaults:
  - "protocol defaults as dill"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "dill.dumps"
  - "dill.loads"
supporting_components:
  - "dill.settings"
semantic_delta:
  - "Settings/flags as adapted surface over pickle-compatible API"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Serialize simple callables/closures subset.
```

## scope

```yaml
included:
  - "dumps/loads roundtrip for functions/lambdas supported by dill"
excluded:
  - "interactive session dump tricks, undetected objects"
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
offline_resources: "in-memory bytes"
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

- Staging path: `benchmark/staging/dill__serialize_settings_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
