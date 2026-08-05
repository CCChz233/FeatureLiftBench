# publicsuffixlist__metadata_lookup_core__001

- release: `external50`
- lift: `Direct`
- coupling: `resource_coupling`
- strict validation: `PASS`
- tests/assertions: `7/11`

## Required API

- `featurelifted.PublicSuffixList` (class) `(source=None, accept_unknown=True, accept_encoded_idn=True, only_icann=False)`
- `featurelifted.PublicSuffixList.publicsuffix` (method) `(domain, accept_unknown=None, keep_case=False)`
- `featurelifted.PublicSuffixList.privatesuffix` (method) `(domain, accept_unknown=None, keep_case=False)`
- `featurelifted.PublicSuffixList.is_public` (method) `(domain) -> bool`
- `featurelifted.PublicSuffixList.is_private` (method) `(domain) -> bool`

## Public Behaviors

- **B001**: PublicSuffixList with no source loads the bundled public_suffix_list.dat resource offline.
- **B002**: publicsuffix and privatesuffix apply exact, wildcard, and exception rules to normalized domain names.
- **B003**: only_icann and unknown-suffix options alter classification according to their constructor settings.
- **B004**: The submitted package does not import publicsuffixlist or perform network refreshes.

## Tests

### `public_tests/test_public_api.py::test_bundled_list_resolves_common_suffixes`

- mapping: `B001`
- API: `featurelifted.PublicSuffixList`
- risk: `none`
- A001 `assert` L6: `psl.publicsuffix('www.example.co.uk') == 'co.uk'`
- A002 `assert` L7: `psl.privatesuffix('www.example.co.uk') == 'example.co.uk'`

### `public_tests/test_public_api.py::test_public_and_private_classification`

- mapping: `B002`
- API: `featurelifted.PublicSuffixList`
- risk: `none`
- A001 `assert` L12: `psl.is_public('com')`
- A002 `assert` L13: `psl.is_private('example.com')`

### `hidden_tests/test_hidden_behavior.py::test_custom_wildcard_and_exception_rules`

- mapping: `B002`
- API: `featurelifted.PublicSuffixList`
- risk: `none`
- A001 `assert` L6: `psl.publicsuffix('a.example') == 'a.example'`
- A002 `assert` L7: `psl.publicsuffix('city.example') == 'example'`

### `hidden_tests/test_hidden_behavior.py::test_unknown_suffix_policy`

- mapping: `B003`
- API: `featurelifted.PublicSuffixList`
- risk: `none`
- A001 `assert` L12: `strict.publicsuffix('host.unknown') is None`

### `hidden_tests/test_hidden_behavior.py::test_bundled_resource_is_available_offline`

- mapping: `B001`
- API: `featurelifted.PublicSuffixList`
- risk: `none`
- A001 `assert` L17: `psl.publicsuffix('www.example.co.uk') == 'co.uk'`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.PublicSuffixList`
- risk: `none`
- A001 `assert` L22: `isinstance(PublicSuffixList, type)`
- A002 `assert` L23: `all((callable(getattr(PublicSuffixList, n)) for n in ('publicsuffix', 'privatesuffix', 'is_public', 'is_private')))`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L32: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `publicsuffixlist`
- source entrypoints: `none`
- oracle source files: `publicsuffixlist/__init__.py, publicsuffixlist/public_suffix_list.dat`
- runtime dependencies: `none`
- oracle notes: Balanced Python-200 replacement slot resource-direct-01; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
