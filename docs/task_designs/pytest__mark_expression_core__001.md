# Task Design: pytest__mark_expression_core__001

Status: draft

## Why This Task

Standalone -m expression evaluator from _pytest/mark/expression.py.

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
from featurelifted import Expression, ParseError
from featurelifted import expression
from featurelifted.expression import Scanner, TokenType
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Expression compile/eval | `Expression` / compile path | `test_kwargs_matcher` |
| Scanner | `expression.py` (`Scanner`) | `test_expression_module_scanner` |
| Parser grammar | expression parse module | `test_kwargs_matcher` |

## Agent Calibration

| Run | Model | Passed | Hidden failure |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | **failed** | hidden collect ERROR (missing `expression` submodule) |
