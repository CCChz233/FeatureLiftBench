# Task Design: jsonschema__validator_core__001

Status: oracle-verified

## Why This Task

Draft 2020-12 validator core with structured errors and optional format checking. **Too easy** on Flash (pass first try) — hidden needs strengthening over time.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/python-jsonschema/jsonschema` |
| Commit | `4.23.0-installed-snapshot` |
| License | MIT |
| Difficulty | hard |

## Output API

```python
from featurelifted import Draft202012Validator, validate, ValidationError, SchemaError, FormatChecker
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Keyword validators | `_keywords/` or validator dispatch | `test_nested_errors_paths_combinators_and_messages` |
| Format checker | format checker registry | `test_format_checker_schema_errors_and_additional_properties` |
| Schema meta-validation | `check_schema` path | `test_format_checker_schema_errors_and_additional_properties` (SchemaError) |

## Manual Oracle Closure Plan

Oracle passes public+hidden; Copy-All functional pass with high ExtractionRatio.

## Agent Calibration

| Run | Model | Passed | Notes |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | pass | hidden not blocking; consider more combinator edges |
