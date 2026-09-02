# Design card: boolean_py__expr_simplify_core__001

**status:** `design_card_ready`  
**wave:** W3  
**package:** `boolean.py`  
**repository_url:** https://github.com/bastikr/boolean.py  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** algorithm_data_structure  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Parse boolean expressions + algebra simplify  
**lift_review_flag:** none

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.BooleanAlgebra()"
  - "featurelifted.BooleanAlgebra.parse(expr: str)"
  - "expression .simplify() / .subs() as upstream"
  - "Symbol / AND / OR / NOT constructors if exposed"
returns:
  - "Expression objects; simplify returns expression"
exceptions:
  - "parse errors as upstream"
defaults:
  - "declare"
state_effects:
  - "algebra instance may hold symbols"
```

## upstream_mapping

```yaml
primary_symbols:
  - "boolean.BooleanAlgebra"
supporting_components:
  - "boolean.boolean Symbol/Expression classes"
semantic_delta:
  - "parse + algebraic simplify composition"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Composite parse+simplify.
```

## scope

```yaml
included:
  - "parse boolean expressions, simplify, equality"
excluded:
  - "SAT solvers"
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

- Staging path: `benchmark/staging/boolean_py__expr_simplify_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
