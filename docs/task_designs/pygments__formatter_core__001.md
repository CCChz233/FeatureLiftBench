# Task Design: pygments__formatter_core__001

Status: oracle-verified

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/formatters/html.py` | `test_linenos_and_cssclass_options` |
| Probe-2 | `featurelifted/style.py` | `test_full_document_and_keyword_highlighting` |
| Probe-3 | `featurelifted/lexers/python.py` | `test_html_escapes_angle_brackets_in_source` |
