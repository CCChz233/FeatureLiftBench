# Task Design: marshmallow__schema_core__001

Status: oracle-verified

## Why This Task

Exercises schema graphs, nested fields, and decorator hooks central to Marshmallow.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Field types | `fields/__init__.py` | `test_load_dump_nested_schema` |
| Schema core | `schema.py` | `test_unknown_exclude_post_load_and_nested_errors` |
| Decorators | `decorators.py` | `test_unknown_exclude_post_load_and_nested_errors` |
