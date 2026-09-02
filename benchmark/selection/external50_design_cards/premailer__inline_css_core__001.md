# Design card: premailer__inline_css_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `premailer`  
**repository_url:** https://github.com/peterbe/premailer  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Parse HTML+CSS and inline styles into result HTML  
**lift_review_flag:** none

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Premailer(html: str, **options).transform() -> str"
  - "options: remove_classes, strip_important, keep_style_tags \u2014 declare subset"
  - "featurelifted.transform(html: str, **options) convenience if kept"
returns:
  - "HTML string with inlined styles"
exceptions:
  - "document upstream exceptions if any"
defaults:
  - "option defaults frozen in TASK"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "premailer.Premailer"
  - "premailer.transform"
supporting_components:
  - "cssutils / lxml via premailer \u2014 treat as deps"
semantic_delta:
  - "HTML parse + CSS parse + inline merge"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  May pull cssutils/lxml; pin versions; no network.
```

## scope

```yaml
included:
  - "style tag and inline style merging for simple HTML"
excluded:
  - "fetch external stylesheets over HTTP"
  - "email send"
```

## feasibility

```yaml
commit: "f4ded0b9701c4985e7ff5c5beda83324c264ea62"  # tag 3.10.0-master
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "lxml may use binary wheels"
offline_resources: "HTML/CSS strings only; disable URL loading"
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

- Staging path: `benchmark/staging/premailer__inline_css_core__001/`
- Skim pass @ 3.10.0-master (`f4ded0b9701c…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
