# fs__url_opener_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/14`

## Required API

- `featurelifted.parse_fs_url` (function) `(fs_url: 'str') -> 'tuple[str, str | None, dict[str, str]]'`
- `featurelifted.FSOpenerRegistry` (class) `(default_protocol: 'str' = 'osfs') -> 'None'`
- `featurelifted.FSOpenerRegistry.open` (method) `(self, fs_url: 'str') -> 'tuple[Any, str | None]'`
- `featurelifted.FSOpenerRegistry.register` (method) `(self, protocol: 'str', factory: 'Callable[[dict[str, str]], Any] | None' = None)`
- `featurelifted.ParseError` (exception)
- `featurelifted.UnsupportedProtocolError` (exception)
- `featurelifted.normalize_fs_path` (function) `(path: 'str | None') -> 'str | None'`

## Public Behaviors

- **B001**: `parse_fs_url` parses `scheme://resource!path` URLs and query parameters.
- **B002**: `FSOpenerRegistry` registers opener factories and opens URLs.
- **B003**: Invalid URLs raise `ParseError`; unknown schemes raise `UnsupportedProtocolError`.
- **B004**: The package exposes the required task API paths `featurelifted.parse_fs_url`, `featurelifted.FSOpenerRegistry`, `featurelifted.FSOpenerRegistry.open`, `featurelifted.FSOpenerRegistry.register`, `featurelifted.ParseError`, `featurelifted.UnsupportedProtocolError`, `featurelifted.normalize_fs_path` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_parse_fs_url_and_open`

- mapping: `B001`
- API: `featurelifted.FSOpenerRegistry, featurelifted.parse_fs_url`
- risk: `filesystem_resource`
- A001 `assert` L7: `scheme == 'mem'`
- A002 `assert` L8: `params['readonly'] == 'true'`
- A003 `assert` L17: `fs['params']['readonly'] == 'true'`
- A004 `assert` L18: `subpath is None`

### `hidden_tests/test_hidden_contract.py::test_default_protocol_injection`

- mapping: `B001, B002`
- API: `featurelifted.FSOpenerRegistry`
- risk: `filesystem_resource`
- A001 `assert` L15: `path is None`

### `hidden_tests/test_hidden_contract.py::test_unknown_protocol_raises`

- mapping: `B002`
- API: `featurelifted.FSOpenerRegistry, featurelifted.UnsupportedProtocolError`
- risk: `exception_semantics, filesystem_resource`
- A001 `raises` L20: `pytest.raises(UnsupportedProtocolError)`

### `hidden_tests/test_hidden_contract.py::test_invalid_path_control_characters`

- mapping: `B003`
- API: `featurelifted.normalize_fs_path`
- risk: `exception_semantics, filesystem_resource`
- A001 `raises` L25: `pytest.raises(__import__('featurelifted').InvalidPathError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.FSOpenerRegistry, featurelifted.ParseError, featurelifted.UnsupportedProtocolError, featurelifted.normalize_fs_path, featurelifted.parse_fs_url`
- risk: `none`
- A001 `assert` L13: `callable(parse_fs_url)`
- A002 `assert` L14: `isinstance(FSOpenerRegistry, type)`
- A003 `assert` L15: `hasattr(FSOpenerRegistry, 'open')`
- A004 `assert` L16: `hasattr(FSOpenerRegistry, 'register')`
- A005 `assert` L17: `issubclass(ParseError, BaseException)`
- A006 `assert` L18: `issubclass(UnsupportedProtocolError, BaseException)`
- A007 `assert` L19: `callable(normalize_fs_path)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `fs`
- source entrypoints: `fs.opener.parse.parse_fs_url, fs.opener.registry.FSOpenerRegistry`
- oracle source files: `repo/fs/opener/parse.py, repo/fs/opener/registry.py`
- runtime dependencies: `none`
- oracle notes: FS URL opener subset without real backends.
