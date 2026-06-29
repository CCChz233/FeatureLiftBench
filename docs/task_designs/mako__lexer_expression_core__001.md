# Task Design: `mako__lexer_expression_core__001`

Status: agent-calibrated (B-tier exception promote)

## Why This Task

Mako templates power many Python web stacks; the lexer and Python-fragment analyzer are a reusable preprocessing slice distinct from Jinja2's delimiter model. Hidden tests stress percent-escape rules, filter escape builtins, and partial-control identifier walks that shallow regex lexers miss.

## Practical reuse（必填）

1. **Reuse module** — Standalone Mako template lexer + expression/control fragment analyzer for static template inspection, linting, or codegen front-ends.
2. **Who imports it** — Framework maintainers, template linters, or doc extractors that need parse trees without pulling full Mako runtime/lookup.
3. **Why not copy-all** — Upstream bundles codegen, runtime, lookup, cache, and ext plugins; the parse slice is ~10 modules vs the full package.

## Source

| Field | Value |
| --- | --- |
| Source repo | https://github.com/sqlalchemy/mako |
| Commit | `d58a9208fd62a816e9609a35be55aa6d3c5b14e7` |
| License | MIT |
| Language | Python |
| Difficulty | hard |
| Tags | batch-1, functional-discriminator, parser_state_coupling |

## Entanglement

```json
{
  "level": "high",
  "types": ["parser_state_coupling", "framework_coupling", "implicit_dependency_coupling"],
  "primary": "parser_state_coupling",
  "description": "Lexer tag/control stacks, parsetree construction, and AST identifier analysis are intertwined.",
  "signals": ["ternary control stack", "PythonFragment partial stmt rewriting", "filter DEFAULT_ESCAPES merge"]
}
```

## Target Feature

### Source entrypoints

- `mako.lexer.Lexer.parse`
- `mako.parsetree.*`
- `mako.ast.PythonCode`, `PythonFragment`
- `mako.pyparser.parse`

### Output API

```python
from featurelifted import Lexer, parsetree, PythonCode, PythonFragment, SyntaxException, CompileException
```

## Included Behaviors

- Lex text, `${expr}`, `% control`, and `<%def>` tags into parsetree
- PythonCode / PythonFragment declared vs undeclared identifier sets
- SyntaxException on unclosed tags; CompileException on invalid partial control

## Excluded Behaviors

- Template compile/render, lookup, cache, CLI, extensions
- Original `mako` import at runtime

## Public Tests

- Text + expression, control lines, PythonCode undeclared, def tag

## Hidden Tests

- Percent escape `%%`, unclosed tag error type, PythonFragment for-loop ids
- Expression filter escapes (`h`, `trim`), elif partial control ids
- Forbidden mako import surface scan

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Probe-1 | `featurelifted/pyparser.py` | `test_python_fragment_for_loop` |
| Probe-2 | `featurelifted/_ast_util.py` | `test_elif_partial_control_identifiers` |
| Probe-3 | `featurelifted/parsetree.py` | `test_expression_filter_escapes` |

## Manual Oracle Closure Plan

| Check | Target | Result |
| --- | --- | --- |
| Public tests | pass | pass (oracle, copy_all, naive) |
| Hidden tests | pass | pass (oracle, copy_all); **fail** (naive) |
| Forbidden import check | pass | pass |
| Oracle LOC | ~2500+ | 2782 |
| Source repo Python LOC | ~3500+ | 6541 |
| ExtractionRatio | 0.20 – 0.60 | oracle **0.425** |
| Copy-All functional gate | 1.0 | pass |
| Copy-All ExtractionRatio | > oracle + margin | **0.938** (Δ=0.513) |
| Module probes | all verified | 3/3 OK |

Expected closure shape:

```text
featurelifted/
  __init__.py
  lexer.py
  parsetree.py
  ast.py
  pyparser.py
  _ast_util.py
  exceptions.py
  filters.py
  util.py
  compat.py
  pygen.py
```

## Go / No-Go Criteria

- Oracle passes public + hidden; naive fails hidden on escapes/fragment semantics.
- ≥3 module probes verified.
- ExtractionRatio in band; copy-all penalized vs compact oracle.

## Agent Calibration

| Run | Model | Passed | ExtractionRatio | final_score | Notes |
| --- | --- | --- | ---: | ---: | --- |
| `mako__lexer_expression_core__001-flash-001` | deepseek_v4_flash | yes (all tests) | 0.316 | 0.684 | **B-tier: 全过，ext≈0.32 vs oracle 0.43** |
