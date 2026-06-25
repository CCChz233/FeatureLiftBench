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
| Loader cache | `loaders.py` | `test_loader_module_required_for_missing_template` |
| BaseLoader API | `loaders.py` (`BaseLoader`) | `test_base_loader_subclass_get_source` |
| Inheritance compile | compiler block resolution | `test_multi_level_inheritance` |
