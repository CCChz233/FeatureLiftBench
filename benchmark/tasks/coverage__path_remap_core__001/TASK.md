# FeatureLift Task: Combine path remap

Extract coverage.py PathAliases logic that remaps measured file paths when combining data from different machines or checkout roots.

## Target API

- Import: `from featurelifted import PathAliases; from featurelifted.exceptions import ConfigError`
- Callable: `featurelifted.PathAliases.map`
- Signature: `PathAliases(...).map(path: str, exists: Callable[[str], bool] = ...) -> str`

## Excluded Behavior

- glob include/omit matching for measurement
- run-section configuration parsing
- InOrOut source selection policy
- coverage data combine I/O and SQLite storage
- original project tests and CLI

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `coverage`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — register glob-style path prefix aliases
- **B002** — map absolute and relative paths through the first matching alias
- **B003** — normalize path separators to the alias result style
- **B004** — reject alias patterns ending in wildcards with ConfigError (message: must not end with wildcards)
- **B005** — skip mappings when the mapped target path does not exist
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: coverage
<!-- featureliftbench:behavior-clauses:end -->
