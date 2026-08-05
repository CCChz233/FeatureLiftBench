# fsspec__url_chain_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/10`

## Required API

- `featurelifted.ProtocolRegistry` (class) `() -> 'None'`
- `featurelifted.url_to_fs` (function) `(url: 'str', registry: 'ProtocolRegistry') -> 'tuple[str, str, dict[str, Any]]'`
- `featurelifted.UnknownProtocolError` (exception)

## Public Behaviors

- **B001**: `ProtocolRegistry` resolves protocol names and aliases.
- **B002**: `url_to_fs` parses chained URLs and merges query/storage options.
- **B003**: Unknown protocols raise `UnknownProtocolError`.
- **B004**: The package exposes the required task API paths `featurelifted.ProtocolRegistry`, `featurelifted.url_to_fs`, `featurelifted.UnknownProtocolError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_simple_file_url`

- mapping: `B002`
- API: `featurelifted.ProtocolRegistry, featurelifted.url_to_fs`
- risk: `none`
- A001 `assert` L8: `protocol == 'file'`
- A002 `assert` L9: `path == '/tmp/data.txt'`

### `hidden_tests/test_hidden_contract.py::test_chained_zip_file_url`

- mapping: `B002`
- API: `featurelifted.ProtocolRegistry, featurelifted.url_to_fs`
- risk: `none`
- A001 `assert` L10: `protocol == 'zip'`
- A002 `assert` L11: `options['target_protocol'] == 'file'`

### `hidden_tests/test_hidden_contract.py::test_storage_options_query`

- mapping: `B003`
- API: `featurelifted.ProtocolRegistry, featurelifted.url_to_fs`
- risk: `none`
- A001 `assert` L17: `protocol == 'memory'`
- A002 `assert` L18: `options['anon'] == 'true'`

### `hidden_tests/test_hidden_contract.py::test_unknown_protocol_raises`

- mapping: `B001`
- API: `featurelifted.ProtocolRegistry, featurelifted.UnknownProtocolError, featurelifted.url_to_fs`
- risk: `exception_semantics`
- A001 `raises` L23: `pytest.raises(UnknownProtocolError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.ProtocolRegistry, featurelifted.UnknownProtocolError, featurelifted.url_to_fs`
- risk: `none`
- A001 `assert` L11: `isinstance(ProtocolRegistry, type)`
- A002 `assert` L12: `callable(url_to_fs)`
- A003 `assert` L13: `issubclass(UnknownProtocolError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `fsspec`
- source entrypoints: `fsspec.core.url_to_fs`
- oracle source files: `repo/fsspec/core.py, repo/fsspec/registry.py`
- runtime dependencies: `none`
- oracle notes: URL chain resolver without filesystem implementations.
