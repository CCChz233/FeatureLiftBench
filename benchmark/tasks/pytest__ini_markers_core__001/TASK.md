# FeatureLift Task: pytest ini markers parsing

Extract pytest ini markers linelist parsing and marker line normalization.

## Target API

- Import: `from featurelifted import MarkerRegistry, parse_linelist, split_marker_line`
- Callable: `featurelifted.MarkerRegistry.from_ini`
- Signature: `from_ini(value: str | list[str]) -> MarkerRegistry`

## Excluded Behavior

- full Config initialization and plugin loading
- strict marker validation at collection
- conftest and pyproject discovery
- CLI --markers display

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pytest`, `_pytest`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse multiline ini markers values into linelist entries
- **B002** — append marker lines preserving order
- **B003** — split marker lines into name and description (strip name; preserve description whitespace)
- **B004** — strip whitespace from linelist entries
- **B005** — MarkerRegistry preserves marker declaration order from ini lines
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: pytest, _pytest
<!-- featureliftbench:behavior-clauses:end -->
