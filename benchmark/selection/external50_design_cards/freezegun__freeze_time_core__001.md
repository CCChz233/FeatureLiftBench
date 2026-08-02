# Design card: freezegun__freeze_time_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `freezegun`  
**repository_url:** https://github.com/spulec/freezegun  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** protocol_state_transition  
**entanglement:** config_environment_coupling  
**feature_one_liner:** freeze_time tick/move API without real clock  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.freeze_time(time_to_freeze=None, tick: bool = False, ...)"
  - "context manager and decorator forms"
  - "frozen_time.move_to / tick APIs if included"
returns:
  - "context yields FrozenDateTimeFactory"
exceptions:
  - "declare"
defaults:
  - "tick=False"
state_effects:
  - "patches datetime/time \u2014 must stop"
```

## upstream_mapping

```yaml
primary_symbols:
  - "freezegun.freeze_time"
supporting_components:
  - "freezegun.api"
semantic_delta:
  - "Test-only time freeze facade"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted datetime patching.
```

## scope

```yaml
included:
  - "freeze, tick, move_to, decorator"
excluded:
  - "patching third-party C extensions clocks"
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
offline_resources: "no network"
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

- Staging path: `benchmark/staging/freezegun__freeze_time_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
