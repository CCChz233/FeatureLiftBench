# Task Design: markdown_it__commonmark_render__001

Status: oracle-verified

## Why This Task

CommonMark parse/render core. Flash passes with **extraction_ratio≈0.93** (copy-heavy) — functional tests OK but decoupling discriminator weak.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/executablebooks/markdown-it-py` |
| Commit | pinned in metadata |
| License | MIT |
| Difficulty | hard |

## Output API

```python
from featurelifted import MarkdownIt
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Block rules | `rules_block/` | `test_nested_blocks_code_escaping_and_images` |
| Inline/render | `renderer.py` or inline rules | `test_nested_blocks_code_escaping_and_images` |
| Rule enable/disable | parser rule registry | `test_fence_rule_disable_and_link_attributes` |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | Notes |
| --- | --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | pass | ~0.93 | add hidden edges or tighten scoring narrative |
