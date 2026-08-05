# pyyaml__safe_load_dump__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `7/18`

## Required API

- `featurelifted.safe_load` (function) `(stream)`
- `featurelifted.safe_load_all` (function) `(stream)`
- `featurelifted.safe_dump` (function) `(data, stream=None, **kwds)`
- `featurelifted.safe_dump_all` (function) `(documents, stream=None, **kwds)`
- `featurelifted.YAMLError` (exception)
- `featurelifted.constructor` (module)
- `featurelifted.constructor.ConstructorError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse mappings, sequences, scalars, booleans, nulls, integers, floats, and nested documents. Required observable cases include safe load basic mapping sequence and scalars; unicode scalar and timestamp tag.
- **B002**: The extracted feature must support this observable behavior: support anchors, aliases, and merge keys with SafeLoader semantics. Required observable cases include anchors aliases merge keys and dates.
- **B003**: The extracted feature must support this observable behavior: dump plain Python data through SafeDumper with deterministic sort_keys behavior. Required observable cases include safe dump sort keys output; parse errors and flow style dumping.
- **B004**: The extracted feature must support this observable behavior: load and dump multi-document streams. Required observable cases include multi document dump load and unsafe tags rejected; parse errors and flow style dumping.
- **B005**: The extracted feature must support this observable behavior: reject unsafe Python object tags under safe_load. Required observable cases include safe load basic mapping sequence and scalars; multi document dump load and unsafe tags rejected; unicode scalar and timestamp tag.
- **B006**: The package exposes the required task API paths `featurelifted.safe_load`, `featurelifted.safe_load_all`, `featurelifted.safe_dump`, `featurelifted.safe_dump_all`, `featurelifted.YAMLError`, `featurelifted.constructor`, `featurelifted.constructor.ConstructorError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_safe_load_basic_mapping_sequence_and_scalars`

- mapping: `B001, B005`
- API: `featurelifted.safe_load`
- risk: `ordering_semantics`
- A001 `assert` L10: `data == {'a': 1, 'b': ['x', 'y'], 'flag': True, 'empty': None}`

### `public_tests/test_public_api.py::test_safe_dump_sort_keys_output`

- mapping: `B003`
- API: `featurelifted.safe_dump`
- risk: `none`
- A001 `assert` L14: `safe_dump({'b': [1, 2], 'a': True}, sort_keys=True) == 'a: true\nb:\n- 1\n- 2\n'`

### `hidden_tests/test_hidden_behavior.py::test_anchors_aliases_merge_keys_and_dates`

- mapping: `B002`
- API: `featurelifted.constructor, featurelifted.safe_load`
- risk: `none`
- A001 `assert` L23: `safe_load(content) == {'defaults': {'retries': 3, 'enabled': True}, 'prod': {'retries': 3, 'enabled': True, 'host': 'example.com'}}`

### `hidden_tests/test_hidden_behavior.py::test_multi_document_dump_load_and_unsafe_tags_rejected`

- mapping: `B004, B005`
- API: `featurelifted.constructor, featurelifted.safe_dump_all, featurelifted.safe_load, featurelifted.safe_load_all`
- risk: `exception_semantics`
- A001 `assert` L31: `docs == [{'a': 1}, {'b': 2}]`
- A002 `assert` L34: `list(safe_load_all(dumped)) == docs`
- A003 `raises` L36: `pytest.raises(ConstructorError)`

### `hidden_tests/test_hidden_behavior.py::test_parse_errors_and_flow_style_dumping`

- mapping: `B003, B004`
- API: `featurelifted.YAMLError, featurelifted.constructor, featurelifted.safe_dump, featurelifted.safe_load`
- risk: `exception_semantics`
- A001 `raises` L41: `pytest.raises(YAMLError)`
- A002 `assert` L44: `safe_dump({'items': [{'x': 1}, {'y': 2}]}, default_flow_style=True) == '{items: [{x: 1}, {y: 2}]}\n'`

### `hidden_tests/test_hidden_behavior.py::test_unicode_scalar_and_timestamp_tag`

- mapping: `B001, B005`
- API: `featurelifted.constructor, featurelifted.safe_dump, featurelifted.safe_load`
- risk: `none`
- A001 `assert` L51: `doc['when'].year == 2020`
- A002 `assert` L52: `doc['emoji'] == '😀'`
- A003 `assert` L54: `roundtrip['emoji'] == '😀'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.YAMLError, featurelifted.constructor, featurelifted.safe_dump, featurelifted.safe_dump_all, featurelifted.safe_load, featurelifted.safe_load_all`
- risk: `none`
- A001 `assert` L14: `callable(safe_load)`
- A002 `assert` L15: `callable(safe_load_all)`
- A003 `assert` L16: `callable(safe_dump)`
- A004 `assert` L17: `callable(safe_dump_all)`
- A005 `assert` L18: `issubclass(YAMLError, BaseException)`
- A006 `assert` L19: `constructor is not None`
- A007 `assert` L20: `issubclass(getattr(constructor, 'ConstructorError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `yaml`
- source entrypoints: `yaml.safe_load, yaml.safe_load_all, yaml.safe_dump, yaml.safe_dump_all, yaml.YAMLError, yaml.constructor.ConstructorError`
- oracle source files: `none`
- runtime dependencies: `none`
