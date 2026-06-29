# Task Design: `jsonpath_ng__expression_eval_core__001`

Status: agent-calibrated (B-tier exception promote)

## Spike Decision

**GO — promoted to main benchmark (batch-1 #4).**

Extract JSONPath parse/find/update with filter expressions (`ext` parser). Oracle omits vendored `_ply` and `bin/`; patches lexer/parser to use system `ply`.

## Practical reuse

1. **Reuse module** — embedded JSONPath query engine for config/query pipelines without full jsonpath-ng distribution.
2. **Who imports it** — ETL tools, API gateways, document transformers that evaluate JSONPath offline.
3. **Why not copy-all** — package includes CLI and duplicates PLY; compact closure uses external `ply` and drops `bin/`.

## Source

| Field | Value |
| --- | --- |
| Source repo | `https://github.com/h2non/jsonpath-ng` |
| Commit | `e59ead334ac47618e6d844ad758114b3bfafcc8a` (v1.8.0) |
| License | Apache-2.0 |
| Difficulty | hard |
| Tags | `batch-1`, `jsonpath`, `hard-first`, `functional-discriminator`, `parser_state_coupling` |

## Target API

```python
from featurelifted import parse
from featurelifted.jsonpath import JSONPath
from featurelifted.exceptions import JsonPathLexerError, JsonPathParserError
```

Public `parse` re-exports extended parser (filters + core paths).

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/ext/filter.py` | `test_filter_expression_selects_items` |
| Probe-2 | `featurelifted/parser.py` | `test_bracket_slice_selects_range` |
| Probe-3 | `featurelifted/jsonpath.py` | `test_update_nested_path` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | **pass** |
| Hidden tests | pass | **pass** |
| ExtractionRatio | 0.20–0.60 | **0.343** |
| Naive hidden fail | yes | **pass** (public pass, hidden fail) |
| Copy-all vs oracle | ≥0.30 higher | **pass** (1.0 vs 0.343) |
| Module probes | ≥3 | **3/3 pass** |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `jsonpath_ng__expression_eval_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 1.0 | 0.0 | **A-tier (copy-heavy):** full-repo copy; scoring penalizes vs oracle 0.657 |

Target: strong agents either fail hidden on compact implementations, or pass functionally but score poorly when copying the entire package.
