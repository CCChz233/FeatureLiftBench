# FeatureLift Task: tinycss2 stylesheet roundtrip

Extract a task-scoped subset of `tinycss2` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ast,
    parse_stylesheet,
    serialize,
)
```

## Required API Details

- `parse_stylesheet(css: str, skip_comments: bool = False, skip_whitespace: bool = False) -> list`
- `serialize(nodes) -> str`
- `ast.QualifiedRule` class must be importable
- `ast.AtRule` class must be importable
- `ast.ParseError` class must be importable

## Required Behavior

- parse_stylesheet returns QualifiedRule nodes for qualified rules and AtRule nodes for at-rules; malformed CSS such as an unmatched `}` is represented by a ParseError node instead of raising an exception.
- Serializing nodes returned by parse_stylesheet produces CSS containing the original rule content, and an `@import` rule retains its `@import` keyword after parse/serialize round-trip.
- When parse_stylesheet is called with `skip_whitespace=True`, its top-level result contains no node whose type name ends with `WhitespaceToken`.
- Parsing a selector rule such as `h1.title{}` returns a QualifiedRule whose `prelude` attribute is non-empty.
- The package exposes the required task API paths `featurelifted.parse_stylesheet`, `featurelifted.serialize`, `featurelifted.ast.QualifiedRule`, `featurelifted.ast.AtRule`, `featurelifted.ast.ParseError` with the kinds and callable signatures listed in this contract.
- Scanning every Python file in the submitted package finds no `import tinycss2` or `from tinycss2 ...` statement.

## Constraints

- Forbidden imports: `tinycss2`.
- Do not implement full CSSOM.
- Do not implement browser layout.
- Do not implement original tinycss2 import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — parse_stylesheet returns QualifiedRule nodes for qualified rules and AtRule nodes for at-rules; malformed CSS such as an unmatched `}` is represented by a ParseError node instead of raising an exception.
- **B002** — Serializing nodes returned by parse_stylesheet produces CSS containing the original rule content, and an `@import` rule retains its `@import` keyword after parse/serialize round-trip.
- **B003** — When parse_stylesheet is called with `skip_whitespace=True`, its top-level result contains no node whose type name ends with `WhitespaceToken`.
- **B004** — Parsing a selector rule such as `h1.title{}` returns a QualifiedRule whose `prelude` attribute is non-empty.
- **B005** — The package exposes the required task API paths `featurelifted.parse_stylesheet`, `featurelifted.serialize`, `featurelifted.ast.QualifiedRule`, `featurelifted.ast.AtRule`, `featurelifted.ast.ParseError` with the kinds and callable signatures listed in this contract.
- **B006** — Scanning every Python file in the submitted package finds no `import tinycss2` or `from tinycss2 ...` statement.
<!-- featureliftbench:behavior-clauses:end -->
