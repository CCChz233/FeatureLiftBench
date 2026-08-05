# strictyaml__schema_load_core__001

- release: `external50`
- lift: `Composite`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `8/10`

## Required API

- `featurelifted.load` (function) `(yaml_string, schema, label='string')`
- `featurelifted.Map` (class)
- `featurelifted.Seq` (class)
- `featurelifted.Str` (class)
- `featurelifted.Int` (class)
- `featurelifted.Bool` (class)
- `featurelifted.Optional` (class)
- `featurelifted.MapPattern` (class)
- `featurelifted.YAMLValidationError` (class)
- `featurelifted.StrictYAMLError` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: load Map/Seq/Bool schemas to .data primitives. Required observable cases include load map seq.
- **B002**: The extracted feature must support this observable behavior: YAMLValidationError on type mismatch. Required observable cases include validation error.
- **B003**: The extracted feature must support this observable behavior: Optional keys and MapPattern. Required observable cases include optional key absent; map pattern.
- **B004**: YAMLValidationError is a StrictYAMLError subclass.
- **B005**: The package exposes load and declared validators/errors with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: strictyaml.

## Tests

### `public_tests/test_public_api.py::test_load_map_seq`

- mapping: `B001`
- API: `featurelifted.Bool, featurelifted.Int, featurelifted.Map, featurelifted.Optional, featurelifted.Seq, featurelifted.Str, featurelifted.load`
- risk: `none`
- A001 `assert` L27: `doc.data == {'name': 'Ada', 'age': 3, 'tags': ['a', 'b'], 'enabled': True}`

### `public_tests/test_public_api.py::test_validation_error`

- mapping: `B002`
- API: `featurelifted.Int, featurelifted.Map, featurelifted.Str, featurelifted.YAMLValidationError, featurelifted.load`
- risk: `none`
- A001 `assert` L33: `False`

### `public_tests/test_public_api.py::test_map_pattern`

- mapping: `B003`
- API: `featurelifted.Int, featurelifted.MapPattern, featurelifted.Str, featurelifted.load`
- risk: `none`
- A001 `assert` L40: `doc.data == {'a': 1, 'b': 2}`

### `hidden_tests/test_hidden_behavior.py::test_optional_key_absent`

- mapping: `B001, B004`
- API: `featurelifted.Map, featurelifted.Optional, featurelifted.Str, featurelifted.load`
- risk: `none`
- A001 `assert` L12: `doc.data == {'name': 'Ada'}`

### `hidden_tests/test_hidden_behavior.py::test_nested_seq_map`

- mapping: `B002`
- API: `featurelifted.Int, featurelifted.Map, featurelifted.Seq, featurelifted.Str, featurelifted.load`
- risk: `none`
- A001 `assert` L19: `items[1]['label'] == 'b'`

### `hidden_tests/test_hidden_behavior.py::test_strict_error_hierarchy`

- mapping: `B003`
- API: `featurelifted.StrictYAMLError, featurelifted.YAMLValidationError`
- risk: `none`
- A001 `assert` L23: `issubclass(YAMLValidationError, StrictYAMLError)`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L32: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Bool, featurelifted.Int, featurelifted.Map, featurelifted.MapPattern, featurelifted.Optional, featurelifted.Seq, featurelifted.Str, featurelifted.StrictYAMLError, featurelifted.YAMLValidationError, featurelifted.load`
- risk: `none`
- A001 `assert` L16: `callable(load)`
- A002 `assert` L17: `all((x is not None for x in (Map, Seq, Str, Int, Bool, Optional, MapPattern)))`
- A003 `assert` L18: `YAMLValidationError is not None and StrictYAMLError is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `python-dateutil, six`
- forbidden imports: `strictyaml`
- source entrypoints: `none`
- oracle source files: `strictyaml/parser.py, strictyaml/compound.py, strictyaml/scalar.py`
- runtime dependencies: `python-dateutil, six`
- oracle notes: Composite load + Map/Seq/scalar validators; ruamel vendored inside package.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
