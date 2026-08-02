# Design card: ftfy__fix_text_core__001

**status:** `design_card_ready`  
**wave:** W5  
**package:** `ftfy`  
**repository_url:** https://github.com/rspeer/python-ftfy  
**planned_lift_type:** Direct  
**final_lift_type:** Direct  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** parser_state_coupling  
**feature_one_liner:** ftfy.fix_text mojibake repair  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.fix_text(text: str, ...) -> str"
  - "featurelifted.guess_bytes if included"
  - "config flags: normalization, explain \u2014 declare"
returns:
  - "fixed unicode str"
exceptions:
  - "declare"
defaults:
  - "ftfy defaults frozen"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "ftfy.fix_text"
supporting_components:
semantic_delta:
  - "Direct"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Mojibake fixtures.
```

## scope

```yaml
included:
  - "fix_text common mojibake cases"
excluded:
  - "cli"
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

- Staging path: `benchmark/staging/ftfy__fix_text_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
