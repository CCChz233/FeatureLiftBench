# python_json_logger__json_formatter_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `config_environment_coupling`
- strict validation: `PASS`
- tests/assertions: `5/9`

## Required API

- `featurelifted.JsonFormatter` (class)
- `featurelifted.JsonFormatter.format` (method)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: format LogRecord to JSON. Required observable cases include basic json line.
- **B002**: The extracted feature must support this observable behavior: rename_fields and static_fields. Required observable cases include rename and static fields.
- **B003**: The extracted feature must support this observable behavior: custom fmt and json submodule import. Required observable cases include custom fmt fields; from json submodule.
- **B004**: Output is a single JSON object line per record.
- **B005**: The package exposes JsonFormatter with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: pythonjsonlogger.

## Tests

### `public_tests/test_public_api.py::test_basic_json_line`

- mapping: `B001`
- API: `featurelifted.JsonFormatter`
- risk: `none`
- A001 `assert` L13: `payload['message'] == 'hello'`
- A002 `assert` L14: `payload['levelname'] == 'INFO'`

### `public_tests/test_public_api.py::test_rename_and_static_fields`

- mapping: `B002`
- API: `featurelifted.JsonFormatter`
- risk: `none`
- A001 `assert` L25: `payload['level'] == 'WARNING'`
- A002 `assert` L26: `payload['app'] == 'svc'`
- A003 `assert` L27: `'levelname' not in payload`

### `hidden_tests/test_hidden_behavior.py::test_custom_fmt_fields`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.JsonFormatter`
- risk: `none`
- A001 `assert` L13: `payload['message'] == 'boom'`
- A002 `assert` L14: `payload['name'] == 'worker'`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L28: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.JsonFormatter`
- risk: `none`
- A001 `assert` L5: `JsonFormatter is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pythonjsonlogger`
- source entrypoints: `none`
- oracle source files: `src/pythonjsonlogger/json.py`
- runtime dependencies: `none`
- oracle notes: Adapted JsonFormatter from pythonjsonlogger.json.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
