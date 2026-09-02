# Design card: python_json_logger__json_formatter_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `python-json-logger`  
**repository_url:** https://github.com/nhairs/python-json-logger  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** config_environment_coupling  
**feature_one_liner:** JsonFormatter field rename/reshape API  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.JsonFormatter(fmt=None, datefmt=None, style='%', rename_fields: dict | None = None, static_fields: dict | None = None, ...)"
  - "featurelifted.JsonFormatter.format(record: logging.LogRecord) -> str"
returns:
  - "JSON line string"
exceptions:
  - "declare"
defaults:
  - "style='%'; rename_fields None"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "pythonjsonlogger.json.JsonFormatter or pythonjsonlogger.jsonlogger.JsonFormatter (pin import path)"
supporting_components:
  - "logging.LogRecord"
semantic_delta:
  - "Document exact import path for v3 package layout"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted formatter options.
```

## scope

```yaml
included:
  - "format LogRecord to JSON, rename_fields, static_fields"
excluded:
  - "SocketHandler networking"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "BSD-2-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "LogRecord manufactured in tests"
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

- Staging path: `benchmark/staging/python_json_logger__json_formatter_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
