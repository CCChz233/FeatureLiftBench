# Task Design: pytest__ini_markers_core__001

Status: draft

## Why This Task

Ini markers linelist parsing subset from pytest config/mark modules.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pytest-dev/pytest` |
| Commit | `b55ab2aabb68c0ce94c3903139b062d0c2790152` |
| License | MIT |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, functional-discriminator |

## Output API

```python
from featurelifted import MarkerRegistry, parse_linelist, split_marker_line
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Linelist parser | linelist parse helper | `test_linelist_strips_blank_lines` |
| Marker line split | `split_marker_line` whitespace rules | `test_split_marker_line_whitespace` |
| Registry ordering | `MarkerRegistry.from_ini` | `test_registry_module_order_preserved` |

## Agent Calibration

| Run | Model | Passed | Hidden failure |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | **failed** | `test_split_marker_line_whitespace` |
