# rfc3986__uri_parse_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `10/29`

## Required API

- `featurelifted.URIBuilder` (class) `(scheme=None, userinfo=None, host=None, port=None, path=None, query=None, fragment=None)`
- `featurelifted.URIBuilder.from_uri` (method) `(reference)`
- `featurelifted.URIReference` (class) `(scheme, authority, path, query, fragment, encoding='utf-8')`
- `featurelifted.is_valid_uri` (function) `(uri, encoding='utf-8', **kwargs)`
- `featurelifted.normalize_uri` (function) `(uri, encoding='utf-8')`
- `featurelifted.uri_reference` (function) `(uri, encoding='utf-8')`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse URI components and authority subcomponents. Required observable cases include uri reference components; authority userinfo host port; builder from uri roundtrip.
- **B002**: The extracted feature must support this observable behavior: normalize scheme/host/path. Required observable cases include authority userinfo host port; normalize uri path dots; uri reference ipv6 host; normalize preserves fragment.
- **B003**: The extracted feature must support this observable behavior: URIBuilder compose and finalize. Required observable cases include uri builder finalize; uri reference ipv6 host.
- **B004**: The extracted feature must support this observable behavior: is_valid_uri convenience check. Required observable cases include is valid uri https; builder from uri roundtrip; uri reference ipv6 host.
- **B005**: The package exposes the required task API paths `featurelifted.URIBuilder`, `featurelifted.URIBuilder.from_uri`, `featurelifted.URIReference`, `featurelifted.is_valid_uri`, `featurelifted.normalize_uri`, `featurelifted.uri_reference` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_uri_reference_components`

- mapping: `B001`
- API: `featurelifted.uri_reference`
- risk: `none`
- A001 `assert` L8: `ref.scheme == 'https'`
- A002 `assert` L9: `ref.host == 'example.com'`
- A003 `assert` L10: `ref.port == '8080'`
- A004 `assert` L11: `ref.path == '/path'`
- A005 `assert` L12: `ref.query == 'q=1'`
- A006 `assert` L13: `ref.fragment == 'frag'`

### `public_tests/test_public_api.py::test_is_valid_uri_https`

- mapping: `B004`
- API: `featurelifted.is_valid_uri`
- risk: `none`
- A001 `assert` L17: `is_valid_uri('https://example.com/path')`

### `public_tests/test_public_api.py::test_uri_builder_finalize`

- mapping: `B003`
- API: `featurelifted.URIBuilder, featurelifted.URIBuilder.add_host, featurelifted.URIBuilder.add_path, featurelifted.URIBuilder.add_scheme, featurelifted.URIBuilder.finalize`
- risk: `filesystem_resource`
- A001 `assert` L22: `built.scheme == 'https'`
- A002 `assert` L23: `built.host == 'example.com'`
- A003 `assert` L24: `built.path == '/x'`

### `hidden_tests/test_hidden_behavior.py::test_authority_userinfo_host_port`

- mapping: `B001, B002`
- API: `featurelifted.uri_reference`
- risk: `none`
- A001 `assert` L11: `ref.userinfo == 'User:Pass'`
- A002 `assert` L12: `ref.host == 'Example.COM'`
- A003 `assert` L13: `ref.port == '8080'`

### `hidden_tests/test_hidden_behavior.py::test_normalize_uri_path_dots`

- mapping: `B002`
- API: `featurelifted.normalize_uri`
- risk: `none`
- A001 `assert` L17: `normalize_uri('HTTP://EXAMPLE.COM:80/a/../b') == 'http://example.com:80/b'`

### `hidden_tests/test_hidden_behavior.py::test_builder_from_uri_roundtrip`

- mapping: `B001, B004`
- API: `featurelifted.URIBuilder, featurelifted.URIBuilder.finalize, featurelifted.URIBuilder.from_uri, featurelifted.uri_reference`
- risk: `none`
- A001 `assert` L23: `rebuilt.scheme == 'https'`
- A002 `assert` L24: `rebuilt.host == 'example.com'`
- A003 `assert` L25: `rebuilt.path == '/a'`
- A004 `assert` L26: `rebuilt.query == 'x=1'`
- A005 `assert` L27: `rebuilt.fragment == 'top'`

### `hidden_tests/test_hidden_behavior.py::test_uri_reference_ipv6_host`

- mapping: `B002, B003, B004`
- API: `featurelifted.uri_reference`
- risk: `none`
- A001 `assert` L32: `ref.host == '[::1]'`
- A002 `assert` L33: `ref.port == '8080'`

### `hidden_tests/test_hidden_behavior.py::test_normalize_preserves_fragment`

- mapping: `B002`
- API: `featurelifted.normalize_uri`
- risk: `none`
- A001 `assert` L37: `normalize_uri('HTTPS://Example.COM/x#frag').endswith('#frag')`

### `hidden_tests/test_hidden_behavior.py::test_no_rfc3986_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L46: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.URIBuilder, featurelifted.URIReference, featurelifted.is_valid_uri, featurelifted.normalize_uri, featurelifted.uri_reference`
- risk: `none`
- A001 `assert` L13: `isinstance(URIBuilder, type)`
- A002 `assert` L14: `hasattr(URIBuilder, 'from_uri')`
- A003 `assert` L15: `isinstance(URIReference, type)`
- A004 `assert` L16: `callable(is_valid_uri)`
- A005 `assert` L17: `callable(normalize_uri)`
- A006 `assert` L18: `callable(uri_reference)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `rfc3986`
- source entrypoints: `rfc3986.uri_reference, rfc3986.normalize_uri, rfc3986.is_valid_uri, rfc3986.builder.URIBuilder`
- oracle source files: `rfc3986/uri.py, rfc3986/parseresult.py, rfc3986/api.py, rfc3986/misc.py, rfc3986/normalizers.py, rfc3986/_mixin.py, rfc3986/compat.py, rfc3986/exceptions.py, rfc3986/abnf_regexp.py, rfc3986/builder.py`
- runtime dependencies: `none`
- oracle notes: Oracle is parse/build/normalize core; repo includes validators/iri for copy-all penalty.

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.URIBuilder.add_host
- public_tests/test_public_api.py uses undeclared API reference featurelifted.URIBuilder.add_path
- public_tests/test_public_api.py uses undeclared API reference featurelifted.URIBuilder.add_scheme
- public_tests/test_public_api.py uses undeclared API reference featurelifted.URIBuilder.finalize
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.URIBuilder.finalize
