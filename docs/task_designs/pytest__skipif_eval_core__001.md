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

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Namespace merge | `markeval_namespace` merge in eval | `test_markeval_namespace_merged` |
| Obj globals | `obj_globals` merge in eval | `test_obj_globals_merged` |
| Syntax guard | compile/eval error path | `test_invalid_syntax_raises` |

## Agent Calibration

| Run | Model | Passed | Hidden failure |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | **failed** | namespace / globals merge |
