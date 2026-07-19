# FeatureLift Task: LALR parse tree core

Extract Lark grammar loading and LALR parsing into parse trees as a standalone package.

## Target API

- Import: `from featurelifted import Lark, Tree, Token, UnexpectedToken, UnexpectedCharacters`
- Callable: `featurelifted.Lark.parse`
- Signature: `Lark.parse(text: str, start: str | None = None, on_error: Callable | None = None) -> Tree`

## Excluded Behavior

- tree Transformer and Visitor APIs as public surface
- standalone code generation tools
- earley-only advanced forest transforms
- original project tests and documentation

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `lark`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse input with inline grammars using LALR
- **B002** — build Tree nodes with rule data and Token leaves
- **B003** — support %import, %ignore, and common terminal imports
- **B004** — raise structured parse errors with line/column context
- **B005** — expose pretty() and child navigation on trees
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: lark
<!-- featureliftbench:behavior-clauses:end -->
