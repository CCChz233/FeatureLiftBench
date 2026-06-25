# Task Design: python_slugify__slugify_core__001

Status: oracle-verified

## Why This Task

Medium pilot with allowed `text-unidecode` dependency; unicode, replacements, and truncation edges.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/un33k/python-slugify` |
| Commit | pinned in metadata |
| License | MIT |
| Difficulty | medium |

## Output API

```python
from featurelifted import slugify, smart_truncate
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Transliteration | unidecode integration / `special.py` | `test_html_entity_decimal_and_hexadecimal_handling` |
| Unicode mode | slugify unicode branch | `test_allow_unicode_preserves_non_ascii_words` |
| Truncation helper | `smart_truncate` | `test_smart_truncate_edges` |

## Manual Oracle Closure Plan

Oracle pass `final_score=1.0`; Copy-All pass `final_score≈0.2`.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio |
| --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | pass | ~0.15 |
