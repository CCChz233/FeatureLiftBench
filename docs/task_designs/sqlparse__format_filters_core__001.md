# Task Design: sqlparse__format_filters_core__001

Status: oracle-verified

## Why This Task

Isolate SQL formatting behavior composed from filter-stack modules. Shares the pinned sqlparse commit but exposes only `format`, testing whether agents can decouple formatter filters without copying parse/split/token-tree APIs.

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
  "description": "SQL formatting behavior depends on tokenizer state, filter-stack composition, and formatter filters spread across multiple modules.",
  "signals": ["formatter behavior composed from multiple filters", "filter stack postprocessing and serialization"]
}
```

## Target Feature

### Source entrypoints

- `sqlparse.format`

### Output API

```python
from featurelifted import format
```

Primary callable:

```python
featurelifted.format(sql: str, encoding: str | None = None, **options) -> str
```

## Included Behaviors

- Format SQL with keyword case, reindent, operator spacing, and comment stripping.
- Validate formatter options and reject invalid values.

## Excluded Behaviors

- SQL parsing into navigable token trees.
- Multi-statement script splitting.
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

- Format supports keyword_case, reindent, and operator spacing.

## Hidden Tests

- Comment stripping and operator spacing combinations.
- Invalid formatter options raise SQLParseError.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Reindent filter | `filters/reindent.py` | `test_formatter_comment_stripping_and_spacing` |
| Formatter validation | `formatter.py` | `test_formatter_rejects_invalid_options` |
| Filter stack | `engine/filter_stack.py` | `test_formatter_comment_stripping_and_spacing` |

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
  formatter.py
  exceptions.py
  utils.py
  engine/
    filter_stack.py
    grouping.py
    statement_splitter.py
  filters/
    ...
```

## Go / No-Go Criteria

- Oracle and Copy-All are clearly separated on ExtractionRatio.
- Narrower than the combined parse+format flagship; formatter closure still spans multiple filter modules.
