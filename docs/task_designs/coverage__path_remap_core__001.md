# Task Design: coverage__path_remap_core__001

Status: oracle-verified

## Why This Task

Isolates combine-time PathAliases remapping used when merging coverage data from different checkout roots.

## Output API

```python
from featurelifted import PathAliases
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Alias map | `files.py` (`PathAliases.map`) | `test_path_aliases_multiple_rules` |
| Glob partial match | `files.py` (`globs_to_regex`) | `test_path_aliases_relative_pattern` |
| Wildcard validation | `files.py` (`PathAliases.add`) | `test_path_aliases_rejects_trailing_wildcards` |

## Manual Oracle Closure Plan

Expected closure: `env.py`, `exceptions.py`, `types.py`, `misc.py`, `files.py`.
