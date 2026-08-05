# distlib__wheel_metadata_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/10`

## Required API

- `featurelifted.to_posix` (function) `(path: 'str') -> 'str'`
- `featurelifted.normalize_record_path` (function) `(path: 'str') -> 'str'`
- `featurelifted.parse_record` (function) `(content: 'str') -> 'list[tuple[str, str | None, int | None]]'`
- `featurelifted.validate_record_hash` (function) `(path: 'str', digest: 'str | None') -> 'bool'`

## Public Behaviors

- **B001**: `parse_record` parses CSV RECORD rows into `(path, digest, size)` tuples.
- **B002**: `normalize_record_path` applies posix normalization and strips `./` prefixes.
- **B003**: When validate_record_hash receives file bytes and a RECORD digest, it accepts matching supported hashes and rejects malformed or mismatched digests.
- **B004**: The package exposes the required task API paths `featurelifted.to_posix`, `featurelifted.normalize_record_path`, `featurelifted.parse_record`, `featurelifted.validate_record_hash` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_parse_record_row`

- mapping: `B001`
- API: `featurelifted.parse_record`
- risk: `none`
- A001 `assert` L7: `rows[0][0] == 'pkg/__init__.py'`

### `hidden_tests/test_hidden_contract.py::test_to_posix_converts_separators`

- mapping: `B004`
- API: `featurelifted.to_posix`
- risk: `none`
- A001 `assert` L6: `'/' in to_posix('a\\b\\c') or to_posix('a/b/c') == 'a/b/c'`

### `hidden_tests/test_hidden_contract.py::test_normalize_record_path_strips_dot_prefix`

- mapping: `B001, B002`
- API: `featurelifted.normalize_record_path`
- risk: `filesystem_resource`
- A001 `assert` L10: `normalize_record_path('./pkg/file.py') == 'pkg/file.py'`

### `hidden_tests/test_hidden_contract.py::test_parse_record_handles_missing_hash_and_size`

- mapping: `B001, B003`
- API: `featurelifted.parse_record`
- risk: `none`
- A001 `assert` L15: `rows[0] == ('README.txt', None, None)`

### `hidden_tests/test_hidden_contract.py::test_validate_record_hash`

- mapping: `B001, B003`
- API: `featurelifted.validate_record_hash`
- risk: `none`
- A001 `assert` L20: `validate_record_hash('pkg/file.py', digest) is True`
- A002 `assert` L21: `validate_record_hash('pkg/file.py', 'bad') is False`

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
- oracle notes: Wheel RECORD parsing subset without installer runtime.
