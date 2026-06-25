# Task Design: coverage__glob_matcher_core__001

Status: oracle-verified

## Why This Task

Orthogonal coverage.py sub-problem: glob preparation and matching shared by include/omit/report filters but separable from config merge, source selection, and path remap.

## Output API

```python
from featurelifted import GlobMatcher, prep_patterns, globs_to_regex
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Regex join helper | `misc.py` (`join_regex`) | `test_glob_matcher_many_patterns` |
| Glob tokenizer | `files.py` (`_glob_to_regex`) | `test_glob_matcher_backslash_pattern` |
| Windows paths | `files.py` (`GlobMatcher.match`) | `test_glob_matcher_respects_windows_style_paths` |

## Manual Oracle Closure Plan

Expected closure: `env.py`, `exceptions.py`, `types.py`, `misc.py`, `files.py`.
