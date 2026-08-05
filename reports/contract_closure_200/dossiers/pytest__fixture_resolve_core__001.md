# pytest__fixture_resolve_core__001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/19`

## Required API

- `featurelifted.FixtureDef` (class) `(argname: 'str', argnames: 'tuple[str, ...]', baseid: 'str', scope: 'str' = 'function') -> None`
- `featurelifted.FixtureLookupError` (exception)
- `featurelifted.FixtureRegistry` (class) `() -> 'None'`
- `featurelifted.FixtureRegistry.register` (method) `(self, fixturedef: 'FixtureDef') -> 'None'`
- `featurelifted.deduplicate_names` (function) `(*seqs: 'Iterable[str]') -> 'tuple[str, ...]'`
- `featurelifted.fixture` (function) `(fixture_function: 'FixtureFunction | None' = None, *, scope: 'str' = 'function', name: 'str | None' = None) -> 'FixtureFunctionMarker | FixtureFunction'`
- `featurelifted.getfixturemarker` (function) `(obj: 'object') -> 'FixtureFunctionMarker | None'`
- `featurelifted.resolve_fixture_closure` (function) `(parent_nodeids: 'AbstractSet[str]', initialnames: 'tuple[str, ...]', registry: 'FixtureRegistry', ignore_args: 'AbstractSet[str] | None' = None) -> 'tuple[list[str], dict[str, tuple[FixtureDef, ...]]]'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: resolve transitive fixture name closure from initial argnames. Required observable cases include resolve closure adds fixture dependencies; fixture lookup error lists available.
- **B002**: The extracted feature must support this observable behavior: match fixture definitions to parent nodeids. Required observable cases include fixture lookup error lists available.
- **B003**: The extracted feature must support this observable behavior: deduplicate fixture name sequences preserving order. Required observable cases include deduplicate names keeps first occurrence order.
- **B004**: The extracted feature must support this observable behavior: sort closure fixtures by scope (session before function). Required observable cases include resolve closure adds fixture dependencies; getfixturemarker on decorated function; closure sorted by scope descending.
- **B005**: The extracted feature must support this observable behavior: detect missing fixtures via FixtureLookupError. Required observable cases include getfixturemarker on decorated function; fixture lookup error lists available.
- **B006**: The package exposes the required task API paths `featurelifted.FixtureDef`, `featurelifted.FixtureLookupError`, `featurelifted.FixtureRegistry`, `featurelifted.FixtureRegistry.register`, `featurelifted.deduplicate_names`, `featurelifted.fixture`, `featurelifted.getfixturemarker`, `featurelifted.resolve_fixture_closure` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_resolve_closure_adds_fixture_dependencies`

- mapping: `B001, B004`
- API: `featurelifted.FixtureDef, featurelifted.FixtureRegistry, featurelifted.resolve_fixture_closure`
- risk: `none`
- A001 `assert` L23: `closure == ['db', 'conn']`
- A002 `assert` L24: `set(arg2defs) == {'db', 'conn'}`

### `public_tests/test_public_api.py::test_getfixturemarker_on_decorated_function`

- mapping: `B004, B005`
- API: `featurelifted.fixture, featurelifted.getfixturemarker`
- risk: `none`
- A001 `assert` L33: `marker is not None`
- A002 `assert` L34: `marker.scope == 'module'`
- A003 `assert` L35: `marker.name == 'resource'`

### `hidden_tests/test_hidden_behavior.py::test_deduplicate_names_keeps_first_occurrence_order`

- mapping: `B003`
- API: `featurelifted.deduplicate_names`
- risk: `ordering_semantics`
- A001 `assert` L12: `names == ('a', 'b', 'c')`

### `hidden_tests/test_hidden_behavior.py::test_closure_sorted_by_scope_descending`

- mapping: `B004`
- API: `featurelifted.FixtureDef, featurelifted.FixtureRegistry, featurelifted.resolve_fixture_closure`
- risk: `ordering_semantics`
- A001 `assert` L26: `closure.index('high') < closure.index('low')`

### `hidden_tests/test_hidden_behavior.py::test_fixture_lookup_error_lists_available`

- mapping: `B001, B002, B005`
- API: `featurelifted.FixtureDef, featurelifted.FixtureLookupError, featurelifted.FixtureRegistry, featurelifted.resolve_fixture_closure`
- risk: `exception_semantics`
- A001 `assert` L33: `'alpha' in arg2defs`
- A002 `raises` L35: `pytest.raises(FixtureLookupError)`
- A003 `assert` L38: `'missing' in str(excinfo.value)`
- A004 `assert` L39: `'alpha' in str(excinfo.value)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.FixtureDef, featurelifted.FixtureLookupError, featurelifted.FixtureRegistry, featurelifted.deduplicate_names, featurelifted.fixture, featurelifted.getfixturemarker, featurelifted.resolve_fixture_closure`
- risk: `none`
- A001 `assert` L15: `isinstance(FixtureDef, type)`
- A002 `assert` L16: `issubclass(FixtureLookupError, BaseException)`
- A003 `assert` L17: `isinstance(FixtureRegistry, type)`
- A004 `assert` L18: `hasattr(FixtureRegistry, 'register')`
- A005 `assert` L19: `callable(deduplicate_names)`
- A006 `assert` L20: `callable(fixture)`
- A007 `assert` L21: `callable(getfixturemarker)`
- A008 `assert` L22: `callable(resolve_fixture_closure)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pytest, _pytest`
- source entrypoints: `_pytest.fixtures.getfixturemarker, _pytest.fixtures.FixtureManager.getfixtureclosure, _pytest.fixtures.FixtureManager.getfixturedefs, _pytest.fixtures.deduplicate_names, _pytest.fixtures.FixtureLookupError`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Fixture name resolution subset: closure, registry lookup, deduplication, and marker helpers.
