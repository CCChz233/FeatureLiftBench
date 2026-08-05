# configupdater__ini_roundtrip_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `config_environment_coupling`
- strict validation: `PASS`
- tests/assertions: `6/12`

## Required API

- `featurelifted.ConfigUpdater` (class)
- `featurelifted.ConfigUpdater.read_string` (method)
- `featurelifted.ConfigUpdater.write` (method) `(fp: TextIO, validate: bool = True)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: read_string and section/option get/set. Required observable cases include read modify write stringio; section option access.
- **B002**: The extracted feature must support this observable behavior: write to StringIO preserves comments and spacing. Required observable cases include add option; multiple sections roundtrip.
- **B003**: Tests use ConfigUpdater.write(StringIO) rather than to_string().
- **B004**: Mutable INI document supports multiple sections.
- **B005**: The package exposes ConfigUpdater with read_string/write with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: configupdater.

## Tests

### `public_tests/test_public_api.py::test_read_modify_write_stringio`

- mapping: `B001`
- API: `featurelifted.ConfigUpdater`
- risk: `none`
- A001 `assert` L18: `cu['app']['name'].value == 'old'`
- A002 `assert` L23: `'# keep this comment' in out`
- A003 `assert` L24: `'name = new' in out`

### `public_tests/test_public_api.py::test_section_option_access`

- mapping: `B002`
- API: `featurelifted.ConfigUpdater`
- risk: `none`
- A001 `assert` L30: `'s' in cu`
- A002 `assert` L31: `cu['s']['key'].value == 'v'`

### `public_tests/test_public_api.py::test_add_option`

- mapping: `B003`
- API: `featurelifted.ConfigUpdater`
- risk: `none`
- A001 `assert` L40: `'b = 2' in buf.getvalue()`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_multiple_sections_roundtrip`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.ConfigUpdater`
- risk: `none`
- A001 `assert` L29: `'# note' in out`
- A002 `assert` L30: `'y = 9' in out`
- A003 `assert` L31: `'[a]' in out and '[b]' in out`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.ConfigUpdater`
- risk: `none`
- A001 `assert` L5: `ConfigUpdater is not None`
- A002 `assert` L7: `hasattr(cu, 'read_string') and hasattr(cu, 'write')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `configupdater`
- source entrypoints: `none`
- oracle source files: `src/configupdater/configupdater.py, src/configupdater/parser.py`
- runtime dependencies: `none`
- oracle notes: Adapted ConfigUpdater read_string + section/option + write(StringIO).
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
