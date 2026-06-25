# Task Design: lark__grammar_loader_core__001

Status: oracle-verified

## Why This Task

Forces extraction of grammar import resolution and packaged `grammars/common.lark` resources.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Grammar loader | `load_grammar.py` | `test_open_from_package_and_import_graph` |
| Packaged grammars | `grammars/common.lark` | `test_packaged_common_grammar_import` |
| Parser frontend | `parser_frontends.py` | `test_open_relative_import_and_common_import` |
