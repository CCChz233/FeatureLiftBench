# Task Design: coverage__source_selection_core__001

Status: oracle-verified

## Why This Task

Exercises InOrOut include/omit/source policy—the core file-selection gate for coverage measurement—without data collection or reporting.

## Output API

```python
from featurelifted import SourceSelector

selector = SourceSelector(source=[...], run_omit=[...])
selector.skip_reason(filename, modulename=None)
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Matchers | `files.py` (`GlobMatcher`) | `test_source_selector_include_without_source` |
| Policy core | `inorout.py` (`check_include_omit_etc`) | `test_source_selector_package_name` |
| Encoding guard | `inorout.py` / disposition | `test_source_selector_rejects_non_utf8_filename` |

## Manual Oracle Closure Plan

Expected closure: `env.py`, `exceptions.py`, `types.py`, `misc.py`, `files.py`, `config.py`, `disposition.py`, `inorout.py`, minimal `python.py`.
