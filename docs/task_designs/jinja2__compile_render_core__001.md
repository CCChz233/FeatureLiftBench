# Task Design: jinja2__compile_render_core__001

Status: draft

## Why This Task

Compile/render without loaders. Probes target compiler and runtime modules.

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
from featurelifted import Environment
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Compiler | `compiler.py` | `test_compiler_module_required_for_set_block` |
| Runtime context | `runtime.py` | `test_runtime_context_exported_vars` |
| Macros | `compiler.py` / macro emit | `test_macro_render_and_caller` |
