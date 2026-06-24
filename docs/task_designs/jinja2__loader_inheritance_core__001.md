# Task Design: jinja2__loader_inheritance_core__001

Status: draft

## Why This Task

Loader + extends with bundled DictLoader fixtures. Probes loaders module.

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
from featurelifted import Environment, DictLoader
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| core module | see hidden tests | see hidden tests |
