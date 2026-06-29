# Task Design: `pathvalidate__sanitize_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Cross-platform filename/path sanitization is a common need when exporting user content to disk (reports, uploads, ETL outputs). `pathvalidate` couples platform tables, reserved Windows device names, per-segment path rules, and rich validation errors across several internal modules—easy to get wrong with a thin regex wrapper.

## Practical reuse（必填）

1. **Reuse module** — A standalone path sanitizer: `sanitize_filename` / `sanitize_filepath` plus typed validation errors for unsafe names on Windows, macOS, and Linux.
2. **Who imports it** — Backend services writing user-supplied names to object storage or local exports; CLI tools generating cross-platform artifact paths without vendoring all of pathvalidate's CLI integrations.
3. **Why not copy-all** — Upstream bundles click/argparse adapters, LTSV label helpers, symbol replacement, examples, and a large upstream test tree; the reusable slice is the filename/filepath core (~9 modules).

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/thombashi/pathvalidate |
| Commit | `1ca0a50fce51d5b5bd633457a72abf74dbe3112d` |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, config_environment_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["config_environment_coupling", "parser_state_coupling", "implicit_dependency_coupling"],
  "description": "Sanitization couples platform detection, reserved-name tables, per-segment filename rules, path normalization, and typed validation error metadata.",
  "signals": ["Platform enum", "ReservedNameHandler", "segment-wise FilePathSanitizer", "ErrorReason codes"]
}
```

## Target Feature

### Source entrypoints

- `pathvalidate.sanitize_filename` / `sanitize_filepath`
- `pathvalidate.validate_filename` / `validate_filepath`
- `pathvalidate.error.ValidationError`, `ErrorReason`, `ReservedNameError`
- `pathvalidate._filename`, `pathvalidate._filepath`, `pathvalidate._base`, `pathvalidate._common`

### Output API

```python
from featurelifted import (
    Platform,
    sanitize_filename,
    sanitize_filepath,
    validate_filename,
    validate_filepath,
    is_valid_filename,
    is_valid_filepath,
    ValidationError,
    ErrorReason,
    ReservedNameError,
    InvalidCharError,
)
```

## Included Behaviors

- Replace invalid filename/path characters
- Windows reserved device names (CON, PRN, …) sanitized or rejected per platform
- `ValidationError.reason` and `reserved_name` metadata
- Multi-segment `sanitize_filepath` with per-entry filename rules

## Excluded Behaviors

- click/argparse CLI adapters, LTSV/symbol helpers
- Original `pathvalidate` import at runtime
- Upstream tests in oracle closure

## Public Tests

- Basic invalid-char replacement in filenames
- Path segment sanitization
- Simple valid filename acceptance

## Hidden Tests

- Windows `CON` → `CON_` after sanitize
- `ReservedNameError` / `ErrorReason.RESERVED_NAME` on validate
- Multi-segment `abc/CON/xyz` sanitization on universal platform
- Invalid-character `ErrorReason` typing
- No `pathvalidate` import surface in submission

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/_const.py` | `test_windows_reserved_name_sanitize` |
| Probe-2 | `featurelifted/_filename.py` | `test_windows_reserved_name_validate_raises` |
| Probe-3 | `featurelifted/_filepath.py` | `test_sanitize_filepath_reserved_segment` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~1500+ | 1520 |
| Source repo Python LOC | ~5400 (incl. tests) | 4408 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.345** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + margin | **0.922** (Δ=0.577) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  __version__.py
  error.py
  handler.py
  _base.py
  _common.py
  _const.py
  _types.py
  _filename.py
  _filepath.py
```

## Go / No-Go Criteria

- Practical reuse narrative holds for export/upload path safety.
- Oracle passes public + hidden; naive fails hidden on reserved-name semantics.
- ≥3 module probes verified after Step 5.
- Copy-all extraction clearly above oracle.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `pathvalidate__sanitize_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.247 | 0.753 | **B-tier: 全过，ext≈0.25 vs oracle 0.35** |
