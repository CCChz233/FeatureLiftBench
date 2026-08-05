# yarl__url_model_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `16/34`

## Required API

- `featurelifted.URL` (constant)
- `featurelifted.Query` (object)
- `featurelifted.QueryVariable` (object)
- `featurelifted.SimpleQuery` (object)
- `featurelifted.cache_clear` (function) `() -> None`
- `featurelifted.cache_configure` (function) `(*, idna_encode_size: int | None = 256, idna_decode_size: int | None = 256, ip_address_size: int | None | UndefinedType = <UndefinedType._singleton: 0>, host_validate_size: int | None | UndefinedType = <UndefinedType._singleton: 0>, encode_host_size: int | None | UndefinedType = <UndefinedType._singleton: 0>) -> None`
- `featurelifted.cache_info` (function) `() -> CacheInfo`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse and construct URL objects with scheme, host, port, path, query, fragment. Required observable cases include basic parse components; with query kwargs; query no double unquote.
- **B002**: The extracted feature must support this observable behavior: join absolute and relative URLs preserving query and fragment rules. Required observable cases include join absolute path; with query kwargs; join relative parent path; query no double unquote; join preserves base query when relative has query only; join rejects non url type.
- **B003**: The extracted feature must support this observable behavior: MultiDict query with duplicate keys, ordering, and semicolon-in-value handling. Required observable cases include duplicate query keys multidict; semicolon in query value not separator; update query with multidict.
- **B004**: The extracted feature must support this observable behavior: path normalization for dot and dot-dot segments. Required observable cases include joinpath appends segments; joinpath normalizes dot segments.
- **B005**: The extracted feature must support this observable behavior: IDNA host encoding and decoding; default port omission in string form. Required observable cases include idna unicode host decoded; default http port omitted from str.
- **B006**: The extracted feature must support this observable behavior: with_query, update_query, and joinpath helpers. Required observable cases include joinpath appends segments; joinpath normalizes dot segments; update query with multidict.
- **B007**: The package exposes the required task API paths `featurelifted.URL`, `featurelifted.Query`, `featurelifted.QueryVariable`, `featurelifted.SimpleQuery`, `featurelifted.cache_clear`, `featurelifted.cache_configure`, `featurelifted.cache_info` with the kinds and callable signatures listed in this contract.

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

- mapping: `B001, B002`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L24: `url.query['a'] == '1'`
- A002 `assert` L25: `url.query['b'] == '2'`

### `public_tests/test_url_public.py::test_joinpath_appends_segments`

- mapping: `B004, B006`
- API: `featurelifted.URL`
- risk: `filesystem_resource`
- A001 `assert` L30: `url.path == '/base/child/leaf'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.Query, featurelifted.QueryVariable, featurelifted.SimpleQuery, featurelifted.URL, featurelifted.cache_clear, featurelifted.cache_configure, featurelifted.cache_info`
- risk: `none`
- A001 `assert` L15: `URL is not None`
- A002 `assert` L16: `Query is not None`
- A003 `assert` L17: `QueryVariable is not None`
- A004 `assert` L18: `SimpleQuery is not None`
- A005 `assert` L19: `callable(cache_clear)`
- A006 `assert` L20: `callable(cache_configure)`
- A007 `assert` L21: `callable(cache_info)`

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

### `hidden_tests/test_url_hidden.py::test_join_relative_parent_path`

- mapping: `B002`
- API: `featurelifted.URL`
- risk: `filesystem_resource`
- A001 `assert` L34: `joined.path == '/a/d'`

### `hidden_tests/test_url_hidden.py::test_joinpath_normalizes_dot_segments`

- mapping: `B004, B006`
- API: `featurelifted.URL`
- risk: `filesystem_resource`
- A001 `assert` L39: `url.path == '/foo/baz'`

### `hidden_tests/test_url_hidden.py::test_default_http_port_omitted_from_str`

- mapping: `B005`
- API: `featurelifted.URL`
- risk: `exact_error_text`
- A001 `assert` L43: `str(URL('http://example.com:80/')) == 'http://example.com/'`

### `hidden_tests/test_url_hidden.py::test_query_no_double_unquote`

- mapping: `B001, B002`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L51: `url.query['url'] == sample_url`

### `hidden_tests/test_url_hidden.py::test_update_query_with_multidict`

- mapping: `B003, B006`
- API: `featurelifted.URL`
- risk: `state_mutation`
- A001 `assert` L57: `updated.query.getall('a') == ['9']`
- A002 `assert` L58: `updated.query['b'] == '2'`
- A003 `assert` L59: `base.query['a'] == '1'`

### `hidden_tests/test_url_hidden.py::test_join_preserves_base_query_when_relative_has_query_only`

- mapping: `B002`
- API: `featurelifted.URL`
- risk: `none`
- A001 `assert` L65: `joined.query['only'] == '2'`
- A002 `assert` L66: `'keep' not in joined.query`

### `hidden_tests/test_url_hidden.py::test_no_yarl_import_surface`

- mapping: `B008`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L75: `not import_pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_url_hidden.py::test_join_rejects_non_url_type`

- mapping: `B002`
- API: `featurelifted.URL`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L79: `pytest.raises(TypeError, match='url should be URL')`

## Dependency / Oracle Evidence

- allowed dependencies: `idna, multidict, propcache`
- forbidden imports: `yarl, aiohttp`
- source entrypoints: `yarl.URL, yarl._parse.split_url, yarl._path.normalize_path, yarl._query.get_str_query, yarl._quoters.QUOTER, yarl._url.URL.join, yarl._url.URL.with_query, yarl._url.URL.update_query, yarl._url.URL.joinpath`
- oracle source files: `yarl/_parse.py, yarl/_path.py, yarl/_query.py, yarl/_quoters.py, yarl/_quoting.py, yarl/_quoting_py.py, yarl/_url.py`
- runtime dependencies: `idna, multidict, propcache`
- oracle notes: Oracle copies the yarl URL model package (pure-Python quoting). Repo snapshot includes upstream tests for copy-all extraction calibration.
