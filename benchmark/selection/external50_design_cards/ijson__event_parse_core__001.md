# Design card: ijson__event_parse_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `ijson`  
**repository_url:** https://github.com/ICRAR/ijson  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Incremental JSON event parse API  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.parse(file_or_bytes) -> iterator of (prefix, event, value)"
  - "featurelifted.items(file, prefix)"
  - "featurelifted.kvitems(file, prefix)"
  - "backend note: use pure python backend if possible (ijson.backends.python)"
returns:
  - "event tuples; items yields decoded values"
exceptions:
  - "IncompleteJSONError, JSONError"
defaults:
  - "declare backend"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "ijson.parse"
  - "ijson.items"
supporting_components:
  - "ijson.backends.python"
semantic_delta:
  - "Force python backend for portability"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted incremental JSON API.
```

## scope

```yaml
included:
  - "parse events, items for arrays/objects"
excluded:
  - "yajl C backend requirement"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "prefer pure python backend"
offline_resources: "BytesIO JSON"
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

- Staging path: `benchmark/staging/ijson__event_parse_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
