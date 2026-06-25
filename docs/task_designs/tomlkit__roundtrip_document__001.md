# Task Design: tomlkit__roundtrip_document__001

Status: oracle-verified

## Why This Task

Format-preserving TOML parse/edit/dump; hard parser + document item model task from early pilot.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/python-poetry/tomlkit` |
| Commit | `9ac3f98214dbfbca0157b6c370c7986f497c34e4` |
| License | MIT |
| Difficulty | hard |

## Output API

```python
from featurelifted import parse, loads, dumps, document, table, inline_table, array, aot, string, item
from featurelifted.exceptions import ParseError, UnexpectedCharError, InvalidUnicodeValueError
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Parser | `parser.py` | `test_dotted_keys_table_redefinition_and_unicode_errors` |
| AoT / items | `items.py` array/table constructors | `test_arrays_of_tables_and_inline_tables_dump_correctly` |
| String formatting | string item dump | `test_string_constructor_and_sorted_dump_preserve_expected_format` |

## Manual Oracle Closure Plan

Oracle pass `final_score=1.0`; Copy-All pass `final_score≈0.2`; oracle LOC ~4528 vs copy-all ~7580.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | pass | ~0.60 |
