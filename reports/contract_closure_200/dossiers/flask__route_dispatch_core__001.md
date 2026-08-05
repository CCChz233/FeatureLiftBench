# flask__route_dispatch_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/11`

## Required API

- `featurelifted.App` (class) `(name)`
- `featurelifted.App.dispatch` (method) `(self, path, method='GET')`
- `featurelifted.App.errorhandler` (method) `(self, code)`
- `featurelifted.App.route` (method) `(self, rule, methods=None)`
- `featurelifted.Response` (class) `(body: object, status_code: int = 200, headers: dict = <factory>) -> None`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: route decorator registration for static, string, and int path segments. Required observable cases include static and typed routes; method dispatch; string converter and response passthrough; error handlers.
- **B002**: The extracted feature must support this observable behavior: method-aware dispatch with GET default. Required observable cases include static and typed routes; method dispatch; string converter and response passthrough; error handlers.
- **B003**: The extracted feature must support this observable behavior: Response normalization for strings, tuples, and Response values. Required observable cases include static and typed routes; method dispatch; string converter and response passthrough; error handlers.
- **B004**: The extracted feature must support this observable behavior: 404 and 405 error-handler dispatch. Required observable cases include static and typed routes; method dispatch; string converter and response passthrough; error handlers.
- **B005**: The package exposes the required task API paths `featurelifted.App`, `featurelifted.App.dispatch`, `featurelifted.App.errorhandler`, `featurelifted.App.route`, `featurelifted.Response` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_static_and_typed_routes`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.App, featurelifted.Response`
- risk: `none`
- A001 `assert` L9: `app.dispatch('/hello') == Response('hello', 200)`
- A002 `assert` L10: `app.dispatch('/users/7') == Response({'id': 7}, 201)`

### `public_tests/test_public_contract.py::test_method_dispatch`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.App`
- risk: `none`
- A001 `assert` L16: `app.dispatch('/items', 'POST').headers['X-Mode'] == 'write'`
- A002 `assert` L17: `app.dispatch('/items', 'GET').status_code == 405`

### `hidden_tests/test_hidden_contract.py::test_string_converter_and_response_passthrough`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.App, featurelifted.Response`
- risk: `none`
- A001 `assert` L7: `app.dispatch('/greet/ada') == Response('ADA', 202, {'X': '1'})`

### `hidden_tests/test_hidden_contract.py::test_error_handlers`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.App, featurelifted.Response`
- risk: `none`
- A001 `assert` L13: `app.dispatch('/unknown') == Response('missing:404', 418)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.App, featurelifted.Response`
- risk: `none`
- A001 `assert` L10: `isinstance(App, type)`
- A002 `assert` L11: `hasattr(App, 'dispatch')`
- A003 `assert` L12: `hasattr(App, 'errorhandler')`
- A004 `assert` L13: `hasattr(App, 'route')`
- A005 `assert` L14: `isinstance(Response, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `flask`
- source entrypoints: `flask.app.Flask.route, flask.app.Flask.dispatch_request, flask.wrappers.Response`
- oracle source files: `flask.app.Flask.route, flask.app.Flask.dispatch_request, flask.wrappers.Response`
- runtime dependencies: `none`
- oracle notes: Entrypoints are maintainer-private provenance and are never Agent-visible in Main.
- behavior contract lacks a completed review_status
