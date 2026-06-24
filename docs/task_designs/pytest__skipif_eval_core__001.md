# Task Design: pytest__skipif_eval_core__001

Status: draft

## Why This Task

evaluate_condition subset from skipping.py with EvalContext/Mark adapters.

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
from featurelifted import Mark, EvalContext, evaluate_condition
```
