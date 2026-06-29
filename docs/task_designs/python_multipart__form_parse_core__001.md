# Task Design: `python_multipart__form_parse_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Multipart form parsing is a reusable offline byte-stream parser embedded in HTTP stacks. python-multipart couples incremental parser state, header parsing, transfer-encoding decoders, and file spill logic—testable without ASGI or sockets.

## Practical reuse（必填）

1. **Reuse module** — Standalone multipart/form-data parser for upload pipelines, CLI tools, or middleware that must parse raw bodies from bytes buffers.
2. **Who imports it** — Teams vendoring upload parsing without Starlette/FastAPI, or building test harnesses that replay captured multipart bodies.
3. **Why not copy-all** — The upstream package bundles urlencoded/octet-stream parsers, fuzz targets, and test fixtures; compact closure keeps multipart path plus decoders only.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/Kludex/python-multipart |
| Commit | `98080c5de45bc23317577086dd9076ba85bc9ce2` |
| License | Apache-2.0 |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, parser_state_coupling, resource_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "resource_coupling", "implicit_dependency_coupling"],
  "primary": "parser_state_coupling",
  "description": "Multipart parsing couples state machine transitions, decoder chaining, and File spill thresholds."
}
```

## Target Feature

### Source entrypoints

- `python_multipart.multipart.FormParser`
- `python_multipart.multipart.parse_form`
- `python_multipart.multipart.parse_options_header`

### Output API

```python
from featurelifted import Field, File, FormParser, parse_form, create_form_parser, parse_options_header
from featurelifted.exceptions import FormParserError, MultipartParseError
```

## Included Behaviors

- Incremental multipart/form-data parsing
- Field and file parts with headers
- Base64 CTE, preamble/epilogue handling
- Disk spill and header limits

## Excluded Behaviors

- urlencoded and octet-stream FormParser branches
- ASGI/Starlette integration
- Original `python_multipart` import

## Public Tests

- Simple field and file parts
- `parse_options_header` boundary extraction
- `parse_form` / `create_form_parser` helpers

## Hidden Tests

- Chunked incremental parsing
- Base64 Content-Transfer-Encoding
- Preamble and epilogue handling
- Missing Content-Disposition name error
- MAX_MEMORY_FILE_SIZE disk spill
- MAX_HEADER_SIZE exceeded
- No forbidden imports

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/decoders.py` | `test_base64_content_transfer_encoding` |
| Probe-2 | `featurelifted/multipart_parse.py` | `test_incremental_chunked_parsing` |
| Probe-3 | `featurelifted/models.py` | `test_max_memory_file_size_spills_to_disk` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~1200+ | 1218 |
| Source repo Python LOC | ~3000+ | 3161 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.385** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + 0.25 | **0.890** (Δ=0.504) |
| Module probes | all verified | 3/3 OK |

## Go / No-Go Criteria

- Oracle passes public + hidden; naive fails hidden on parser/decoder semantics.
- ExtractionRatio in band; copy-all penalized vs compact oracle.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| TBD | | | | | |
