# Task Design: rich__markup_parse_core__001

Status: oracle-verified

## Why This Task

Isolates console markup stack semantics without terminal Console rendering.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Markup parser | `markup.py` | `test_nested_styles_and_implicit_close` |
| Text spans | `text.py` | `test_meta_link_handler_and_repr` |
| Style normalization | `style.py` | `test_render_escape_and_from_markup` |
