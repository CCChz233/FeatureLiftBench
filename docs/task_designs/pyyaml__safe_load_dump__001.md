# Task Design: pyyaml__safe_load_dump__001

Status: oracle-verified

## Why This Task

Safe YAML load/dump pipeline without unsafe constructors. Flash passes with **extraction_ratio≈0.92** (copy-heavy functional pass).

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/yaml/pyyaml` |
| Commit | `6.0.1-installed-snapshot` |
| License | MIT |
| Difficulty | hard |

## Output API

```python
from featurelifted import safe_load, safe_load_all, safe_dump, safe_dump_all, YAMLError
from featurelifted.constructor import ConstructorError
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Safe constructor | `constructor.py` SafeConstructor | `test_multi_document_dump_load_and_unsafe_tags_rejected` |
| Composer / anchors | composer merge-key path | `test_anchors_aliases_merge_keys_and_dates` |
| Parser errors | scanner/parser | `test_parse_errors_and_flow_style_dumping` |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | Notes |
| --- | --- | --- | --- | --- |
| `benchmark-28-deepseek-flash-003` | deepseek-v4-flash | pass | ~0.92 | decoupling discriminator weak |
