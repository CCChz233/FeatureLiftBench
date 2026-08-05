# Contract V2 P0: yarl__url_model_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `18/45`

## Required API

- `featurelifted.URL` (class) `(val: Union[str, urllib.parse.SplitResult, ForwardRef('URL'), UndefinedType] = <UndefinedType._singleton: 0>, *, encoded: bool = False, strict: bool | None = None) -> 'URL'`
- `featurelifted.URL.fragment` (attribute)
- `featurelifted.URL.host` (attribute)
- `featurelifted.URL.human_repr` (method) `(self) -> str`
- `featurelifted.URL.join` (method) `(self, url: URL) -> URL`
- `featurelifted.URL.joinpath` (method) `(self, *paths: str) -> URL`
- `featurelifted.URL.path` (attribute)
- `featurelifted.URL.port` (attribute)
- `featurelifted.URL.query` (attribute)
- `featurelifted.URL.scheme` (attribute)
- `featurelifted.URL.update_query` (method) `(self, *args, **kwargs) -> URL`
- `featurelifted.URL.with_query` (method) `(self, *args, **kwargs) -> URL`
- `featurelifted.URL.__str__` (method) `(self) -> str`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse and construct URL objects with scheme, host, port, path, query, fragment. Required observable cases include basic parse components; with query kwargs; query no double unquote.
- **B002**: URL.join accepts only URL operands and applies RFC-style absolute/relative path, query, and fragment replacement or inheritance rules.
- **B003**: URL.query is an ordered MultiDict-style read-only result supporting key lookup, membership, len(), getall(), and items() with duplicate-key order preserved and semicolons retained inside values.
- **B004**: The extracted feature must support this observable behavior: path normalization for dot and dot-dot segments. Required observable cases include joinpath appends segments; joinpath normalizes dot segments.
- **B005**: Unicode hosts are IDNA-encoded in str(URL), punycode hosts are decoded by URL.host and human_repr(), and default HTTP port 80 is omitted from string form.
- **B006**: The extracted feature must support this observable behavior: with_query, update_query, and joinpath helpers. Required observable cases include joinpath appends segments; joinpath normalizes dot segments; update query with multidict.
- **B007**: The package exposes the required task API paths `featurelifted.URL`, `featurelifted.URL.fragment`, `featurelifted.URL.host`, `featurelifted.URL.human_repr`, `featurelifted.URL.join`, `featurelifted.URL.joinpath`, `featurelifted.URL.path`, `featurelifted.URL.port`, `featurelifted.URL.query`, `featurelifted.URL.scheme`, `featurelifted.URL.update_query`, `featurelifted.URL.with_query`, and 1 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_url_public.py::test_basic_parse_components`

- mapping: `B001`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L8: `url.scheme == 'http'`
- A002 `assert` L9: `url.host == 'example.com'`
- A003 `assert` L10: `url.port == 8080`
- A004 `assert` L11: `url.path == '/foo'`
- A005 `assert` L12: `url.fragment == 'frag'`
- A006 `assert` L13: `url.query['bar'] == '1'`

### `public_tests/test_url_public.py::test_join_absolute_path`

- mapping: `B002`
- API: `featurelifted.URL`
- risk: `exact_error_text, filesystem_resource`
- A001 `assert` L19: `str(joined) == 'http://example.com/c'`

### `public_tests/test_url_public.py::test_with_query_kwargs`

- mapping: `B001, B006`
- API: `featurelifted.URL, featurelifted.URL.with_query`
- risk: `none`
- A001 `assert` L24: `url.query['a'] == '1'`
- A002 `assert` L25: `url.query['b'] == '2'`

### `public_tests/test_url_public.py::test_joinpath_appends_segments`

- mapping: `B004, B006`
- API: `featurelifted.URL, featurelifted.URL.joinpath`
- risk: `filesystem_resource`
- A001 `assert` L30: `url.path == '/base/child/leaf'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L9: `isinstance(URL, type)`
- A002 `assert` L10: `URL is not None`
- A003 `assert` L11: `URL is not None`
- A004 `assert` L12: `hasattr(URL, 'human_repr')`
- A005 `assert` L13: `hasattr(URL, 'join')`
- A006 `assert` L14: `hasattr(URL, 'joinpath')`
- A007 `assert` L15: `URL is not None`
- A008 `assert` L16: `URL is not None`
- A009 `assert` L17: `URL is not None`
- A010 `assert` L18: `URL is not None`
- A011 `assert` L19: `hasattr(URL, 'update_query')`
- A012 `assert` L20: `hasattr(URL, 'with_query')`
- A013 `assert` L21: `hasattr(URL, '__str__')`

