# FeatureLift Task: pytest fixture name resolution

Extract pytest fixture name closure resolution and lookup helpers from _pytest.fixtures as a standalone package.

## Target API

- Import: `from featurelifted import FixtureDef, FixtureLookupError, FixtureRegistry, deduplicate_names, fixture, getfixturemarker, resolve_fixture_closure`
- Callable: `featurelifted.resolve_fixture_closure`
- Signature: `resolve_fixture_closure(parent_nodeids, initialnames, registry, ignore_args=None) -> tuple[list[str], dict[str, tuple[FixtureDef, ...]]]`

## Excluded Behavior

- fixture execution, setup/teardown, and parametrization
- full pytest collection and plugin manager integration
- request.getfixturevalue dynamic lookup
- CLI, original tests, docs, packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pytest`, `_pytest`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — resolve transitive fixture name closure from initial argnames
- **B002** — match fixture definitions to parent nodeids
- **B003** — deduplicate fixture name sequences preserving order
- **B004** — sort closure fixtures by scope (session before function)
- **B005** — detect missing fixtures via FixtureLookupError
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: pytest, _pytest
<!-- featureliftbench:behavior-clauses:end -->
