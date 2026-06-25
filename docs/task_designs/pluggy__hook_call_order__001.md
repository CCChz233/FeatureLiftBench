# Task Design: pluggy__hook_call_order__001

Status: oracle-verified

## Why This Task

Plugin manager hook ordering, firstresult, hookwrapper, and validation. Flash passes with **extraction_ratio≈0.88** — only 3 pytest cases; hidden does not prevent copy-all.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pytest-dev/pluggy` |
| Commit | `1.0.0-installed-snapshot` |
| License | MIT |
| Difficulty | hard |

## Output API

```python
from featurelifted import PluginManager, HookspecMarker, HookimplMarker, PluginValidationError
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Hook caller | `_hooks.py` / call ordering | `test_firstresult_and_hookwrapper_result_mutation` |
| Hookwrapper | wrapper yield path | `test_firstresult_and_hookwrapper_result_mutation` |
| Plugin validation | `_manager.py` validation | `test_validation_unregister_and_plugin_names` |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | Notes |
| --- | --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | pass | ~0.88 | consider extra hidden for copy-all footprint |
