# Design card: portalocker__file_lock_core__001

**status:** `design_card_ready`  
**wave:** W5  
**package:** `portalocker`  
**repository_url:** https://github.com/WoLpH/portalocker  
**planned_lift_type:** Direct  
**final_lift_type:** Direct  
**reclassification_reason:** None  
**feature_family:** resource_metadata_loading  
**entanglement:** resource_coupling  
**feature_one_liner:** portalocker file lock API  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.lock(file, flags=LOCK_EX)"
  - "featurelifted.unlock(file)"
  - "featurelifted.Lock(filename, mode='a', timeout=...) context manager"
  - "constants LOCK_EX/LOCK_SH/LOCK_NB"
returns:
  - "Lock context yields file object"
exceptions:
  - "LockException / AlreadyLocked \u2014 declare"
defaults:
  - "timeout defaults"
state_effects:
  - "locks files"
```

## upstream_mapping

```yaml
primary_symbols:
  - "portalocker.lock"
  - "portalocker.Lock"
supporting_components:
semantic_delta:
  - "Direct"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  tmp files.
```

## scope

```yaml
included:
  - "exclusive lock context manager"
excluded:
  - "redis lock"
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
offline_resources: "local FS"
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

- Staging path: `benchmark/staging/portalocker__file_lock_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
