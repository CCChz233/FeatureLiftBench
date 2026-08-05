# jsonpickle__handler_roundtrip_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `5/7`

## Required API

- `featurelifted.encode` (function)
- `featurelifted.decode` (function)
- `featurelifted.register` (function)
- `featurelifted.handlers.BaseHandler` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: encode/decode roundtrip for dict payloads. Required observable cases include encode decode builtin.
- **B002**: The extracted feature must support this observable behavior: register BaseHandler restores custom classes. Required observable cases include custom handler roundtrip.
- **B003**: The extracted feature must support this observable behavior: unpicklable=False yields dict snapshots. Required observable cases include unpicklable false dict mode.
- **B004**: Handler registry is global; tests register handlers explicitly.
- **B005**: The package exposes encode/decode/register/BaseHandler with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: jsonpickle.

## Tests

### `public_tests/test_public_api.py::test_encode_decode_builtin`

- mapping: `B001`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.handlers`
- risk: `none`
- A001 `assert` L25: `decode(encode(payload)) == payload`

### `public_tests/test_public_api.py::test_custom_handler_roundtrip`

- mapping: `B002`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.handlers, featurelifted.register`
- risk: `none`
- A001 `assert` L32: `isinstance(restored, Point)`
- A002 `assert` L33: `restored.x == 3 and restored.y == 4`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_unpicklable_false_dict_mode`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.decode, featurelifted.encode`
- risk: `none`
- A001 `assert` L26: `data['name'] == 'Ada'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.decode, featurelifted.encode, featurelifted.handlers, featurelifted.register`
- risk: `none`
- A001 `assert` L6: `callable(encode) and callable(decode) and callable(register)`
- A002 `assert` L7: `BaseHandler is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `jsonpickle`
- source entrypoints: `none`
- oracle source files: `jsonpickle/pickler.py, jsonpickle/unpickler.py, jsonpickle/handlers.py`
- runtime dependencies: `none`
- oracle notes: Adapted encode/decode with custom handler registration.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
