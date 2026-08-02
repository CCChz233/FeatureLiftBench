# Design card: hyperlink__url_parse_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `hyperlink`  
**repository_url:** https://github.com/python-hyper/hyperlink  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** protocol_state_transition  
**entanglement:** data_model_coupling  
**feature_one_liner:** hyperlink.URL parse/replace API  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.URL.from_text(text: str) -> URL"
  - "featurelifted.URL.replace(**parts) -> URL"
  - "featurelifted.URL.click(relative) / to_text()"
  - "attributes: scheme, userinfo, host, port, path, query, fragment"
returns:
  - "URL immutable; to_text str"
exceptions:
  - "URLParseError / ValueError declare"
defaults:
  - "declare"
state_effects:
  - "immutable"
```

## upstream_mapping

```yaml
primary_symbols:
  - "hyperlink.URL"
supporting_components:
semantic_delta:
  - "Immutable URL adapted surface"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted.
```

## scope

```yaml
included:
  - "from_text, replace, to_text, query manipulation"
excluded:
  - "network resolve"
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

- Staging path: `benchmark/staging/hyperlink__url_parse_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
