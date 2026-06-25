# Task Design: python_pathspec__gitignore_match__001

Status: oracle-verified

## Why This Task

Gitignore-style path matching and tree walks. Medium difficulty with strong hidden discriminator on Flash.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/cpburnz/python-pathspec` |
| Commit | pinned in metadata |
| License | MPL-2.0 |
| Difficulty | medium |

## Output API

```python
from featurelifted import PathSpec, GitIgnoreSpec
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Tree walk | `pathspec/util.py` or match_tree | `test_match_tree_files_returns_relative_paths` |
| Pattern normalization | path normalization helpers | `test_absolute_paths_and_custom_separators_are_normalized` |
| Pattern combine | `PathSpec.__add__` / pattern list | `test_ordering_equality_and_negated_match_files` |

## Agent Calibration

| Run | Model | Passed | Hidden failure |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | **failed** | `match_tree_files`, negated match ordering |
