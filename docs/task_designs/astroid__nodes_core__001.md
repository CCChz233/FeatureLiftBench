# Task Design: `astroid__nodes_core__001`

Status: agent-calibrated (B-tier exception promote)

## Practical reuse

1. **Reuse module** — Extract astroid string parsing into NodeNG trees via TreeRebuilder without inference, brain plugins, or import introspection.
2. **Who imports it** — Static analysis and lint tooling needing lightweight AST nodes without full pylint/astroid inference graph.
3. **Why not copy-all** — Full astroid tree is large; compact closure attempted but `bases` ↔ `nodes.node_classes` circular import blocks functional oracle.

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| TreeRebuilder | `featurelifted/rebuilder.py` | `test_async_and_match_statements` |
| Nodes package | `featurelifted/nodes/node_classes.py` | `test_defaults_and_docstring` |
| Builder | `featurelifted/builder.py` | `test_module_as_string_contains_def` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | **fail** (circular import) |
| Hidden tests | pass | **fail** |
| ExtractionRatio | 0.20 – 0.60 | **0.713** (over cap) |
| Copy-All delta | ≥ 0.25 | 0.281 (copy-all passes) |

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| oracle | — | no | 0.713 | 0.0 | bases/nodes cycle; needs smaller slice or full inference chain |
| naive | — | no | 0.001 | — | |
| | | | | | **Skipped promote** batch-1 #50 |
