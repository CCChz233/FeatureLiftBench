# Task Design: jinja2__extensions_core__001

Status: oracle-verified

## Why This Task

Extract Jinja2 extension loading and Environment integration where parser tags, preprocessors, and priority ordering are framework-coupled.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pallets/jinja` |
| Commit | `15206881c006c79667fe5154fe80c01c65410679` |
| License | BSD-3-Clause |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, framework_coupling |

## Output API

```python
from featurelifted import Environment, Extension
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Extension base | `ext.py` (`Extension`) | `test_custom_extension_tag_renders` |
| Environment loader | `environment.py` (`load_extensions`) | `test_loopcontrols_extension_breaks_loop` (public) |
| Priority ordering | `ext.py` / `Environment.iter_extensions` | `test_extension_ordering_by_priority` |
