# Task Design: `python_frontmatter__roundtrip_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Markdown with YAML front matter is a common content-pipeline pattern (static sites, docs generators, CMS exports). `python-frontmatter` couples delimiter detection, handler plugins, unicode normalization, and `Post` metadata proxies—distinct from raw PyYAML load/dump.

## Practical reuse

1. **Reuse module** — Standalone front-matter parser/writer for markdown files with YAML metadata blocks.
2. **Who imports it** — Static-site tooling, doc pipelines, or CMS adapters that need `loads`/`dumps` round-trip without vendoring examples/tests.
3. **Why not copy-all** — Upstream bundles doctest fixtures, TOML/JSON handler demos, and Sphinx docs; compact closure keeps YAML path + `Post` API only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/eyeseast/python-frontmatter |
| Commit | `dc7c0af5466b104e0ba01ae3c5b2cd77edc27292` |
| License | MIT |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, parser_state_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "config_environment_coupling", "third_party_dependency_coupling"],
  "primary": "parser_state_coupling",
  "description": "Front matter parsing couples delimiter regex detection, handler split/load/export, unicode line-ending normalization, and Post metadata/content duality.",
  "signals": [
    "YAMLHandler.FM_BOUNDARY allows trailing whitespace on delimiter lines",
    "parse() merges caller defaults before handler load",
    "util.u() normalizes CRLF before split",
    "dumps() respects post.handler and custom delimiters"
  ]
}
```

## Target API

```python
from featurelifted import Post, parse, load, loads, dump, dumps, checks
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| YAML handler | `featurelifted/default_handlers.py` | `test_extra_space_after_opening_delimiter` |
| Unicode util | `featurelifted/util.py` | `test_crlf_bytes_normalize` |
| Parse / Post core | `featurelifted/__init__.py` | `test_parse_defaults_merge` |

## Public Tests

- `loads` parses YAML front matter into `Post` with metadata keys and body content
- `dumps` + `loads` round-trip preserves metadata and content
- `parse` returns `(metadata, content)` tuple

## Hidden Tests

- Opening delimiter with trailing space (`--- `)
- CRLF byte input normalized via `loads`
- No frontmatter and empty frontmatter blocks
- Unicode metadata round-trip in dump output
- `parse(..., **defaults)` merges defaults
- `Post.to_dict()` shape
- `checks()` detection
- Custom dump delimiters
- No runtime `frontmatter` import surface

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~700 | 516 |
| Source repo Python LOC | ~1664 | 1005 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.513** |
| Copy-All ExtractionRatio | > oracle + margin | **0.958** (Δ=0.445) |
| Module probes | ≥3 verified | **3/3 OK** |

Expected closure shape:

```text
featurelifted/
  __init__.py
  default_handlers.py
  util.py
  py.typed
```

## Go / No-Go Criteria

- Oracle compact closure passes; copy-all extraction clearly higher than oracle.
- Naive regex-only implementation fails hidden on delimiter/unicode/defaults edges.
- PyYAML allowed via empty lock + system-site-packages (documented in metadata).

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `python_frontmatter__roundtrip_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.305 | 0.695 | **B-tier: 全过，ext≈0.31 vs oracle 0.51** |
