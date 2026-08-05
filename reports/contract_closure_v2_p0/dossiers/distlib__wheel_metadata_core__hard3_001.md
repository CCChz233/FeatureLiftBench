# Contract V2 P0: distlib__wheel_metadata_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/14`

## Required API

- `featurelifted.to_posix` (function) `(path: 'str') -> 'str'`
- `featurelifted.normalize_record_path` (function) `(path: 'str') -> 'str'`
- `featurelifted.parse_record` (function) `(content: 'str') -> 'list[tuple[str, str | None, int | None]]'`
- `featurelifted.validate_record_hash` (function) `(path: 'str', digest: 'str | None') -> 'bool'`

## Public Behaviors

- **B001**: parse_record uses CSV quoting rules and returns complete (normalized path, digest or None, integer size or None) tuples in input order.
- **B002**: to_posix deterministically converts backslashes to forward slashes on every host, and normalize_record_path removes redundant dot segments and leading ./ prefixes.
- **B003**: validate_record_hash validates an optional RECORD sha256 digest field syntactically; it does not read file content or claim content-hash verification.
- **B004**: The package exposes the required task API paths `featurelifted.to_posix`, `featurelifted.normalize_record_path`, `featurelifted.parse_record`, `featurelifted.validate_record_hash` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_parse_record_row`

- mapping: `B001`
- API: `featurelifted.parse_record`
- risk: `none`
- A001 `assert` L7: `rows[0][0] == 'pkg/__init__.py'`

### `hidden_tests/test_hidden_contract.py::test_to_posix_converts_separators`

- mapping: `B002`
- API: `featurelifted.to_posix`
- risk: `none`
- A001 `assert` L5: `to_posix('a\\b\\c') == 'a/b/c'`
- A002 `assert` L6: `to_posix('a/b/c') == 'a/b/c'`

### `hidden_tests/test_hidden_contract.py::test_normalize_record_path_strips_dot_prefix`

- mapping: `B002`
- API: `featurelifted.normalize_record_path`
- risk: `filesystem_resource`
- A001 `assert` L10: `normalize_record_path('./pkg/../pkg/file.py') == 'pkg/file.py'`

### `hidden_tests/test_hidden_contract.py::test_parse_record_handles_missing_hash_and_size`

- mapping: `B001`
- API: `featurelifted.parse_record`
- risk: `none`
- A001 `assert` L15: `rows == [('pkg,data/file.txt', 'sha256=abc', 12), ('README.txt', None, None)]`

### `hidden_tests/test_hidden_contract.py::test_validate_record_hash`

- mapping: `B003`
- API: `featurelifted.validate_record_hash`
- risk: `none`
- A001 `assert` L23: `validate_record_hash('pkg/file.py', digest) is True`
- A002 `assert` L24: `validate_record_hash('pkg/file.py', None) is True`
- A003 `assert` L25: `validate_record_hash('pkg/file.py', 'sha256=' + 'a' * 63) is False`
- A004 `assert` L26: `validate_record_hash('pkg/file.py', 'sha512=' + 'a' * 64) is False`
- A005 `assert` L27: `validate_record_hash('pkg/file.py', 'bad') is False`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.normalize_record_path, featurelifted.parse_record, featurelifted.to_posix, featurelifted.validate_record_hash`
- risk: `none`
- A001 `assert` L12: `callable(to_posix)`
- A002 `assert` L13: `callable(normalize_record_path)`
- A003 `assert` L14: `callable(parse_record)`
- A004 `assert` L15: `callable(validate_record_hash)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `distlib`
- source entrypoints: `distlib.wheel, distlib.resources`
- oracle source files: `repo/distlib/wheel.py, repo/distlib/resources.py, repo/distlib/util.py`
- runtime dependencies: `none`
- oracle notes: Adapted Wheel RECORD parser. validate_record_hash validates digest syntax only; it does not read path content. to_posix treats both slash styles deterministically.
