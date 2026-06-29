# Task Design: `xmltodict__xml_parse_core__001`

Status: agent-calibrated

## Why This Task

XML-to-dict bridges are common in config ingestion and API adapters. xmltodict couples expat SAX handler stack state, namespace URI rewriting, attribute-prefix conventions, and symmetric unparse emission—more than a thin ElementTree wrapper.

## Practical reuse

1. **Reuse module** — Standalone XML ↔ ordered-dict converter for config snippets and legacy SOAP/Atom payloads.
2. **Who imports it** — Backend teams embedding XML mapping in workers or ETL without vendoring full xmltodict test harness.
3. **Why not copy-all** — Upstream is a single module but ships extensive tests and streaming CLI; compact split closure documents logical boundaries for probes.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/martinblech/xmltodict |
| Commit | `966b903e4441f27816cd39ecf3305727b294a9c5` |
| License | MIT |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, parser_state_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "resource_coupling", "implicit_dependency_coupling"],
  "primary": "parser_state_coupling",
  "description": "SAX handler stack, namespace declarations, attr_prefix/cdata_key conventions, and unparse validation are tightly coupled."
}
```

## Target Feature

### Source entrypoints

- `xmltodict.parse`
- `xmltodict.unparse`
- `xmltodict._DictSAXHandler`
- `xmltodict._process_namespace`

### Output API

```python
from featurelifted import parse, unparse, ParsingInterrupted
```

## Included Behaviors

- Parse XML to ordered dict with default `@` attribute prefix
- Unparse dict back to XML
- Repeated siblings become lists
- `process_namespaces` with optional URI collapse map
- Mixed content (`#text` + child elements)
- Custom `attr_prefix` and `force_cdata`

## Excluded Behaviors

- Streaming `item_depth` / `item_callback` / `ParsingInterrupted` control
- `postprocessor`, `force_list`, `process_comments`
- CLI marshal entrypoint (`__main__`)
- Original `xmltodict` import at runtime

## Public Tests

- Simple text node parse
- Default `@` attributes
- Repeated siblings → list
- Basic `unparse` and simple roundtrip

## Hidden Tests

- Namespace collapse with `process_namespaces` + `namespaces` map
- Custom `attr_prefix` parse and unparse roundtrip
- Semi-structured mixed content (`#text` + empty child)
- `force_cdata=True` text wrapping
- No runtime `xmltodict` import surface

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/sax_handler.py` | `test_namespace_collapse_map` |
| Probe-2 | `featurelifted/validation.py` | `test_unparse_custom_attr_prefix_roundtrip` |
| Probe-3 | `featurelifted/unparse.py` | `test_unparse_custom_attr_prefix_roundtrip` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~500+ | 566 |
| Source repo Python LOC | ~650+ | 1590 (incl. upstream tests in snapshot) |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.356** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + margin | **1.002** (Δ=0.646) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  exceptions.py
  sax_handler.py
  validation.py
  parse.py
  unparse.py
```

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `xmltodict__xml_parse_core__001-flash-001` | deepseek_v4_flash | no (hidden fail) | 0.225 | 0.000 | **A-tier: pub pass / hidden fail，ext≈0.23** |

## Go / No-Go Criteria

- Practical reuse narrative holds for XML config/adapter embedding.
- Oracle passes public + hidden; naive fails hidden on namespace/mixed-content semantics.
- ≥3 module probes verified after Step 5.
- Copy-all penalized vs compact oracle on ExtractionRatio.
