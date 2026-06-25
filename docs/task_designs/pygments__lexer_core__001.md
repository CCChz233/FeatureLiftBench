# Task Design: pygments__lexer_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/lexers/python.py` | `test_triple_quoted_string_and_operator_tokens` |
| Probe-2 | `featurelifted/unistring.py` | `test_string_and_comment_tokens_are_distinct` |
| Probe-3 | `featurelifted/regexopt.py` | `test_stripall_option_removes_whitespace_tokens` |
