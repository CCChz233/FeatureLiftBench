# Task Design: jinja2__lexer_parser_core__001

Status: draft

## Why This Task

Narrow jinja2 extraction to lex+parse AST. Module probes target lexer and parser.

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
from featurelifted import Environment, nodes
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Lexer | `lexer.py` | `test_lexer_module_required_for_raw_blocks` |
| Parser | `parser.py` | `test_parser_module_required_for_if_elif` |
| AST nodes | `nodes.py` | `test_parse_for_loop_structure` |
