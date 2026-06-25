# Task Design: sqlparse__parse_format_core__001

Status: implemented as `tasks/sqlparse__parse_format_core__001/`. The first manual oracle passes evaluator with `functional_gate=1.0` and `ExtractionRatio=0.486`. A transformed Copy-All baseline also passes functionally but scores `ExtractionRatio=1.0`. mini-swe-agent baseline (deepseek-v4-pro, official API): **passed**, `extraction_ratio=0.487`, 45 steps, 855k tokens — see `outputs/mini-swe-agent/sqlparse-extreme-baseline-001/baseline-summary.md`.

## Why This Task

`sqlparse` is a good first hard-plus candidate because the target feature is not just a pure function. SQL parsing and formatting behavior is spread across tokenizer state, statement splitting, grouping rules, token tree data models, and formatter filters. This makes it a better fit for FeatureLiftBench than another small utility package, while still being smaller and easier to stabilize than a framework-heavy target such as `pytest` or `jinja2`.

The task should test whether an Agent can decouple a reusable SQL parse/format core without copying tests, documentation, release tooling, CLI glue, or unrelated project files.

## Source

| Field | Planned value |
| --- | --- |
| Source repo | `https://github.com/andialbrecht/sqlparse` |
| Commit | `f80af6a4007f11ada847218df8c29dc859238290` |
| License | BSD-3-Clause |
| Language | Python |
| Difficulty | Hard |
| Entanglement level | High |

## Entanglement

Planned `metadata.entanglement`:

```json
{
  "level": "high",
  "types": [
    "parser_state_coupling",
    "data_model_coupling",
    "implicit_dependency_coupling"
  ],
  "description": "SQL parse, split, and format behavior depends on tokenizer state, grouping passes, token tree classes, and formatter filters spread across multiple modules.",
  "signals": [
    "lexer and statement-splitting state",
    "grouped token tree data model",
    "formatter behavior composed from multiple filters",
    "public API hides a multi-module runtime closure"
  ]
}
```

## Target Feature

Extract the SQL parsing, statement splitting, token tree traversal, and core formatting API as a standalone package.

Planned source entrypoints:

- `sqlparse.parse`
- `sqlparse.parsestream`
- `sqlparse.split`
- `sqlparse.format`
- `sqlparse.sql.Token`
- `sqlparse.sql.TokenList`
- `sqlparse.sql.Statement`
- `sqlparse.sql.Identifier`
- `sqlparse.sql.IdentifierList`
- `sqlparse.tokens`

Planned output API:

```python
from featurelifted import parse, parsestream, split, format
from featurelifted.sql import Token, TokenList, Statement, Identifier, IdentifierList
from featurelifted import tokens
```

Primary callable:

```python
featurelifted.parse(sql: str, encoding: str | None = None) -> tuple[Statement, ...]
```

## Included Behaviors

- Parse one or more SQL statements into `Statement` objects.
- Split SQL scripts into statements while respecting strings, comments, parentheses, and semicolon placement.
- Preserve useful token tree behavior: `flatten()`, `get_type()`, token navigation, parent relationships, identifiers, and identifier lists.
- Format common SQL using options such as `keyword_case`, `identifier_case`, `strip_comments`, `reindent`, `indent_width`, and `use_space_around_operators`.
- Preserve original behavior for comments, whitespace, string literals, aliases, functions, nested expressions, CTEs, CASE expressions, and common DDL/DML statement types.
- Treat SQL as syntax/token structure, not as a validating SQL engine.

## Excluded Behaviors

- CLI entrypoint.
- Original project tests.
- Documentation, changelog, release scripts, CI config, type checking config, and packaging metadata from the original project.
- Dialect-perfect SQL validation.
- Network, database, browser, or external service behavior.
- Original `sqlparse` package import at runtime.

## Environment

Planned environment:

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

`requirements.lock` should be empty unless the pinned source snapshot introduces a required runtime dependency. The expected task should be pure Python.

## Public Tests

Public tests should communicate the task shape without revealing hard hidden edges:

- `parse("select * from users where id = 1")` returns one `Statement` whose `get_type()` is `SELECT`.
- `split()` handles two simple statements and ignores a trailing semicolon.
- `format()` supports `keyword_case="upper"` and basic `reindent=True`.
- token tree basics: `Statement.tokens`, `flatten()`, and simple identifier extraction.
- comments and quoted strings remain distinct from keywords.

