# Design card: textx__metamodel_model_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `textX`  
**repository_url:** https://github.com/textX/textX  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Metamodel from grammar + model parse  
**lift_review_flag:** none

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.metamodel_from_str(grammar: str, **kwargs) -> MetaModel"
  - "featurelifted.MetaModel.model_from_str(model_str: str)"
  - "object attribute access on model as grammar defines"
  - "textx exceptions TextXError / TextXSyntaxError"
returns:
  - "model object tree"
exceptions:
  - "TextXSyntaxError, TextXSemanticError"
defaults:
  - "declare"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "textx.metamodel_from_str"
supporting_components:
  - "textx.model"
  - "textx.exceptions"
semantic_delta:
  - "grammar metamodel + model parse"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Provide grammar string in tests.
```

## scope

```yaml
included:
  - "metamodel_from_str, model_from_str, basic RREL-free grammars"
excluded:
  - "textx-lang registration, generators, VS Code"
```

## feasibility

```yaml
commit: "ff7327de0b3d7ae81d52d867eb0cdcb643b56e93"  # tag v2.2.0
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "grammar+model strings"
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

- Staging path: `benchmark/staging/textx__metamodel_model_core__001/`
- Skim pass @ v2.2.0 (`ff7327de0b3d…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
