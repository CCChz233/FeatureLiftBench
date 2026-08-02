# Design card: tinycss2__stylesheet_roundtrip_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `tinycss2`  
**repository_url:** https://github.com/Kozea/tinycss2  
**planned_lift_type:** Composite  
**final_lift_type:** Adapted  
**reclassification_reason:** parse_stylesheet + serialize are paired upstream entrypoints. Planned Composite → Adapted.  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Parse stylesheet tokens + serialize back  
**lift_review_flag:** none

**skim_status:** `pass` (2026-08-01)
**skim_notes:** Adapted OK. Freeze Required API to parse_stylesheet + serialize + QualifiedRule/AtRule/ParseError. Drop parse_rule_list/parse_component_value_list from required.

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.parse_stylesheet(css: str, skip_comments: bool = False, skip_whitespace: bool = False) -> list"
  - "featurelifted.parse_rule_list(...)"
  - "featurelifted.parse_component_value_list(...)"
  - "featurelifted.serialize(nodes) -> str"
  - "node types: QualifiedRule, AtRule, ParseError \u2014 declare tested ones"
returns:
  - "list of nodes; serialize returns CSS string"
exceptions:
  - "nodes can be ParseError objects rather than raising \u2014 document"
defaults:
  - "skip_comments/skip_whitespace False"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "tinycss2.parse_stylesheet"
  - "tinycss2.serialize"
supporting_components:
  - "tinycss2.ast"
semantic_delta:
  - "Round-trip contract explicitly in TASK"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted parse/serialize pair.
```

## scope

```yaml
included:
  - "stylesheet parse, serialize roundtrip, selected at-rules"
excluded:
  - "full CSSOM, browser layout"
```

## feasibility

```yaml
commit: "f295a49711a4d348664bba7fb34113b3b4b78cb2"  # tag v1.5.1
license: "BSD-3-Clause"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "CSS strings only"
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

- Staging path: `benchmark/staging/tinycss2__stylesheet_roundtrip_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
