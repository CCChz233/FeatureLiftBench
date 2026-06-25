# Task Design: sqlparse__token_tree_core__001

Status: oracle-verified

## Why This Task

Focus on SQL token tree navigation and identifier helpers without requiring split or format behavior. Tests whether agents can decouple the grouped token data model and traversal APIs from the broader sqlparse package.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/andialbrecht/sqlparse` |
| Commit | `f80af6a4007f11ada847218df8c29dc859238290` |
| License | BSD-3-Clause |
| Language | Python |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "data_model_coupling", "implicit_dependency_coupling"],
  "description": "Token tree navigation depends on grouping passes, token tree classes, and identifier helpers spread across multiple modules.",
  "signals": ["grouped token tree data model", "identifier and comparison navigation helpers"]
}
```

## Target Feature

### Source entrypoints

- `sqlparse.parse`
- `sqlparse.parsestream`
- `sqlparse.sql.*`
- `sqlparse.tokens`

### Output API

```python
from featurelifted import parse, parsestream
from featurelifted import sql, tokens
```

Primary callable:

```python
featurelifted.parse(sql: str, encoding: str | None = None) -> tuple[Statement, ...]
```

## Included Behaviors

- Parse SQL into Statement token trees.
- Token tree traversal: flatten, get_type, token navigation, parent/ancestor relationships.
- Identifier helpers: get_name, get_real_name, get_alias, CTE structure.

## Excluded Behaviors

- Multi-statement script splitting.
- SQL formatting and formatter filters.
- CLI, original tests, docs, CI, packaging metadata.
- Original package import at runtime.

## Environment

```json
{
  "python": "3.11",
  "network": false,
  "timeout_seconds": 60,
  "dependency_lock": "requirements.lock",
  "allowed_dependencies": [],
  "forbidden_dependencies": ["sqlparse"],
  "forbidden_imports": ["sqlparse"]
}
```

## Public Tests

- Basic parse returns SELECT statement with expected flattened tokens.
- Token tree basics: tokens list and flatten traversal.

## Hidden Tests

- CTE aliases and identifier helper extraction.
- Token navigation and ancestor relationships in WHERE clauses.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Grouping | `engine/grouping.py` | `test_cte_aliases_and_identifier_helpers` |
| SQL data model | `sql.py` | `test_token_navigation_and_ancestor_relationships` |
| Lexer tokens | `lexer.py` | `test_token_navigation_and_ancestor_relationships` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| Forbidden import check | pass | |
| ExtractionRatio | 0.25–0.55 | |

Expected closure shape:

```text
featurelifted/
  __init__.py
  sql.py
  tokens.py
  lexer.py
  keywords.py
  exceptions.py
  utils.py
  engine/
    grouping.py
    statement_splitter.py
```

## Go / No-Go Criteria

- Oracle and Copy-All are clearly separated on ExtractionRatio.
- Hidden tests force real decoupling of token tree navigation, not public-test hardcoding.
