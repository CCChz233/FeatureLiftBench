# Task Design: `python_dotenv__env_parse_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

`.env` parsing is a common bootstrap need decoupled from full python-dotenv (CLI, IPython, load_dotenv side effects). The upstream library couples a regex-driven parser, quote escape tables, POSIX variable expansion, and atomic file rewrite for `set_key`. Hidden tests stress escape semantics, BOM handling, interpolation order, and quoting rules that naive split-based parsers miss.

## Practical reuse（必填）

1. **Reuse module** — A standalone environment-file parser and key writer for config bootstrap in services and test fixtures.
2. **Who imports it** — Teams vendoring dotenv parsing into frameworks, deployment tools, or secret loaders without the `python-dotenv` PyPI dependency.
3. **Why not copy-all** — Upstream bundles CLI, IPython extension, and test harness; compact closure keeps parse + set_key core only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/theskumar/python-dotenv |
| Commit | `751f8c148222e58aa173c83c4e5e6cfccb2cc124` |
| License | BSD-3-Clause |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, config_environment_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["config_environment_coupling", "parser_state_coupling", "implicit_dependency_coupling"],
  "primary": "config_environment_coupling",
  "description": "Dotenv parsing couples regex lexer state, quote escapes, ordered variable resolution, and atomic file rewrite."
}
```

## Target Feature

### Source entrypoints

- `dotenv.dotenv_values`
- `dotenv.set_key`
- `dotenv.parser.parse_stream`
- `dotenv.variables.parse_variables`

### Output API

```python
from featurelifted import dotenv_values, set_key, get_key
```

## Included Behaviors

- Parse key=value with export prefix, comments, quoted values
- Double/single quote escape sequences
- UTF-8 BOM stripping
- `${VAR}` and `${VAR:-default}` interpolation
- `set_key` create/update with auto-quoting

## Excluded Behaviors

- CLI (`cli.py`), IPython extension
- `load_dotenv` os.environ mutation in hidden tests
- Original `dotenv` import at runtime

## Public Tests

- Simple pairs, quoted values, export prefix
- `set_key` create and update

## Hidden Tests

- Double-quote `\n` escape vs single-quote literal backslash-n
- UTF-8 BOM strip
- Inline comment after whitespace
- Key without `=` → `None`
- Variable interpolation chain and `${VAR:-default}`
- `set_key` quoting and append without trailing newline
- No `dotenv` import surface

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/parser.py` | `test_double_quote_escape_sequences` |
| Probe-2 | `featurelifted/variables.py` | `test_variable_default_when_missing` |
| Probe-3 | `featurelifted/main.py` | `test_set_key_quotes_special_characters` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.237** |
| Copy-All ExtractionRatio | > oracle + margin | **0.890** (Δ=0.653) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  parser.py
  variables.py
  main.py
```

## Go / No-Go Criteria

- Practical reuse narrative holds for config bootstrap.
- Oracle passes public + hidden; naive fails hidden on escape/interpolation/quoting.
- ≥3 module probes verified after Step 5.
- Copy-all extraction clearly above oracle.
