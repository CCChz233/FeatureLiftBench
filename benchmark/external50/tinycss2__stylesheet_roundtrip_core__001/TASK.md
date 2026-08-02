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

- The extracted feature must support this observable behavior: parse stylesheet into QualifiedRule/AtRule/ParseError nodes. Required observable cases include parse qualified rule; parse at rule; parse error node not raise.
- The extracted feature must support this observable behavior: serialize nodes back to CSS. Required observable cases include roundtrip simple; serialize preserves at keyword.
- The extracted feature must support this observable behavior: skip_whitespace option. Required observable cases include skip whitespace option.
- QualifiedRule exposes a prelude used by selectors.
- The package exposes the required task API paths `featurelifted.parse_stylesheet`, `featurelifted.serialize`, `featurelifted.ast.QualifiedRule`, `featurelifted.ast.AtRule`, `featurelifted.ast.ParseError` with the kinds and callable signatures listed in this contract.
- the submitted package does not import forbidden upstream packages: tinycss2.

## Constraints

- Forbidden imports: `tinycss2`.
- Do not implement full CSSOM.
- Do not implement browser layout.
- Do not implement original tinycss2 import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: parse stylesheet into QualifiedRule/AtRule/ParseError nodes. Required observable cases include parse qualified rule; parse at rule; parse error node not raise.
- **B002** — The extracted feature must support this observable behavior: serialize nodes back to CSS. Required observable cases include roundtrip simple; serialize preserves at keyword.
- **B003** — The extracted feature must support this observable behavior: skip_whitespace option. Required observable cases include skip whitespace option.
- **B004** — QualifiedRule exposes a prelude used by selectors.
- **B005** — The package exposes the required task API paths `featurelifted.parse_stylesheet`, `featurelifted.serialize`, `featurelifted.ast.QualifiedRule`, `featurelifted.ast.AtRule`, `featurelifted.ast.ParseError` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: tinycss2.
<!-- featureliftbench:behavior-clauses:end -->
