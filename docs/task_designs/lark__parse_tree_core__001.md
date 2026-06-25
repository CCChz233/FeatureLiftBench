# Task Design: lark__parse_tree_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/parsers/lalr_parser.py` | `test_nested_lists_and_tokens` |
| Probe-2 | `featurelifted/load_grammar.py` | `test_named_terminal_and_pretty_output` |
| Probe-3 | `featurelifted/lexer.py` | `test_unexpected_characters_on_garbage_input` |
