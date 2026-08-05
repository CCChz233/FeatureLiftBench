# flask_cors__cors_options_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `framework_coupling`
- strict validation: `PASS`
- tests/assertions: `5/7`

## Required API

- `featurelifted.CORS` (class) `(app=None, **options)`
- `featurelifted.cross_origin` (function) `(**options)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: CORS(app) reflects Origin on GET responses. Required observable cases include cors app headers.
- **B002**: The extracted feature must support this observable behavior: cross_origin decorator sets per-route ACAO. Required observable cases include cross origin decorator.
- **B003**: The extracted feature must support this observable behavior: OPTIONS preflight exposes allowed methods. Required observable cases include options preflight.
- **B004**: Tests use Flask test client only; Flask is an allowed dependency.
- **B005**: The package exposes CORS and cross_origin with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: flask_cors.

## Tests

### `public_tests/test_public_api.py::test_cors_app_headers`

- mapping: `B001`
- API: `featurelifted.CORS`
- risk: `none`
- A001 `assert` L18: `resp.status_code == 200`
- A002 `assert` L19: `resp.headers.get('Access-Control-Allow-Origin') in ('http://example.com', '*')`

### `public_tests/test_public_api.py::test_cross_origin_decorator`

- mapping: `B002`
- API: `featurelifted.cross_origin`
- risk: `none`
- A001 `assert` L35: `resp.headers.get('Access-Control-Allow-Origin') == 'https://a.test'`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_options_preflight`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.CORS`
- risk: `filesystem_resource`
- A001 `assert` L38: `resp.status_code in {200, 204}`
- A002 `assert` L39: `'Access-Control-Allow-Methods' in resp.headers`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.CORS, featurelifted.cross_origin`
- risk: `none`
- A001 `assert` L5: `CORS is not None and callable(cross_origin)`

## Dependency / Oracle Evidence

- allowed dependencies: `blinker, click, flask, itsdangerous, jinja2, markupsafe, six, werkzeug`
- forbidden imports: `flask_cors`
- source entrypoints: `none`
- oracle source files: `flask_cors/flask_cors.py`
- runtime dependencies: `blinker, click, flask, itsdangerous, jinja2, markupsafe, six, werkzeug`
- oracle notes: Single-file flask_cors adapted as featurelifted; Flask test client only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
