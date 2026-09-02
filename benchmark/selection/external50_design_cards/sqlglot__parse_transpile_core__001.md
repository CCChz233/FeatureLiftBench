# Design card: sqlglot__parse_transpile_core__001

**status:** `validated_staging`  
**wave:** W1  
**package:** `sqlglot`  
**repository_url:** https://github.com/tobymao/sqlglot  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** parse_tokenize_decode  
**entanglement:** parser_state_coupling  
**feature_one_liner:** Parse SQL + transpile dialect + optimize expression tree  
**lift_review_flag:** none

**skim_status:** `pass-with-care` (2026-08-01)
**skim_notes:** Composite OK but large. Freeze dialects: sqlite, postgres, mysql. API: parse_one/parse/transpile/Expression.sql + ParseError. No optimizer/DB execute.

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.parse_one(sql: str, read: str | None = None) -> Expression"
  - "featurelifted.parse(sql: str, read: str | None = None) -> list[Expression]"
  - "featurelifted.transpile(sql: str, read: str | None = None, write: str | None = None, pretty: bool = False) -> list[str]"
  - "featurelifted.Expression.sql(dialect: str | None = None, pretty: bool = False) -> str"
  - "featurelifted.exp node types used in tests must be listed (Select, Column, ...)"
  - "featurelifted.errors.ParseError"
returns:
  - "Expression trees; transpile returns SQL strings"
exceptions:
  - "ParseError on invalid SQL"
defaults:
  - "pretty=False"
state_effects:
  - "none"
```

## upstream_mapping

```yaml
primary_symbols:
  - "sqlglot.parse_one"
  - "sqlglot.transpile"
supporting_components:
  - "sqlglot.expressions"
  - "sqlglot.dialects"
  - "sqlglot.optimizer (only if included)"
semantic_delta:
  - "Parse + transpile (+ optional optimize if in scope) as pipeline; freeze dialect names"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Large repo — keep dialect subset small (e.g. sqlite/postgres/mysql).
```

## scope

```yaml
included:
  - "parse_one/parse, transpile across declared dialects, Expression.sql"
excluded:
  - "execute against DB, full optimizer suite unless explicitly listed"
```

## feasibility

```yaml
commit: "29c651b85309693924b8c034501e6a2733d14588"  # tag v30.14.0
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "SQL string transforms only"
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

- Staging path: `benchmark/staging/sqlglot__parse_transpile_core__001/`
- Do not materialize until human skim of target_api + lift (esp. reclassified cards).
- Do not promote to `benchmark/tasks/` in design_card phase.
