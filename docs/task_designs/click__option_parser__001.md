# Task Design: click__option_parser__001

Status: oracle-verified

## Why This Task

Extract Click command/option/argument parsing and CliRunner invocation without shell completion or terminal styling integrations. Flash baseline fails on **forbidden import** while public+hidden pass — tests are correct; gate is the discriminator.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/pallets/click` |
| Commit | `8.1.7-installed-snapshot` |
| License | BSD-3-Clause |
| Difficulty | hard |
| Tags | functional-discriminator, decoupling-discriminator |

## Output API

```python
import featurelifted as click
from featurelifted.testing import CliRunner
```

## Hidden Tests

- Nested groups, `pass_context`, `IntRange`, flag pairs.
- Prompts, usage errors, `CliRunner.isolated_filesystem`.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Parameter types | `types.py` (`Choice`, `IntRange`) | `test_group_context_flags_range_and_defaults` |
| Context stack | `globals.py` (`pass_context`, `Context`) | `test_group_context_flags_range_and_defaults` |
| CliRunner | `testing.py` | `test_usage_errors_prompts_and_isolated_filesystem` |

## Manual Oracle Closure Plan

| Check | Target |
| --- | --- |
| Public + hidden tests | pass |
| Forbidden import check | pass |
| Copy-All ExtractionRatio | ≥ 0.95 |
| Oracle ExtractionRatio | ~0.15–0.45 |

## Agent Calibration

| Run | Model | Passed | Notes |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | **failed** | public+hidden pass; 7× forbidden `import click` |