### `hidden_tests/test_url_hidden.py::test_duplicate_query_keys_multidict`

- mapping: `B003`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L15: `url.query.getall('a') == ['1', '2']`
- A002 `assert` L16: `list(url.query.items()) == [('a', '1'), ('a', '2'), ('b', '3')]`

### `hidden_tests/test_url_hidden.py::test_semicolon_in_query_value_not_separator`

- mapping: `B003`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L21: `len(url.query) == 1`
- A002 `assert` L22: `url.query['a'] == '10;b=20'`

### `hidden_tests/test_url_hidden.py::test_idna_unicode_host_decoded`

- mapping: `B005`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L27: `url.host == 'όβλοσ.com'`
- A002 `assert` L28: `'xn--' not in url.human_repr()`

### `hidden_tests/test_url_hidden.py::test_unicode_host_is_idna_encoded`

- mapping: `B005`
- API: `featurelifted.URL`
- risk: `exact_error_text`
- A001 `assert` L33: `'xn--' in str(url)`
- A002 `assert` L34: `url.host == 'όβλοσ.com'`

### `hidden_tests/test_url_hidden.py::test_join_relative_parent_path`

- mapping: `B002`
- API: `featurelifted.URL, featurelifted.URL.join`
- risk: `filesystem_resource`
- A001 `assert` L39: `joined.path == '/a/d'`

### `hidden_tests/test_url_hidden.py::test_join_fragment_rules`

- mapping: `B002`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L45: `joined.path == '/path'`
- A002 `assert` L46: `joined.query['keep'] == '1'`
- A003 `assert` L47: `joined.fragment == 'new'`

### `hidden_tests/test_url_hidden.py::test_joinpath_normalizes_dot_segments`

- mapping: `B004, B006`
- API: `featurelifted.URL, featurelifted.URL.joinpath`
- risk: `filesystem_resource`
- A001 `assert` L52: `url.path == '/foo/baz'`

### `hidden_tests/test_url_hidden.py::test_default_http_port_omitted_from_str`

- mapping: `B005`
- API: `featurelifted.URL`
- risk: `exact_error_text`
- A001 `assert` L56: `str(URL('http://example.com:80/')) == 'http://example.com/'`

### `hidden_tests/test_url_hidden.py::test_query_no_double_unquote`

- mapping: `B001`
- API: `featurelifted.URL, featurelifted.URL.query`
- risk: `none`
- A001 `assert` L62: `URL('http://test_url.aha?' + query).query['url'] == sample_url`

### `hidden_tests/test_url_hidden.py::test_update_query_with_multidict`

- mapping: `B003, B006`
- API: `featurelifted.URL`
- risk: `state_mutation`
- A001 `assert` L68: `updated.query.getall('a') == ['9']`
- A002 `assert` L69: `updated.query['b'] == '2'`
- A003 `assert` L70: `base.query['a'] == '1'`

### `hidden_tests/test_url_hidden.py::test_join_preserves_base_query_when_relative_has_query_only`

- mapping: `B002`
- API: `featurelifted.URL, featurelifted.URL.join`
- risk: `none`
- A001 `assert` L75: `joined.query['only'] == '2'`
- A002 `assert` L76: `'keep' not in joined.query`

### `hidden_tests/test_url_hidden.py::test_no_yarl_import_surface`

- mapping: `B008`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L85: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_url_hidden.py::test_join_rejects_non_url_type`

- mapping: `B002`
- API: `featurelifted.URL, featurelifted.URL.join`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L89: `pytest.raises(TypeError, match='url should be URL')`

## Dependency / Oracle Evidence

- allowed dependencies: `idna, multidict, propcache`
- forbidden imports: `yarl, aiohttp`
- source entrypoints: `yarl.URL, yarl._parse.split_url, yarl._path.normalize_path, yarl._query.get_str_query, yarl._quoters.QUOTER, yarl._url.URL.join, yarl._url.URL.with_query, yarl._url.URL.update_query, yarl._url.URL.joinpath`
- oracle source files: `yarl/_parse.py, yarl/_path.py, yarl/_query.py, yarl/_quoters.py, yarl/_quoting.py, yarl/_quoting_py.py, yarl/_url.py`
- runtime dependencies: `idna, multidict, propcache`
- oracle notes: Oracle copies the yarl URL model package (pure-Python quoting). Repo snapshot includes upstream tests for copy-all extraction calibration.
