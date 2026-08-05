# uritools__uri_join_normalize_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `9/23`

## Required API

- `featurelifted.urisplit` (function) `(uri: str) -> SplitResult`
- `featurelifted.uriunsplit` (function) `(parts: SplitResult | tuple) -> str`
- `featurelifted.urijoin` (function) `(base: str, ref: str, strict: bool = False) -> str`
- `featurelifted.urinorm` (function) `(uri: str) -> str`
- `featurelifted.uriencode` (function) `(s: str, safe: str = '', encoding: str = 'utf-8') -> str`
- `featurelifted.uridecode` (function) `(s: str, encoding: str = 'utf-8') -> str`
- `featurelifted.SplitResult` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: split/unsplit with SplitResult fields scheme/authority/path/query/fragment. Required observable cases include urisplit fields; split relative ref.
- **B002**: The extracted feature must support this observable behavior: join absolute and relative refs. Required observable cases include urijoin relative; urijoin strict absolute ref.
- **B003**: The extracted feature must support this observable behavior: adapted urinorm path/scheme normalization. Required observable cases include urinorm path dots; urinorm scheme case.
- **B004**: The extracted feature must support this observable behavior: utf-8 percent encode/decode. Required observable cases include encode decode roundtrip.
- **B005**: The package exposes the required task API paths `featurelifted.urisplit`, `featurelifted.uriunsplit`, `featurelifted.urijoin`, `featurelifted.urinorm`, `featurelifted.uriencode`, `featurelifted.uridecode`, `featurelifted.SplitResult` with the kinds and callable signatures listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: uritools.

## Tests

### `public_tests/test_public_api.py::test_urisplit_fields`

- mapping: `B001`
- API: `featurelifted.urisplit, featurelifted.uriunsplit`
- risk: `none`
- A001 `assert` L8: `parts.scheme == 'https'`
- A002 `assert` L9: `parts.authority == 'example.com'`
- A003 `assert` L10: `parts.path == '/a/b'`
- A004 `assert` L11: `parts.query == 'q=1'`
- A005 `assert` L12: `parts.fragment == 'frag'`
- A006 `assert` L13: `uriunsplit(parts) == 'https://example.com/a/b?q=1#frag'`

### `public_tests/test_public_api.py::test_urijoin_relative`

- mapping: `B002`
- API: `featurelifted.urijoin`
- risk: `none`
- A001 `assert` L17: `urijoin('https://example.com/a/', '../b') == 'https://example.com/b'`

### `public_tests/test_public_api.py::test_urinorm_path_dots`

- mapping: `B003`
- API: `featurelifted.urinorm`
- risk: `none`
- A001 `assert` L21: `urinorm('https://example.com/a/./b/../c') == 'https://example.com/a/c'`

### `hidden_tests/test_hidden_behavior.py::test_encode_decode_roundtrip`

- mapping: `B001`
- API: `featurelifted.uridecode, featurelifted.uriencode`
- risk: `none`
- A001 `assert` L15: `'%' in encoded_text`
- A002 `assert` L16: `uridecode(encoded) == '你好'`

### `hidden_tests/test_hidden_behavior.py::test_urijoin_strict_absolute_ref`

- mapping: `B002`
- API: `featurelifted.urijoin`
- risk: `none`
- A001 `assert` L20: `urijoin('https://example.com/a', 'https://other.test/x', strict=True) == 'https://other.test/x'`

### `hidden_tests/test_hidden_behavior.py::test_urinorm_scheme_case`

- mapping: `B003`
- API: `featurelifted.urinorm`
- risk: `none`
- A001 `assert` L25: `out.startswith('http://')`
- A002 `assert` L26: `'/a/b' in out or out.endswith('/a/b')`

### `hidden_tests/test_hidden_behavior.py::test_split_relative_ref`

- mapping: `B004`
- API: `featurelifted.urisplit`
- risk: `none`
- A001 `assert` L31: `parts.scheme is None or parts.scheme == ''`
- A002 `assert` L32: `parts.path == '/rel/path'`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L41: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.SplitResult, featurelifted.uridecode, featurelifted.uriencode, featurelifted.urijoin, featurelifted.urinorm, featurelifted.urisplit, featurelifted.uriunsplit`
- risk: `none`
- A001 `assert` L13: `callable(urisplit)`
- A002 `assert` L14: `callable(uriunsplit)`
- A003 `assert` L15: `callable(urijoin)`
- A004 `assert` L16: `callable(urinorm)`
- A005 `assert` L17: `callable(uriencode)`
- A006 `assert` L18: `callable(uridecode)`
- A007 `assert` L19: `SplitResult is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `uritools`
- source entrypoints: `none`
- oracle source files: `src/uritools/__init__.py`
- runtime dependencies: `none`
- oracle notes: Adapted flat helpers + urinorm via SplitResult getters.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
