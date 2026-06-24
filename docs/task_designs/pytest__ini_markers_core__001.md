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
