# Design card: python_crontab__cron_item_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `python-crontab`  
**repository_url:** https://github.com/lyda/python-crontab  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** config_resolve_discover  
**entanglement:** parser_state_coupling  
**feature_one_liner:** CronItem / CronSlices parse and render  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.CronSlices(line: str)"
  - "featurelifted.CronItem(command=None, comment=None, user=None, pre_comment=False)"
  - "CronItem.setall / render / is_valid / schedule frequency helpers used \u2014 declare"
returns:
  - "slices/item; render returns cron line str"
exceptions:
  - "ValueError on invalid slices"
defaults:
  - "declare"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "crontab.CronSlices"
  - "crontab.CronItem"
supporting_components:
  - "crontab.CronTab excluded for file/user system"
semantic_delta:
  - "Item/slices without touching system crontab files"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  No /etc/crontab access.
```

## scope

```yaml
included:
  - "parse slice strings, render, validity"
excluded:
  - "reading user crontabs from OS"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "LGPL-3.0"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "strings only"
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

- Staging path: `benchmark/staging/python_crontab__cron_item_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
