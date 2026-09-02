# Design card: pyparsing__grammar_compose_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `pyparsing`  
**repository_url:** https://github.com/pyparsing/pyparsing  
**planned_lift_type:** Composite  
**final_lift_type:** Adapted  
**reclassification_reason:** Composing ParserElements is the normal upstream API, not a novel multi-system surface. Planned Composite → Adapted.  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Compose ParserElements + parseString + named results  
**lift_review_flag:** none

**skim_status:** `pass` (2026-08-01)
**skim_notes:** Adapted OK (not Direct). Freeze helpers: Word, Literal, Keyword, Regex, Optional, ZeroOrMore, OneOrMore, Group, Suppress + parse_string + ParseResults + ParseException. No parse actions in tests.

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.Word / Literal / Keyword / Regex / Optional / ZeroOrMore / OneOrMore / Group / Suppress helpers used"
  - "featurelifted.ParserElement.parse_string(instring, parse_all: bool = False)"
  - "featurelifted.ParseResults accessors (as_list, as_dict, named results)"
  - "featurelifted.ParseException"
returns:
  - "ParseResults"
exceptions:
  - "ParseException with loc/msg"
defaults:
  - "parse_all=False"
state_effects:
  - "grammars may set parse actions \u2014 declare if used"
```

## upstream_mapping

```yaml
primary_symbols:
  - "pyparsing.ParserElement"
  - "pyparsing.core common helpers"
supporting_components:
  - "pyparsing.results.ParseResults"
semantic_delta:
  - "Task provides a sample composed grammar API surface rather than inventing a new engine"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Adapted extract of pyparsing composition+parse.
```

## scope

```yaml
included:
  - "build grammar from helpers, parse_string, named results, ParseException"
excluded:
  - "diagram generation, railroad, infixNotation full suite unless listed"
```

## feasibility

```yaml
commit: "fa24016d953353f8ba566abb5c8fc12e1d07556c"  # tag 3.3.2
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "string parse only"
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

- Staging path: `benchmark/staging/pyparsing__grammar_compose_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
