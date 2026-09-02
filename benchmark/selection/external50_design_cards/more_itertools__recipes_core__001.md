# Design card: more_itertools__recipes_core__001

**status:** `design_card_ready`  
**wave:** W5  
**package:** `more-itertools`  
**repository_url:** https://github.com/more-itertools/more-itertools  
**planned_lift_type:** Direct  
**final_lift_type:** Direct  
**reclassification_reason:** None  
**feature_family:** algorithm_data_structure  
**entanglement:** data_model_coupling  
**feature_one_liner:** Extract recipes/chunked/windowed-style helpers  
**lift_review_flag:** Confirm Direct; recipes module is usually direct extract

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.chunked(iterable, n)"
  - "featurelifted.sliced(seq, n)"
  - "featurelifted.consume / first / one / only / unique_everseen / windowed \u2014 declare exact set from recipes/more"
returns:
  - "iterators/values per helper"
exceptions:
  - "ValueError for one/only failures"
defaults:
  - "declare"
state_effects:
  - "consume advances iterators"
```

## upstream_mapping

```yaml
primary_symbols:
  - "more_itertools.recipes"
  - "more_itertools.more"
supporting_components:
semantic_delta:
  - "Direct toolkit extract"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Direct.
```

## scope

```yaml
included:
  - "listed helpers only"
excluded:
  - "entire more_itertools surface"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "pure"
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

- Staging path: `benchmark/staging/more_itertools__recipes_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
