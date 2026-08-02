# Design card: toolz__compose_pipe_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `toolz`  
**repository_url:** https://github.com/pytoolz/toolz  
**planned_lift_type:** Composite  
**final_lift_type:** Direct  
**reclassification_reason:** Thin extract of functoolz compose/pipe/curry. Planned Composite → Direct.  
**feature_family:** algorithm_data_structure  
**entanglement:** data_model_coupling  
**feature_one_liner:** compose/pipe/curry function pipeline utilities  
**lift_review_flag:** May be Direct/Adapted if target is thin extract of functoolz compose/pipe/curry

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.compose(*funcs)"
  - "featurelifted.pipe(data, *funcs)"
  - "featurelifted.curry(func, *args, **kwargs)"
  - "featurelifted.identity optional"
returns:
  - "compose returns callable; pipe returns value; curry returns curried callable"
exceptions:
  - "TypeError on bad call arities"
defaults:
  - "curry underscores partial application rules as upstream"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "toolz.functoolz.compose"
  - "toolz.functoolz.pipe"
  - "toolz.functoolz.curry"
supporting_components:
semantic_delta:
  - "Direct extract"
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
  - "compose, pipe, curry basic"
excluded:
  - "cytoolz, parallelism"
```

## feasibility

```yaml
commit: "568c2b8393973cd172a466546c9d95779c452438"  # tag 1.1.0
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none (pytoolz)"
offline_resources: "pure functions"
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

- Staging path: `benchmark/staging/toolz__compose_pipe_core__001/`
- Skim pass @ 1.1.0 (`568c2b839397…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
