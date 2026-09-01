# FeatureLift Task: AST token annotation

Build a standalone `featurelifted` package providing asttokens-style `ASTTokens` annotation of parsed Python AST nodes with source text and tokens.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ASTTokens,
)
```

## Required API Details

- `ASTTokens(source_text, parse=False, tree=None, filename='<unknown>', tokens=None)` class constructor
  - `ASTTokens.__init__(self, source_text, parse=False, tree=None, filename='<unknown>', tokens=None)`
  - `ASTTokens.get_text(self, node, padded=True) -> str`
  - `ASTTokens.get_token(self, lineno, col_offset)`

## Required Behavior

- Constructing `ASTTokens(source, parse=True)` annotates the parsed tree so `get_text` of a binary-operation node returns the exact source snippet for that operation, such as `1 + 2`.
- For an assignment statement in the parsed tree, `get_text` returns the full assignment source text, such as `x = 1 + 2`, without requiring a trailing comment to be present.
- `get_token(lineno, col_offset)` returns the token whose `.string` equals the source characters at that line and column, such as the name `x` at column 0 of `x = 1 + 2`.
- The package exposes `ASTTokens` with construction, `get_text`, and `get_token` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `asttokens`.

## Constraints

- Forbidden imports: `asttokens`.
- Do not implement executing/stack_data traceback UX.
- Do not implement comment token inclusion.
- Do not implement runtime import of asttokens.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Constructing `ASTTokens(source, parse=True)` annotates the parsed tree so `get_text` of a binary-operation node returns the exact source snippet for that operation, such as `1 + 2`.
- **B002** — For an assignment statement in the parsed tree, `get_text` returns the full assignment source text, such as `x = 1 + 2`, without requiring a trailing comment to be present.
- **B003** — `get_token(lineno, col_offset)` returns the token whose `.string` equals the source characters at that line and column, such as the name `x` at column 0 of `x = 1 + 2`.
- **B004** — The package exposes `ASTTokens` with construction, `get_text`, and `get_token` as listed in this contract.
- **B005** — The submitted package source does not import the forbidden upstream package `asttokens`.
<!-- featureliftbench:behavior-clauses:end -->
