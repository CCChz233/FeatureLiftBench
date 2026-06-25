# Task Design: pytest__fixture_resolve_core__001

Status: oracle-verified

## Why This Task

Extract pytest fixture name closure resolution from `_pytest.fixtures` where registry lookup, nodeid scoping, and scope ordering are tightly coupled to the test framework.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pytest-dev/pytest` |
| Commit | `b55ab2aabb68c0ce94c3903139b062d0c2790152` |
| License | MIT |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator, framework_coupling |

## Output API

```python
from featurelifted import FixtureDef, FixtureRegistry, deduplicate_names, fixture, getfixturemarker, resolve_fixture_closure
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Closure expansion | `fixture_resolve.py` (`resolve_fixture_closure`) | `test_closure_sorted_by_scope_descending` |
| Deduplication | `fixture_resolve.py` (`deduplicate_names`) | `test_deduplicate_names_keeps_first_occurrence_order` |
| Lookup errors | `fixture_resolve.py` (`FixtureLookupError`) | `test_fixture_lookup_error_lists_available` |
