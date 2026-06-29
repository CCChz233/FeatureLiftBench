# Task Design: `tabulate__table_format_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Pretty-printing tabular data is a common utility need (CLI output, logs, notebooks). `python-tabulate` couples dozens of table format templates, Unicode display-width measurement, column alignment, and data normalization in a ~2900-line monolith—easy to break with a naive `str.ljust` wrapper.

## Practical reuse（必填）

1. **Reuse module** — A standalone text table formatter: `tabulate()` with format registry, column alignment, and wide-character width handling.
2. **Who imports it** — Data tools, REPL helpers, and services that render fixed-width tables without pulling in CLI entrypoints or the full upstream package.
3. **Why not copy-all** — Upstream bundles CLI (`cli.py`), benchmarks, examples, and a large upstream test tree; the reusable slice is the formatting core in `tabulate/__init__.py`.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/astanin/python-tabulate |
| Commit | `268615a5c27dc40e5c22454c07b44d5c50410da0` |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, data_model_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["data_model_coupling", "resource_coupling", "implicit_dependency_coupling"],
  "description": "Table formatting couples format template registry, Unicode/wcwidth display width, numeric type inference, column alignment, and row normalization in one module.",
  "signals": ["_table_formats registry", "_visible_width / wcwidth", "numalign decimal padding", "colglobalalign override"]
}
```

## Target Feature

### Source entrypoints

- `tabulate.tabulate`
- `tabulate.tabulate_formats`
- `tabulate.simple_separated_format`
- `tabulate._visible_width`, `tabulate._align_column`, `tabulate._format_table`
- `tabulate._normalize_tabular_data`, `tabulate._table_formats`

### Output API

```python
from featurelifted import tabulate, tabulate_formats, simple_separated_format
```

## Included Behaviors

- `tabulate()` with common table formats (`simple`, `grid`, `pipe`, `plain`)
- Automatic numeric vs string column alignment
- Per-column `colalign` and global `colglobalalign`
- Unicode wide-character column width (when `wcwidth` available)
- ANSI escape sequence width stripping
- `simple_separated_format` custom separator templates
- `tabulate_formats` registry listing supported format names

## Excluded Behaviors

- CLI (`tabulate/cli.py`, `__main__`)
- Jupyter/HTML display helpers beyond string output
- Upstream test suite in oracle closure
- Original `tabulate` import at runtime

## Public Tests

- Basic `simple` and `grid` formatting with ASCII data
- Explicit column headers
- `tabulate_formats` contains expected format names

## Hidden Tests

- `numalign="decimal"` decimal-point alignment
- Wide-character (CJK) grid alignment with `wcwidth`
- `colglobalalign` with per-column `colalign` override
- `pipe` format alignment colons in separator row
- ANSI-colored cell visible width
- No `tabulate` import surface in submission

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/formats.py` | `test_pipe_format_colalign` |
| Probe-2 | `featurelifted/layout.py` | `test_wide_char_grid_alignment` |
| Probe-3 | `featurelifted/render.py` | `test_decimal_column_alignment` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~2400+ | 2311 |
| Source repo Python LOC | ~7600 | 7641 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.302** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + margin | **0.966** (Δ=0.664) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  formats.py      # format templates + _table_formats registry
  layout.py       # width, alignment, normalization, wrapping
  render.py       # tabulate() + _format_table
```

## Go / No-Go Criteria

- Practical reuse narrative holds for offline table rendering.
- Oracle passes public + hidden; naive fails hidden on width/alignment semantics.
- ≥3 module probes verified after Step 5.
- Copy-all extraction clearly above oracle.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| (pending Step 6) | | | | | |
