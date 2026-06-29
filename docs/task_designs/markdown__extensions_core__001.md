# Task Design: `markdown__extensions_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Markdown renderer with tables/footnotes for docs sites.
2. **Who imports it** — Static site tooling needing python-markdown extensions subset.
3. **Why not copy-all** — Full extension pack inflates copy-all; oracle keeps core + 2 extensions.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Tables extension | `featurelifted/extensions/tables.py` | `test_table_header_align` |
| Footnotes extension | `featurelifted/extensions/footnotes.py` | `test_footnote_backlink` |
| Block processors | `featurelifted/blockprocessors.py` | `test_table_row_span` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | |
| Hidden tests | pass | |
| ExtractionRatio | 0.20 – 0.60 | |
| Copy-All delta | ≥ 0.25 | |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| | | | | | Flash deferred |
