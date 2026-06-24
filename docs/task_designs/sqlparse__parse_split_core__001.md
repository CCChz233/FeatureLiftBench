# Task Design: sqlparse__parse_split_core__001

Status: oracle-verified

## Why This Task

Narrow sqlparse extraction to parse and split only. Shares the pinned commit with other sqlparse Extreme tasks but exposes a smaller output API, forcing agents to decouple statement splitting without pulling in formatter filters.

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
  "description": "SQL parse and split behavior depends on tokenizer state, statement-splitting passes, and grouping rules spread across multiple modules.",
  "signals": ["lexer and statement-splitting state", "grouped token tree data model for split boundaries"]
}
```

## Target Feature

### Source entrypoints

- `sqlparse.parse`
- `sqlparse.parsestream`
- `sqlparse.split`

### Output API

```python
from featurelifted import parse, parsestream, split
```

Primary callable:

```python
featurelifted.parse(sql: str, encoding: str | None = None) -> tuple[Statement, ...]
```

## Included Behaviors

- Parse SQL text into Statement token trees.
- Split multi-statement scripts while respecting strings, comments, and nesting.

## Excluded Behaviors

- SQL formatting and formatter filters.
- Token tree navigation helpers beyond basic parse output.
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
- Split respects semicolons inside quoted strings.

## Hidden Tests

- Split handles comments and embedded semicolons in strings.
- Parse returns multiple statements from a script.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Statement splitter | `engine/statement_splitter.py` | `test_split_handles_comments_and_embedded_semicolons` |
| Grouping | `engine/grouping.py` | `test_parse_multiple_statements` |

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
- Adds discrimination not covered by the combined parse+format flagship task.
