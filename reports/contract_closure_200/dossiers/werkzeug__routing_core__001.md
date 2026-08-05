# werkzeug__routing_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/16`

## Required API

- `featurelifted.routing` (module)
- `featurelifted.routing.Map` (class) `(rules: 't.Iterable[RuleFactory] | None' = None, default_subdomain: 'str' = '', strict_slashes: 'bool' = True, merge_slashes: 'bool' = True, redirect_defaults: 'bool' = True, converters: 't.Mapping[str, type[BaseConverter]] | None' = None, sort_parameters: 'bool' = False, sort_key: 't.Callable[[t.Any], t.Any] | None' = None, host_matching: 'bool' = False) -> 'None'`
- `featurelifted.routing.Map.bind` (method) `(self, server_name: 'str', script_name: 'str | None' = None, subdomain: 'str | None' = None, url_scheme: 'str' = 'http', default_method: 'str' = 'GET', path_info: 'str | None' = None, query_args: 't.Mapping[str, t.Any] | str | None' = None) -> 'MapAdapter'`
- `featurelifted.routing.Rule` (class) `(string: 'str', defaults: 't.Mapping[str, t.Any] | None' = None, subdomain: 'str | None' = None, methods: 't.Iterable[str] | None' = None, build_only: 'bool' = False, endpoint: 't.Any | None' = None, strict_slashes: 'bool | None' = None, merge_slashes: 'bool | None' = None, redirect_to: 'str | t.Callable[..., str] | None' = None, alias: 'bool' = False, host: 'str | None' = None, websocket: 'bool' = False) -> 'None'`
- `featurelifted.routing.Subdomain` (class) `(subdomain: 'str', rules: 't.Iterable[RuleFactory]') -> 'None'`
- `featurelifted.routing.Submount` (class) `(path: 'str', rules: 't.Iterable[RuleFactory]') -> 'None'`
- `featurelifted.routing.exceptions` (module)
- `featurelifted.routing.exceptions.RequestRedirect` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: define URL rules with converters and HTTP methods. Required observable cases include subdomain and submount routing.
- **B002**: The extracted feature must support this observable behavior: match paths to endpoints with argument extraction. Required observable cases include match and build simple rules; subdomain and submount routing.
- **B003**: The extracted feature must support this observable behavior: build URLs from endpoints and arguments. Required observable cases include match and build simple rules; subdomain and submount routing.
- **B004**: The extracted feature must support this observable behavior: subdomain and submount rule factories. Required observable cases include subdomain and submount routing.
- **B005**: The extracted feature must support this observable behavior: redirect and alias redirect exceptions on match. Required observable cases include strict slashes redirect.
- **B006**: The package exposes the required task API paths `featurelifted.routing`, `featurelifted.routing.Map`, `featurelifted.routing.Map.bind`, `featurelifted.routing.Rule`, `featurelifted.routing.Subdomain`, `featurelifted.routing.Submount`, `featurelifted.routing.exceptions`, `featurelifted.routing.exceptions.RequestRedirect` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_match_and_build_simple_rules`

- mapping: `B002, B003`
- API: `featurelifted.routing`
- risk: `none`
- A001 `assert` L14: `adapter.match('/') == ('index', {})`
- A002 `assert` L15: `adapter.match('/users/42') == ('user', {'user_id': 42})`
- A003 `assert` L16: `adapter.build('user', {'user_id': 7}) == '/users/7'`

### `hidden_tests/test_hidden_behavior.py::test_subdomain_and_submount_routing`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.routing, featurelifted.routing.exceptions`
- risk: `none`
- A001 `assert` L24: `api.match('/v1/status') == ('api_status', {})`
- A002 `assert` L27: `www.match('/blog/') == ('blog_index', {})`
- A003 `assert` L28: `www.match('/blog/hello-world') == ('blog_post', {'slug': 'hello-world'})`

### `hidden_tests/test_hidden_behavior.py::test_strict_slashes_redirect`

- mapping: `B005`
- API: `featurelifted.routing, featurelifted.routing.exceptions`
- risk: `exception_semantics`
- A001 `raises` L34: `pytest.raises(RequestRedirect)`
- A002 `assert` L36: `exc.value.new_url.endswith('/about/')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.routing, featurelifted.routing.exceptions`
- risk: `none`
- A001 `assert` L11: `routing is not None`
- A002 `assert` L12: `isinstance(getattr(routing, 'Map'), type)`
- A003 `assert` L13: `hasattr(getattr(routing, 'Map'), 'bind')`
- A004 `assert` L14: `isinstance(getattr(routing, 'Rule'), type)`
- A005 `assert` L15: `isinstance(getattr(routing, 'Subdomain'), type)`
- A006 `assert` L16: `isinstance(getattr(routing, 'Submount'), type)`
- A007 `assert` L17: `getattr(routing, 'exceptions') is not None`
- A008 `assert` L18: `issubclass(getattr(getattr(routing, 'exceptions'), 'RequestRedirect'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `werkzeug`
- source entrypoints: `werkzeug.routing.Map, werkzeug.routing.Rule, werkzeug.routing.MapAdapter, werkzeug.routing.Subdomain, werkzeug.routing.Submount`
- oracle source files: `none`
- runtime dependencies: `none`
