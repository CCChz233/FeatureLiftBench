# packaging__requirement_marker_specifier__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `8/66`

## Required API

- `featurelifted.Version` (class) `(version: 'str') -> 'None'`
- `featurelifted.Specifier` (class) `(spec: 'str' = '', prereleases: 'bool | None' = None) -> 'None'`
- `featurelifted.SpecifierSet` (class) `(specifiers: 'str' = '', prereleases: 'bool | None' = None) -> 'None'`
- `featurelifted.Requirement` (class) `(requirement_string: 'str') -> 'None'`
- `featurelifted.Requirement.extras` (attribute)
- `featurelifted.Requirement.marker` (attribute)
- `featurelifted.Requirement.name` (attribute)
- `featurelifted.Requirement.specifier` (attribute)
- `featurelifted.Requirement.url` (attribute)
- `featurelifted.Marker` (class) `(marker: 'str') -> 'None'`
- `featurelifted.Marker.evaluate` (method) `(self, environment: 'dict[str, str] | None' = None) -> 'bool'`
- `featurelifted.default_environment` (function) `() -> 'Environment'`
- `featurelifted.InvalidVersion` (exception)
- `featurelifted.InvalidSpecifier` (exception)
- `featurelifted.InvalidRequirement` (exception)
- `featurelifted.InvalidMarker` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse, normalize, compare, hash, and stringify PEP 440 versions including epochs, post releases, pre releases, dev releases, and local versions. Required observable cases include versions and specifiers basic semantics; version normalization ordering and invalid inputs.
- **B002**: The extracted feature must support this observable behavior: parse and evaluate specifier sets including compatible release, equality wildcard, exclusion, prerelease handling, filtering, and containment. Required observable cases include versions and specifiers basic semantics; specifier prerelease wildcard compatible and filtering.
- **B003**: The extracted feature must support this observable behavior: parse PEP 508 requirements with extras, URL requirements, specifiers, and environment markers. Required observable cases include requirements and markers api; invalid requirement is rejected; requirement urls extras and marker evaluation.
- **B004**: The extracted feature must support this observable behavior: parse and evaluate environment markers with and/or grouping, in/not in operators, extra handling, and default environment values. Required observable cases include requirements and markers api; marker boolean logic default environment and errors.
- **B005**: The extracted feature must support this observable behavior: raise stable InvalidVersion, InvalidSpecifier, InvalidRequirement, and InvalidMarker errors for malformed input. Required observable cases include version normalization ordering and invalid inputs.
- **B006**: The package exposes the required task API paths `featurelifted.Version`, `featurelifted.Specifier`, `featurelifted.SpecifierSet`, `featurelifted.Requirement`, `featurelifted.Requirement.extras`, `featurelifted.Requirement.marker`, `featurelifted.Requirement.name`, `featurelifted.Requirement.specifier`, `featurelifted.Requirement.url`, `featurelifted.Marker`, `featurelifted.Marker.evaluate`, `featurelifted.default_environment`, and 4 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_versions_and_specifiers_basic_semantics`

- mapping: `B001, B002`
- API: `featurelifted.SpecifierSet, featurelifted.Version`
- risk: `exact_error_text`
- A001 `assert` L14: `Version('1.0a1') < Version('1.0')`
- A002 `assert` L15: `Version('1!2.0') > Version('2.0')`
- A003 `assert` L16: `str(Version('  v1.0-1 ')) == '1.0.post1'`
- A004 `assert` L19: `Version('1.5') in spec`
- A005 `assert` L20: `Version('2.0') not in spec`
- A006 `assert` L21: `list(spec.filter(['0.9', '1.0', '1.5', '2.0'])) == ['1.0', '1.5']`

### `public_tests/test_public_api.py::test_requirements_and_markers_public_api`

- mapping: `B003, B004`
- API: `featurelifted.Marker, featurelifted.Marker.evaluate, featurelifted.Requirement, featurelifted.default_environment`
- risk: `exact_error_text`
- A001 `assert` L27: `req.name == 'demo'`
- A002 `assert` L28: `req.extras == {'fast'}`
- A003 `assert` L29: `str(req.specifier) == '>=1.0'`
- A004 `assert` L30: `req.marker is not None`
- A005 `assert` L31: `req.marker.evaluate({'python_version': '3.11'})`
- A006 `assert` L32: `not req.marker.evaluate({'python_version': '3.9'})`
- A007 `assert` L35: `'python_version' in env`
- A008 `assert` L36: `Marker('os_name == "posix" or python_version >= "4"').evaluate({'os_name': 'posix', 'python_version': '3.11'})`

### `public_tests/test_public_api.py::test_invalid_requirement_is_rejected`

- mapping: `B003`
- API: `featurelifted.InvalidRequirement, featurelifted.Requirement`
- risk: `exception_semantics`
- A001 `raises` L42: `pytest.raises(InvalidRequirement)`

### `hidden_tests/test_hidden_behavior.py::test_version_normalization_ordering_and_invalid_inputs`

- mapping: `B001, B005`
- API: `featurelifted.InvalidVersion, featurelifted.Version`
- risk: `exact_error_text, exception_semantics, ordering_semantics`
- A001 `assert` L18: `str(Version('1.0.dev1')) == '1.0.dev1'`
- A002 `assert` L19: `str(Version('1.0rc1')) == '1.0rc1'`
- A003 `assert` L20: `str(Version('1.0+ABC.5')) == '1.0+abc.5'`
- A004 `assert` L21: `Version('1.0.dev1') < Version('1.0a1') < Version('1.0') < Version('1.0.post1')`
- A005 `assert` L22: `Version('1.0+abc.5') > Version('1.0')`
- A006 `assert` L23: `hash(Version('1.0')) == hash(Version('1.0.0'))`
- A007 `raises` L25: `pytest.raises(InvalidVersion)`

### `hidden_tests/test_hidden_behavior.py::test_specifier_prerelease_wildcard_compatible_and_filtering`

- mapping: `B002`
- API: `featurelifted.InvalidSpecifier, featurelifted.Specifier, featurelifted.SpecifierSet, featurelifted.SpecifierSet.filter, featurelifted.Version`
- risk: `exact_error_text, exception_semantics`
- A001 `assert` L30: `Version('1.0a1') not in SpecifierSet('>=1.0')`
- A002 `assert` L31: `Version('1.0a1') in SpecifierSet('>=1.0a1')`
- A003 `assert` L32: `Version('1.2.5') in SpecifierSet('==1.2.*')`
- A004 `assert` L33: `Version('1.3.0') not in SpecifierSet('==1.2.*')`
- A005 `assert` L34: `Version('2.3.4') in SpecifierSet('~=2.2')`
- A006 `assert` L35: `Version('3.0') not in SpecifierSet('~=2.2')`
- A007 `assert` L36: `Version('1.4') not in SpecifierSet('>=1.0,!=1.4,<2.0')`
- A008 `assert` L37: `str(Specifier('~=2.2')) == '~=2.2'`
- A009 `assert` L40: `filtered == ['1.1', '1.4']`
- A010 `raises` L42: `pytest.raises(InvalidSpecifier)`

### `hidden_tests/test_hidden_behavior.py::test_requirement_urls_extras_and_marker_evaluation`

- mapping: `B003`
- API: `featurelifted.InvalidRequirement, featurelifted.Requirement`
- risk: `exact_error_text, exception_semantics`
- A001 `assert` L51: `req.name == 'Example_Pkg'`
- A002 `assert` L52: `req.extras == {'PDF', 'ssl'}`
- A003 `assert` L53: `str(req.specifier) == '~=1.4'`
- A004 `assert` L54: `req.url is None`
- A005 `assert` L55: `req.marker is not None`
- A006 `assert` L56: `req.marker.evaluate({'python_version': '3.11', 'extra': 'PDF'})`
- A007 `assert` L57: `not req.marker.evaluate({'python_version': '3.9', 'extra': 'PDF'})`
- A008 `assert` L58: `not req.marker.evaluate({'python_version': '3.11', 'extra': 'ssl'})`
- A009 `assert` L61: `url_req.name == 'demo'`
- A010 `assert` L62: `url_req.url == 'https://example.com/demo-1.0.tar.gz'`
- A011 `assert` L63: `url_req.marker is not None`
- A012 `assert` L64: `url_req.marker.evaluate({'os_name': 'posix'})`
- A013 `raises` L66: `pytest.raises(InvalidRequirement)`

### `hidden_tests/test_hidden_behavior.py::test_marker_boolean_logic_default_environment_and_errors`

- mapping: `B004`
- API: `featurelifted.InvalidMarker, featurelifted.Marker, featurelifted.default_environment`
- risk: `exception_semantics`
- A001 `assert` L72: `env['implementation_name']`
- A002 `assert` L73: `env['python_version'].count('.') == 1`
- A003 `assert` L79: `marker.evaluate({'python_version': '3.12', 'implementation_name': 'cpython', 'os_name': 'posix'})`
- A004 `assert` L86: `not marker.evaluate({'python_version': '3.7', 'implementation_name': 'cpython', 'os_name': 'posix'})`
- A005 `raises` L94: `pytest.raises(InvalidMarker)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.InvalidMarker, featurelifted.InvalidRequirement, featurelifted.InvalidSpecifier, featurelifted.InvalidVersion, featurelifted.Marker, featurelifted.Requirement, featurelifted.Specifier, featurelifted.SpecifierSet, featurelifted.Version, featurelifted.default_environment`
- risk: `none`
- A001 `assert` L18: `isinstance(Version, type)`
- A002 `assert` L19: `isinstance(Specifier, type)`
- A003 `assert` L20: `isinstance(SpecifierSet, type)`
- A004 `assert` L21: `isinstance(Requirement, type)`
- A005 `assert` L22: `Requirement is not None`
- A006 `assert` L23: `Requirement is not None`
- A007 `assert` L24: `Requirement is not None`
- A008 `assert` L25: `Requirement is not None`
- A009 `assert` L26: `Requirement is not None`
- A010 `assert` L27: `isinstance(Marker, type)`
- A011 `assert` L28: `hasattr(Marker, 'evaluate')`
- A012 `assert` L29: `callable(default_environment)`
- A013 `assert` L30: `issubclass(InvalidVersion, BaseException)`
- A014 `assert` L31: `issubclass(InvalidSpecifier, BaseException)`
- A015 `assert` L32: `issubclass(InvalidRequirement, BaseException)`
- A016 `assert` L33: `issubclass(InvalidMarker, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `packaging`
- source entrypoints: `packaging.version.Version, packaging.version.InvalidVersion, packaging.specifiers.Specifier, packaging.specifiers.SpecifierSet, packaging.specifiers.InvalidSpecifier, packaging.requirements.Requirement, packaging.requirements.InvalidRequirement, packaging.markers.Marker, packaging.markers.InvalidMarker, packaging.markers.default_environment`
- oracle source files: `none`
- runtime dependencies: `none`

## Machine Issues

- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.SpecifierSet.filter
