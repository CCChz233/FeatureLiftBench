# semver__version_core__001

- release: `external50`
- lift: `Direct`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `9/24`

## Required API

- `featurelifted.Version` (class) `(major: int, minor: int = 0, patch: int = 0, prerelease: str | None = None, build: str | None = None)`
- `featurelifted.Version.parse` (method) `(version: str) -> Version`
- `featurelifted.Version.compare` (method) `(self, other: Version) -> int`
- `featurelifted.Version.bump_major` (method) `(self) -> Version`
- `featurelifted.Version.bump_minor` (method) `(self) -> Version`
- `featurelifted.Version.bump_patch` (method) `(self) -> Version`
- `featurelifted.Version.replace` (method) `(self, **parts) -> Version`
- `featurelifted.Version.major` (attribute)
- `featurelifted.Version.minor` (attribute)
- `featurelifted.Version.patch` (attribute)
- `featurelifted.Version.prerelease` (attribute)
- `featurelifted.Version.build` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse semver strings into Version. Required observable cases include parse basic; prerelease and build parse.
- **B002**: The extracted feature must support this observable behavior: compare and order Version instances. Required observable cases include compare and order; ordering operators.
- **B003**: The extracted feature must support this observable behavior: bump major/minor/patch and replace parts. Required observable cases include bump and replace; constructor defaults.
- **B004**: Invalid version strings raise ValueError.
- **B005**: The package exposes the required task API paths `featurelifted.Version`, `featurelifted.Version.parse`, `featurelifted.Version.compare`, `featurelifted.Version.bump_major`, `featurelifted.Version.bump_minor`, `featurelifted.Version.bump_patch`, `featurelifted.Version.replace` with the kinds and callable signatures listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: semver.

## Tests

### `public_tests/test_public_api.py::test_parse_basic`

- mapping: `B001`
- API: `featurelifted.Version, featurelifted.Version.parse`
- risk: `exact_error_text`
- A001 `assert` L8: `str(v) == '1.2.3'`
- A002 `assert` L9: `v.major == 1 and v.minor == 2 and (v.patch == 3)`

### `public_tests/test_public_api.py::test_compare_and_order`

- mapping: `B002`
- API: `featurelifted.Version, featurelifted.Version.parse`
- risk: `ordering_semantics`
- A001 `assert` L15: `a.compare(b) == -1`
- A002 `assert` L16: `a < b`
- A003 `assert` L17: `a != b`

### `public_tests/test_public_api.py::test_bump_and_replace`

- mapping: `B003`
- API: `featurelifted.Version, featurelifted.Version.parse`
- risk: `exact_error_text`
- A001 `assert` L22: `str(v.bump_major()) == '2.0.0'`
- A002 `assert` L23: `str(v.bump_minor()) == '1.3.0'`
- A003 `assert` L24: `str(v.bump_patch()) == '1.2.4'`
- A004 `assert` L25: `str(v.replace(prerelease='rc.1')) == '1.2.3-rc.1'`

### `hidden_tests/test_hidden_behavior.py::test_prerelease_and_build_parse`

- mapping: `B001`
- API: `featurelifted.Version, featurelifted.Version.parse`
- risk: `exact_error_text`
- A001 `assert` L12: `v.prerelease == 'alpha.1'`
- A002 `assert` L13: `v.build == 'build.7'`
- A003 `assert` L14: `str(v) == '1.0.0-alpha.1+build.7'`

### `hidden_tests/test_hidden_behavior.py::test_invalid_version_raises`

- mapping: `B002`
- API: `featurelifted.Version, featurelifted.Version.parse`
- risk: `exception_semantics`
- A001 `raises` L18: `pytest.raises(ValueError)`

### `hidden_tests/test_hidden_behavior.py::test_constructor_defaults`

- mapping: `B003`
- API: `featurelifted.Version`
- risk: `exact_error_text`
- A001 `assert` L24: `str(v) == '2.0.0'`

### `hidden_tests/test_hidden_behavior.py::test_ordering_operators`

- mapping: `B004`
- API: `featurelifted.Version, featurelifted.Version.parse`
- risk: `ordering_semantics`
- A001 `assert` L28: `Version.parse('1.0.0') <= Version.parse('1.0.0')`
- A002 `assert` L29: `Version.parse('2.0.0') >= Version.parse('1.9.9')`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L38: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Version, featurelifted.Version.bump_major, featurelifted.Version.bump_minor, featurelifted.Version.bump_patch, featurelifted.Version.compare, featurelifted.Version.parse, featurelifted.Version.replace`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'Version')`
- A002 `assert` L6: `callable(featurelifted.Version.parse)`
- A003 `assert` L7: `callable(featurelifted.Version.compare)`
- A004 `assert` L8: `callable(featurelifted.Version.bump_major)`
- A005 `assert` L9: `callable(featurelifted.Version.bump_minor)`
- A006 `assert` L10: `callable(featurelifted.Version.bump_patch)`
- A007 `assert` L11: `callable(featurelifted.Version.replace)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `semver`
- source entrypoints: `none`
- oracle source files: `src/semver/version.py, src/semver/__init__.py`
- runtime dependencies: `none`
- oracle notes: Direct extract of Version parse/compare/bump/replace.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
