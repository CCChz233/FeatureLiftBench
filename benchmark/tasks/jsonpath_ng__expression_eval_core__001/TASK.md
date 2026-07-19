# FeatureLift Task: JSONPath parse, find, and update core

Extract jsonpath-ng expression parsing and evaluation (including filter expressions) without CLI or original package import.

## Target API

- Import: `import featurelifted; from featurelifted import parse; from featurelifted.jsonpath import JSONPath; from featurelifted.exceptions import JsonPathLexerError, JsonPathParserError`
- Callable: `featurelifted.parse`
- Signature: `parse(path_string)`

## Excluded Behavior

- CLI bin/jsonpath.py
- original jsonpath_ng import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `jsonpath_ng`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse JSONPath strings into expression objects
- **B002** — find matching values in dict/list document trees
- **B003** — update values at matching paths in place
- **B004** — filter expressions with comparison operators
- **B005** — array slices and wildcard/index segments
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: jsonpath_ng
<!-- featureliftbench:behavior-clauses:end -->
