# Task Design: packaging__requirement_marker_specifier__001

Status: oracle-verified

## Why This Task

PEP 440/508 version, specifier, requirement, and marker semantics in one hard parser/data-model task.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pypa/packaging` |
| Commit | `24.1-installed-snapshot` |
| License | Apache-2.0 OR BSD-2-Clause |
| Difficulty | hard |

## Output API

```python
from featurelifted import Version, Specifier, SpecifierSet, Requirement, Marker, default_environment
from featurelifted import InvalidVersion, InvalidSpecifier, InvalidRequirement, InvalidMarker
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Version parser | `version.py` | `test_version_normalization_ordering_and_invalid_inputs` |
| Specifier engine | `specifiers.py` | `test_specifier_prerelease_wildcard_compatible_and_filtering` |
| Marker evaluator | `markers.py` | `test_marker_boolean_logic_default_environment_and_errors` |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | pass | ~0.58 |
