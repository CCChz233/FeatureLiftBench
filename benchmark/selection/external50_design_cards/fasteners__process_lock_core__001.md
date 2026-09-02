# Design card: fasteners__process_lock_core__001

**status:** `design_card_ready`  
**wave:** W5  
**package:** `fasteners`  
**repository_url:** https://github.com/harlowja/fasteners  
**planned_lift_type:** Direct  
**final_lift_type:** Direct  
**reclassification_reason:** None  
**feature_family:** resource_metadata_loading  
**entanglement:** resource_coupling  
**feature_one_liner:** InterProcessLock acquire/release  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.InterProcessLock(path: str)"
  - "acquire(blocking: bool = True) / release / __enter__/__exit__"
returns:
  - "acquire returns bool"
exceptions:
  - "Threading conflicts declare"
defaults:
  - "blocking=True"
state_effects:
  - "creates lock file in temp"
```

## upstream_mapping

```yaml
primary_symbols:
  - "fasteners.process_lock.InterProcessLock"
supporting_components:
semantic_delta:
  - "Direct"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Use tmp_path lock files.
```

## scope

```yaml
included:
  - "acquire/release/context manager"
excluded:
  - "redis locks, readers-writer unless listed"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "Apache-2.0"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "local filesystem"
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

- Staging path: `benchmark/staging/fasteners__process_lock_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
