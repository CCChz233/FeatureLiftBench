# FeatureLift Task: Python parser grammar core

Extract parso parse/load_grammar with error recovery and get_code roundtrip.

## Target API

- Import: `import featurelifted; from featurelifted import parse, load_grammar, Grammar`
- Callable: `featurelifted.parse`
- Signature: `parse(code=None, *, version=None, **kwargs)`

## Excluded Behavior

- diff parser
- pep8 normalizer
- original parso import

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `parso`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse Python source to syntax tree
- **B002** — get_code round-trip on nodes
- **B003** — iter_errors for multiple syntax issues
- **B004** — version-specific grammars
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: parso
<!-- featureliftbench:behavior-clauses:end -->
