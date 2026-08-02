# Design card: furl__url_mutate_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `furl`  
**repository_url:** https://github.com/gruns/furl  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** protocol_state_transition  
**entanglement:** data_model_coupling  
**feature_one_liner:** furl URL mutate/query API (offline)  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.furl(url: str = '')"
  - "attributes set: scheme/host/port/path/query/fragment"
  - "featurelifted.furl.set / add / remove / join / url / pathstr / querystr"
returns:
  - "furl object; .url str"
exceptions:
  - "declare ValueError cases"
defaults:
  - "empty url"
state_effects:
  - "mutable furl"
```

## upstream_mapping

```yaml
primary_symbols:
  - "furl.furl"
supporting_components:
  - "furl.Path"
  - "furl.Query"
semantic_delta:
  - "Mutation-oriented URL API packaging"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted URL model.
```

## scope

```yaml
included:
  - "parse, mutate query/path, serialize"
excluded:
  - "network"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "Unlicense"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "strings"
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

- Staging path: `benchmark/staging/furl__url_mutate_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
