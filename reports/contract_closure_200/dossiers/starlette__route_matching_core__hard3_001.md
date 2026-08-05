# starlette__route_matching_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/16`

## Required API

- `featurelifted.compile_path` (function) `(path: 'str') -> 'tuple[Pattern[str], str, dict[str, Convertor]]'`
- `featurelifted.Route` (class) `(name: 'str', path: 'str', methods: 'list[str]' = <factory>, endpoint: 'Callable[..., Any] | None' = None) -> None`
- `featurelifted.Route.matches` (method) `(self, path: 'str', method: 'str') -> 'tuple[Match, dict[str, Any]]'`
- `featurelifted.Mount` (class) `(path: 'str', routes: 'list[Route]' = <factory>) -> None`
- `featurelifted.Router` (class) `(routes: 'list[Route | Mount] | None' = None) -> 'None'`
- `featurelifted.Router.match` (method) `(self, path: 'str', method: 'str' = 'GET') -> 'tuple[Route | None, dict[str, Any]]'`
- `featurelifted.Router.url_path_for` (method) `(self, route_name: 'str', **path_params: 'Any') -> 'str'`
- `featurelifted.Match` (class) `(*values)`
- `featurelifted.Match.NONE` (attribute)

## Public Behaviors

- **B001**: compile_path builds a matching regex and parameter convertors, and Route distinguishes full, partial, and non-matches for the request path.
- **B002**: compile_path resolves registered convertors for typed path parameters and rejects unknown convertor names.
- **B003**: `Mount` matches child routes under a path prefix.
- **B004**: When url_path_for is called on Route, Mount, or Router, it substitutes required parameters and raises for missing names or parameters.
- **B005**: The package exposes the required task API paths `featurelifted.compile_path`, `featurelifted.Route`, `featurelifted.Route.matches`, `featurelifted.Mount`, `featurelifted.Router`, `featurelifted.Router.match`, `featurelifted.Router.url_path_for`, `featurelifted.Match`, `featurelifted.Match.NONE` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_router_matches_route`

- mapping: `B001, B003`
- API: `featurelifted.Route, featurelifted.Router`
- risk: `none`
- A001 `assert` L8: `route.name == 'item'`
- A002 `assert` L9: `params == {'item_id': 42}`

### `hidden_tests/test_hidden_contract.py::test_mount_prefix_and_url_path_for`

- mapping: `B002, B003, B004`
- API: `featurelifted.Mount, featurelifted.Route, featurelifted.Router`
- risk: `none`
- A001 `assert` L9: `route.name == 'detail'`
- A002 `assert` L10: `params == {'name': 'hello'}`
- A003 `assert` L11: `router.url_path_for('detail', name='hello') == '/api/hello'`

### `hidden_tests/test_hidden_contract.py::test_method_mismatch_returns_no_match`

- mapping: `B001, B003`
- API: `featurelifted.Match, featurelifted.Match.NONE, featurelifted.Route`
- risk: `none`
- A001 `assert` L17: `match is Match.NONE`
- A002 `assert` L18: `params == {}`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Match, featurelifted.Mount, featurelifted.Route, featurelifted.Router, featurelifted.compile_path`
- risk: `none`
- A001 `assert` L13: `callable(compile_path)`
- A002 `assert` L14: `isinstance(Route, type)`
- A003 `assert` L15: `hasattr(Route, 'matches')`
- A004 `assert` L16: `isinstance(Mount, type)`
- A005 `assert` L17: `isinstance(Router, type)`
- A006 `assert` L18: `hasattr(Router, 'match')`
- A007 `assert` L19: `hasattr(Router, 'url_path_for')`
- A008 `assert` L20: `isinstance(Match, type)`
- A009 `assert` L21: `Match is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `starlette`
- source entrypoints: `starlette.routing.Route, starlette.routing.Router`
- oracle source files: `repo/starlette/routing.py, repo/starlette/convertors.py`
- runtime dependencies: `none`
- oracle notes: Route matching subset without ASGI server.
