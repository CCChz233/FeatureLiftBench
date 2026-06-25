# Task Design: iniconfig__parse_config__001

Status: oracle-verified

## Why This Task

Easy pilot: single-package INI parser with clear API boundary and no third-party deps. Validates benchmark pipeline before hard tasks.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pytest-dev/iniconfig` |
| Commit | `77db208ab4ae0cd2061d909fe222a1db72867850` |
| License | MIT |
| Difficulty | easy |

## Output API

```python
from featurelifted import IniConfig, ParseError, iscommentline, COMMENTCHARS
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Core parser | `__init__.py` / parse loop | `test_multiline_values_and_file_order` |
| Comment stripping | inline-comment logic in parser | `test_parse_strips_inline_comments_by_default` |
| Error metadata | `ParseError` lineno/path | `test_duplicate_section_and_key_errors` |

## Manual Oracle Closure Plan

| Check | Result |
| --- | --- |
| Oracle `eval` | pass, `final_score≈1.0` |
| Copy-All | pass, `final_score≈0.2` |
| Oracle LOC | ~334 vs source ~667 |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | pass | ~0.47 |
