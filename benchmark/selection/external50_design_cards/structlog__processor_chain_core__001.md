# Design card: structlog__processor_chain_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `structlog`  
**repository_url:** https://github.com/hynek/structlog  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** serialize_format_render  
**entanglement:** data_model_coupling  
**feature_one_liner:** BoundLogger + ordered processor chain + context binding  
**lift_review_flag:** none

**skim_status:** `pass` (2026-08-01)
**skim_notes:** Composite OK. Freeze processors: TimeStamper, add_log_level, KeyValueRenderer, JSONRenderer. Use PrintLogger/list capture + reset_defaults. No stdlib/twisted integrations.

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.configure(processors: list, wrapper_class=..., context_class=dict, logger_factory=..., cache_logger_on_first_use: bool = False)"
  - "featurelifted.get_logger(*args, **initial_values) -> BoundLogger"
  - "featurelifted.BoundLogger.bind/unbind/new(**values)"
  - "featurelifted.stdlib processors subset: KeyValueRenderer, JSONRenderer, TimeStamper, add_log_level (declare list)"
  - "featurelifted.reset_defaults()"
returns:
  - "log method calls run processor chain and emit via factory (capture with list logger)"
exceptions:
  - "DropEvent if used; TypeError on bad processors"
defaults:
  - "cache_logger_on_first_use False in tests"
state_effects:
  - "global configure state \u2014 tests must reset_defaults"
```

## upstream_mapping

```yaml
primary_symbols:
  - "structlog.configure"
  - "structlog.get_logger"
  - "structlog.BoundLoggerLazyProxy"
supporting_components:
  - "structlog.processors"
  - "structlog.stdlib"
semantic_delta:
  - "Contract is configure+processors+bound logger together"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Use MemoryLoggerFactory or list append factory for offline capture.
```

## scope

```yaml
included:
  - "bind context, processor ordering, JSON/KeyValue render, timestamp/level"
excluded:
  - "twisted/asyncio integrations, PrintLogger exotic configs"
```

## feasibility

```yaml
commit: "8174a86a2f14b5bd295eded733ff5fffc12aa173"  # tag 26.1.0
license: "MIT OR Apache-2.0"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "in-memory logger factory"
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

- Staging path: `benchmark/staging/structlog__processor_chain_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
