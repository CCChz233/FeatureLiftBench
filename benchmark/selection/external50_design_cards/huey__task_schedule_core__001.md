# Design card: huey__task_schedule_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `huey`  
**repository_url:** https://github.com/coleifer/huey  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** workflow_session_orchestration  
**entanglement:** framework_coupling  
**feature_one_liner:** Task define + crontab schedule + result read  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.MemoryHuey(name: str = ...)"
  - "featurelifted.Huey.task() decorator"
  - "featurelifted.Task.then / call / schedule APIs used"
  - "featurelifted.crontab(minute='*', ...) schedule helper"
  - "featurelifted.Huey.execute / result store get"
returns:
  - "task result values via Result"
exceptions:
  - "TaskException declare"
defaults:
  - "MemoryHuey immediate/eager mode for tests \u2014 declare"
state_effects:
  - "in-memory broker state"
```

## upstream_mapping

```yaml
primary_symbols:
  - "huey.api.Huey"
  - "huey.api.MemoryHuey"
  - "huey.api.crontab"
supporting_components:
  - "huey.storage"
  - "huey.consumer excluded"
semantic_delta:
  - "task + crontab + memory result compose; eager execution in tests"
```

## oracle_basis

```yaml
basis: mixed
notes: |
  No Redis; MemoryHuey only.
```

## scope

```yaml
included:
  - "define tasks, enqueue, crontab schedule objects, fetch results in memory"
excluded:
  - "RedisHuey, consumer process, signals"
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
offline_resources: "MemoryHuey"
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

- Staging path: `benchmark/staging/huey__task_schedule_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
