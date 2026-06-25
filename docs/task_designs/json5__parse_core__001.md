# Task Design: json5__parse_core__001

Status: oracle-verified

## Why This Task

Extract json5 loads parsing where recursive-descent parser state, scope stack, and lib.py value materialization are tightly coupled.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Parser state machine | `parser.py` | `test_loads_supports_line_comments` (public) |
| Value materialization | `lib.py` | `test_hex_and_plus_numeric_literals` |
| Package entry | `__init__.py` | `test_loads_parses_unquoted_keys_and_trailing_comma` (public) |
