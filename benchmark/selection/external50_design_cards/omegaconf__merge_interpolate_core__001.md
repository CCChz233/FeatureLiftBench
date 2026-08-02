# Design card: omegaconf__merge_interpolate_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `omegaconf`  
**repository_url:** https://github.com/omry/omegaconf  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** config_resolve_discover  
**entanglement:** config_environment_coupling  
**feature_one_liner:** DictConfig merge + interpolation + struct-mode resolution  
**lift_review_flag:** none

**skim_status:** `pass` (2026-08-01)
**skim_notes:** Composite OK. Freeze: OmegaConf.create/merge/to_container/select/resolve + is_missing/is_null/is_config. Exceptions: InterpolationResolutionError, ConfigKeyError. No dataclass structured configs / custom resolvers.

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.OmegaConf.create(obj: dict | list | str | None = None) -> DictConfig | ListConfig"
  - "featurelifted.OmegaConf.merge(*configs) -> DictConfig"
  - "featurelifted.OmegaConf.to_container(cfg, resolve: bool = False) -> Any"
  - "featurelifted.OmegaConf.select(cfg, key: str, default: Any = None) -> Any"
  - "featurelifted.OmegaConf.is_missing / is_null / is_config helpers (declared subset)"
  - "interpolation: ${...} resolution via resolve=True or OmegaConf.resolve(cfg)"
returns:
  - "DictConfig/ListConfig; to_container returns plain dict/list"
exceptions:
  - "omegaconf.errors.* subset: InterpolationResolutionError, ConfigKeyError, ValidationError \u2014 list exact names in TASK"
defaults:
  - "struct mode off unless set_struct; resolve default False on to_container"
state_effects:
  - "configs are mutable nodes; merge returns new tree"
```

## upstream_mapping

```yaml
primary_symbols:
  - "omegaconf.OmegaConf"
  - "omegaconf.DictConfig"
supporting_components:
  - "omegaconf.resolvers"
  - "omegaconf.errors"
semantic_delta:
  - "Compose create/merge/interpolate/select as one extraction contract"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Merge + interpolation + struct flags are distinct capabilities.
```

## scope

```yaml
included:
  - "dict/list config, merge, dot-select, interpolations, to_container"
excluded:
  - "CLI flags, dataclass structured configs beyond declared subset, custom resolvers registration unless listed"
```

## feasibility

```yaml
commit: "350bdb632865c5dd2286f2f6521acefe4abd843d"  # tag v2.3.0
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "in-memory configs only"
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

- Staging path: `benchmark/staging/omegaconf__merge_interpolate_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
