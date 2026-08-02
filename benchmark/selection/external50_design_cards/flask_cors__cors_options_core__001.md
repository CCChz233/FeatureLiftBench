# Design card: flask_cors__cors_options_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `flask-cors`  
**repository_url:** https://github.com/corydolphin/flask-cors  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** registry_plugin_dispatch  
**entanglement:** framework_coupling  
**feature_one_liner:** CORS options object / after-request decoration API  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.CORS(app=None, **options)"
  - "featurelifted.cross_origin(**options) decorator"
  - "options: origins, methods, allow_headers, supports_credentials \u2014 declare"
returns:
  - "decorated view; CORS installs after_request"
exceptions:
  - "declare"
defaults:
  - "origins='*' unless tightened"
state_effects:
  - "mutates Flask app hooks"
```

## upstream_mapping

```yaml
primary_symbols:
  - "flask_cors.CORS"
  - "flask_cors.cross_origin"
supporting_components:
  - "flask_cors.core"
semantic_delta:
  - "Options object/decorator adapted API; Flask test client"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Needs Flask.
```

## scope

```yaml
included:
  - "attach CORS, verify ACAO headers on test client responses"
excluded:
  - "real browsers"
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
offline_resources: "Flask test client"
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

- Staging path: `benchmark/staging/flask_cors__cors_options_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
