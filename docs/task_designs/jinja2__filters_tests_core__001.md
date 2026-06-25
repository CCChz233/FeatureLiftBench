# Task Design: jinja2__filters_tests_core__001

Status: draft

## Why This Task

Filters/tests with module probes on filters.py and tests.py.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pallets/jinja` |
| Commit | `15206881c006c79667fe5154fe80c01c65410679` |
| License | BSD-3-Clause |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator |

## Output API

```python
from featurelifted import Environment
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Filters registry | `filters.py` | `test_default_filter_with_boolean` |
| Tests registry | `tests.py` | `test_defined_test_in_template` |
| Join filter | `filters.py` (`do_join`) | `test_filters_module_required_for_join` |
