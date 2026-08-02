# Design card: parsimonious__grammar_visitor_core__001

**status:** `staging_validated`  
**wave:** W2  
**package:** `parsimonious`  
**repository_url:** https://github.com/erikrose/parsimonious  
**planned_lift_type:** Composite  
**final_lift_type:** Adapted  
**reclassification_reason:** Grammar + NodeVisitor is the documented upstream workflow; treat as Adapted unless task invents a new facade.  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Grammar parse + NodeVisitor evaluation  
**lift_review_flag:** Check whether Grammar+NodeVisitor is one documented workflow vs invented glue

> Skim pass + pin resolved. Materialize next; staging only (no promote).  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Grammar(rules: str)"
  - "featurelifted.Grammar.parse(text: str) -> Node"
  - "featurelifted.NodeVisitor.visit(node) / generic_visit"
  - "featurelifted.ParseError"
returns:
  - "Node tree; visitor returns evaluated values"
exceptions:
  - "ParseError"
  - "VisitationError if any"
defaults:
  - "declare"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "parsimonious.Grammar"
  - "parsimonious.NodeVisitor"
supporting_components:
  - "parsimonious.nodes.Node"
semantic_delta:
  - "Documented grammar+visitor pair as Adapted packaging"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted, not Composite, unless extra glue API added.
```

## scope

```yaml
included:
  - "PEG grammar parse, visitor evaluation"
excluded:
  - "left-recursion hacks beyond upstream"
```

## feasibility

```yaml
commit: "a33206834534df5bc1da341315c819f4312b8131"  # tag 0.10.0
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "strings only"
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

- Staging path: `benchmark/staging/parsimonious__grammar_visitor_core__001/`
- Skim pass @ 0.10.0 (`a33206834534…`).
- Do not promote to `benchmark/tasks/` in design_card phase.
