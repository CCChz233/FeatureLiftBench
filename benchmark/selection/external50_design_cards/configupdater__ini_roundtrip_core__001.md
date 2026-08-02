# Design card: configupdater__ini_roundtrip_core__001

**status:** `design_card_ready`  
**wave:** W4  
**package:** `ConfigUpdater`  
**repository_url:** https://github.com/pyscaffold/configupdater  
**planned_lift_type:** Adapted  
**final_lift_type:** Adapted  
**reclassification_reason:** None  
**feature_family:** config_resolve_discover  
**entanglement:** config_environment_coupling  
**feature_one_liner:** INI round-trip update preserving comments  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.ConfigUpdater()"
  - "featurelifted.ConfigUpdater.read_string / read"
  - "section/option get set space-preserving API"
  - "featurelifted.ConfigUpdater.to_string()"
  - "UpdateError exceptions declare"
returns:
  - "updater; to_string INI text"
exceptions:
  - "NoConfigFileError / NoSectionError variants declare"
defaults:
  - "declare"
state_effects:
  - "mutable AST of INI"
```

## upstream_mapping

```yaml
primary_symbols:
  - "configupdater.ConfigUpdater"
supporting_components:
semantic_delta:
  - "Comment-preserving INI adapted from ConfigParser mental model"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Round-trip comments/spacing.
```

## scope

```yaml
included:
  - "read_string, modify values, to_string preserves comments"
excluded:
  - "interpolation beyond declared"
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

- Staging path: `benchmark/staging/configupdater__ini_roundtrip_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