## Hidden Tests

Hidden tests should force real decoupling rather than public-test hardcoding:

- Statement splitting with semicolons inside single quotes, double quotes, comments, nested parentheses, and function bodies where supported by the pinned behavior.
- CTEs, nested subqueries, CASE expressions, function calls, aliases, joins, and DDL.
- Formatter combinations: `strip_comments`, `keyword_case`, `identifier_case`, `reindent`, `indent_width`, `wrap_after`, and operator spacing.
- Token tree traversal: `token_next`, `token_prev`, `token_first`, `token_matching`, `within`, `has_ancestor`, `get_real_name`, `get_alias`, and identifier list iteration.
- Malformed or incomplete SQL should follow original tokenizer/parser behavior and should not become a validating SQL parser.
- No runtime import of `sqlparse`.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Statement splitter | `engine/statement_splitter.py` | `test_split_handles_comments_and_embedded_semicolons` |
| Token grouping | `engine/grouping.py` | `test_cte_aliases_and_identifier_helpers` |
| Formatter filters | `filters/reindent.py` | `test_formatter_comment_stripping_and_spacing` |

## Manual Oracle Closure Plan

Manual oracle status:

| Check | Result |
| --- | --- |
| Public tests | Passed |
| Hidden tests | Passed |
| Forbidden import check | Passed |
| Dependency count | 0 |
| Oracle LOC | 2930 |
| Source repo Python LOC | 6026 |
| ExtractionRatio | 0.486 |
| Copy-All-ish functional gate | 1.0 |
| Copy-All-ish ExtractionRatio | 1.0 |

Before treating this as a fully calibrated hard-plus task, still record:

- whether formatter support pulls in too much of the package for good discrimination;
- whether a narrower task should be split into `parse_split_core` and `format_core`;
- mini-swe-agent behavior and token/step cost.

Expected closure shape, to verify against the pinned repo:

```text
featurelifted/
  __init__.py
  sql.py
  tokens.py
  lexer.py
  keywords.py
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

If the oracle closure is more than roughly 75% of the source package runtime LOC, split the task into a smaller parser/split task first. If Copy-All and Oracle are still clearly separated because the repo contains substantial tests/docs/tooling, keeping parse+format together is acceptable.

## Initial Metadata Sketch

```json
{
  "task_id": "sqlparse__parse_format_core__001",
  "language": "python",
  "difficulty": "hard",
  "tags": ["parser", "formatter", "tokenizer", "pure-python", "multi-module"],
  "source": {
    "name": "sqlparse",
    "url": "https://github.com/andialbrecht/sqlparse",
    "commit": "<fixed-commit-hash>",
    "license": "<verify-from-snapshot>"
  },
  "feature": {
    "name": "SQL parse, split, and format core",
    "description": "Extract sqlparse's SQL statement parsing, splitting, token tree, and common formatting behavior as a standalone package.",
    "source_entrypoints": [
      "sqlparse.parse",
      "sqlparse.parsestream",
      "sqlparse.split",
      "sqlparse.format",
      "sqlparse.sql.Token",
      "sqlparse.sql.TokenList",
      "sqlparse.sql.Statement",
      "sqlparse.sql.Identifier",
      "sqlparse.sql.IdentifierList",
      "sqlparse.tokens"
    ],
    "included_behaviors": [
      "parse SQL text into Statement token trees",
      "split multi-statement SQL scripts while respecting strings, comments, and nesting",
      "support common token tree traversal and identifier helpers",
      "format common SQL with keyword case, identifier case, comment stripping, reindentation, indentation width, and operator spacing",
      "preserve original behavior for comments, whitespace, string literals, aliases, functions, nested expressions, CTEs, CASE expressions, and common DDL/DML"
    ],
    "excluded_behaviors": [
      "command line interface",
      "original project tests",
      "documentation and release tooling",
      "packaging metadata from the original project",
      "dialect-perfect SQL validation"
    ]
  }
}
```

## Remaining Go / No-Go Criteria

Keep the real task only if:

- the task adds coverage not already represented by `tomlkit`, `markdown_it`, or `pyyaml`.

If these criteria fail after baseline and Agent runs, use this design as a source for a narrower `sqlparse__statement_split_core__001` task.
