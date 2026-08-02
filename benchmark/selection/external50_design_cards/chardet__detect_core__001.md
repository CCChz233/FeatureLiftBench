# Design card: chardet__detect_core__001

**status:** `design_card_ready`  
**wave:** W5  
**package:** `chardet`  
**repository_url:** https://github.com/chardet/chardet  
**planned_lift_type:** Direct  
**final_lift_type:** Direct  
**reclassification_reason:** None  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** chardet.detect encoding detection  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.detect(byte_str: bytes) -> dict encoding/confidence/language"
returns:
  - "dict with encoding, confidence"
exceptions:
  - "declare empty input behavior"
defaults:
  - "none"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "chardet.detect"
supporting_components:
  - "chardet.universaldetector optional excluded"
semantic_delta:
  - "Direct"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Fixture byte samples.
```

## scope

```yaml
included:
  - "detect on provided fixtures"
excluded:
  - "cli chardetect"
```

## feasibility

```yaml
commit: null  # resolve at pin/materialize
license: "LGPL-2.1"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "bytes fixtures"
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

- Staging path: `benchmark/staging/chardet__detect_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
