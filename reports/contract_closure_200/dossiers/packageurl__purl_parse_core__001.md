# packageurl__purl_parse_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `7/14`

## Required API

- `featurelifted.PackageURL` (class)
- `featurelifted.PackageURL.from_string` (method)
- `featurelifted.PackageURL.to_string` (method)
- `featurelifted.PackageURL.type` (attribute)
- `featurelifted.PackageURL.name` (attribute)
- `featurelifted.PackageURL.namespace` (attribute)
- `featurelifted.PackageURL.version` (attribute)
- `featurelifted.PackageURL.from_string` (method)
- `featurelifted.PackageURL.to_string` (method)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: from_string exposes type/namespace/name/version. Required observable cases include from string fields; constructor.
- **B002**: The extracted feature must support this observable behavior: to_string roundtrips canonical purls. Required observable cases include to string roundtrip; qualifiers normalize.
- **B003**: The extracted feature must support this observable behavior: invalid purls raise ValueError. Required observable cases include invalid purl.
- **B004**: Qualifiers are serialized in stable order.
- **B005**: The package exposes PackageURL.from_string/to_string with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: packageurl.

## Tests

### `public_tests/test_public_api.py::test_from_string_fields`

- mapping: `B001`
- API: `featurelifted.PackageURL, featurelifted.PackageURL.from_string`
- risk: `none`
- A001 `assert` L8: `purl.type == 'npm'`
- A002 `assert` L9: `purl.namespace == '@scope'`
- A003 `assert` L10: `purl.name == 'foo'`
- A004 `assert` L11: `purl.version == '1.2.3'`

### `public_tests/test_public_api.py::test_to_string_roundtrip`

- mapping: `B002`
- API: `featurelifted.PackageURL, featurelifted.PackageURL.from_string`
- risk: `none`
- A001 `assert` L17: `purl.to_string() == original`

### `public_tests/test_public_api.py::test_constructor`

- mapping: `B003`
- API: `featurelifted.PackageURL`
- risk: `none`
- A001 `assert` L22: `'pkg:gem/rails@7.0.0' == purl.to_string()`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_qualifiers_normalize`

- mapping: `B001, B002, B004`
- API: `featurelifted.PackageURL, featurelifted.PackageURL.from_string`
- risk: `none`
- A001 `assert` L23: `'arch=x86' in text and 'os=windows' in text`

### `hidden_tests/test_hidden_behavior.py::test_invalid_purl`

- mapping: `B003`
- API: `featurelifted.PackageURL, featurelifted.PackageURL.from_string`
- risk: `exception_semantics`
- A001 `raises` L27: `pytest.raises(ValueError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.PackageURL, featurelifted.PackageURL.from_string, featurelifted.PackageURL.to_string`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'PackageURL')`
- A002 `assert` L6: `callable(featurelifted.PackageURL.from_string)`
- A003 `assert` L7: `callable(featurelifted.PackageURL.to_string)`
- A004 `assert` L8: `callable(featurelifted.PackageURL.from_string)`
- A005 `assert` L9: `callable(featurelifted.PackageURL.to_string)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `packageurl`
- source entrypoints: `none`
- oracle source files: `src/packageurl/__init__.py`
- runtime dependencies: `none`
- oracle notes: Adapted PackageURL.from_string/to_string.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
