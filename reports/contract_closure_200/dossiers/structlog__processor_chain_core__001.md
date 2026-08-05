# structlog__processor_chain_core__001

- release: `external50`
- lift: `Composite`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `7/14`

## Required API

- `featurelifted.configure` (function)
- `featurelifted.get_logger` (function)
- `featurelifted.reset_defaults` (function)
- `featurelifted.processors.JSONRenderer` (class)
- `featurelifted.processors.KeyValueRenderer` (class)
- `featurelifted.processors.TimeStamper` (class)
- `featurelifted.processors.add_log_level` (function)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: configure processor chain with JSONRenderer and bind context. Required observable cases include bind and json renderer; key value renderer.
- **B002**: The extracted feature must support this observable behavior: TimeStamper/add_log_level and unbind/new context. Required observable cases include timestamp and unbind; new context.
- **B003**: The extracted feature must support this observable behavior: processors run in configure order. Required observable cases include processor order.
- **B004**: reset_defaults clears global configuration between tests.
- **B005**: The package exposes the required task API paths `featurelifted.configure`, `featurelifted.get_logger`, `featurelifted.reset_defaults`, and the frozen processors with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: structlog.

## Tests

### `public_tests/test_public_api.py::test_bind_and_json_renderer`

- mapping: `B001`
- API: `none detected`
- risk: `none`
- A001 `assert` L35: `entries and '"user": "a"' in entries[0].messages[0]`
- A002 `assert` L36: `'"event": "hello"' in entries[0].messages[0]`

### `public_tests/test_public_api.py::test_key_value_renderer`

- mapping: `B002`
- API: `none detected`
- risk: `none`
- A001 `assert` L48: `'a=2' in sink.messages[0] and 'evt' in sink.messages[0]`

### `hidden_tests/test_hidden_behavior.py::test_timestamp_and_unbind`

- mapping: `B001, B004`
- API: `none detected`
- risk: `none`
- A001 `assert` L34: `'"k": 2' in msg and 'timestamp' in msg and ('"level": "warning"' in msg)`

### `hidden_tests/test_hidden_behavior.py::test_new_context`

- mapping: `B002`
- API: `none detected`
- risk: `none`
- A001 `assert` L47: `'"b": 2' in sink.messages[0] and '"a"' not in sink.messages[0]`

### `hidden_tests/test_hidden_behavior.py::test_processor_order`

- mapping: `B003`
- API: `none detected`
- risk: `ordering_semantics`
- A001 `assert` L68: `seen == ['a', 'b']`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L78: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `none detected`
- risk: `none`
- A001 `assert` L5: `callable(structlog.configure)`
- A002 `assert` L6: `callable(structlog.get_logger)`
- A003 `assert` L7: `callable(structlog.reset_defaults)`
- A004 `assert` L8: `structlog.processors.JSONRenderer is not None`
- A005 `assert` L9: `structlog.processors.KeyValueRenderer is not None`
- A006 `assert` L10: `structlog.processors.TimeStamper is not None`
- A007 `assert` L11: `structlog.processors.add_log_level is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `structlog`
- source entrypoints: `none`
- oracle source files: `src/structlog/_config.py, src/structlog/processors.py, src/structlog/_base.py`
- runtime dependencies: `none`
- oracle notes: Composite configure + processors + BoundLogger.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
