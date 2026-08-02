# Design card: invoke__collection_context_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `invoke`  
**repository_url:** https://github.com/pyinvoke/invoke  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** workflow_session_orchestration  
**entanglement:** framework_coupling  
**feature_one_liner:** Collection namespace + Context + task runners  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.task decorator"
  - "featurelifted.Collection(*tasks|**kwargs)"
  - "featurelifted.Context / MockContext for run()"
  - "featurelifted.Program or Executor subset used to invoke tasks \u2014 declare"
  - "Result stdout/stderr/exited"
returns:
  - "task return values; Result from run"
exceptions:
  - "UnexpectedExit, Failure \u2014 declare"
defaults:
  - "declare echo/pty defaults False"
state_effects:
  - "MockContext records run calls"
```

## upstream_mapping

```yaml
primary_symbols:
  - "invoke.task"
  - "invoke.Collection"
  - "invoke.Context"
supporting_components:
  - "invoke.runners"
  - "invoke.mock"
semantic_delta:
  - "Collection namespace + Context execution"
```

## oracle_basis

```yaml
basis: mixed
notes: |
  Use MockContext; do not spawn real shells if avoidable.
```

## scope

```yaml
included:
  - "build collection, call tasks with ctx, mock run"
excluded:
  - "real SSH fabric, config files discovery beyond declared"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "BSD-2-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "MockContext only"
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

- Staging path: `benchmark/staging/invoke__collection_context_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
