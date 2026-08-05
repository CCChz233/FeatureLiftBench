# tldextract__suffix_resolve_core__001

- release: `external50`
- lift: `Composite`
- coupling: `resource_coupling`
- strict validation: `PASS`
- tests/assertions: `6/14`

## Required API

- `featurelifted.TLDExtract` (class)
- `featurelifted.TLDExtract.__call__` (method)
- `featurelifted.extract` (function)
- `featurelifted.ExtractResult` (class)
- `featurelifted.ExtractResult.subdomain` (attribute)
- `featurelifted.ExtractResult.domain` (attribute)
- `featurelifted.ExtractResult.suffix` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: offline TLDExtract splits URLs. Required observable cases include tldextract offline.
- **B002**: The extracted feature must support this observable behavior: extract convenience helper. Required observable cases include extract convenience.
- **B003**: The extracted feature must support this observable behavior: registered domain and bare hosts. Required observable cases include registered domain; no subdomain.
- **B004**: suffix_list_urls=() disables network suffix fetch.
- **B005**: The package exposes TLDExtract/extract/ExtractResult with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: tldextract.

## Tests

### `public_tests/test_public_api.py::test_tldextract_offline`

- mapping: `B001`
- API: `featurelifted.TLDExtract`
- risk: `none`
- A001 `assert` L9: `result.subdomain == 'www'`
- A002 `assert` L10: `result.domain == 'google'`
- A003 `assert` L11: `result.suffix == 'co.uk'`

### `public_tests/test_public_api.py::test_extract_convenience`

- mapping: `B002`
- API: `featurelifted.TLDExtract`
- risk: `none`
- A001 `assert` L17: `result.domain == 'example'`
- A002 `assert` L18: `result.suffix == 'com'`

### `hidden_tests/test_hidden_behavior.py::test_registered_domain`

- mapping: `B001, B003, B004`
- API: `featurelifted.TLDExtract`
- risk: `none`
- A001 `assert` L9: `f'{result.domain}.{result.suffix}' == 'bar.co.uk'`

### `hidden_tests/test_hidden_behavior.py::test_no_subdomain`

- mapping: `B002`
- API: `featurelifted.TLDExtract`
- risk: `none`
- A001 `assert` L15: `result.subdomain == ''`
- A002 `assert` L16: `result.domain == 'example'`
- A003 `assert` L17: `result.suffix == 'com'`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L31: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.TLDExtract, featurelifted.TLDExtract.__call__`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'ExtractResult')`
- A002 `assert` L6: `hasattr(featurelifted, 'TLDExtract')`
- A003 `assert` L7: `hasattr(featurelifted, 'extract')`
- A004 `assert` L8: `callable(featurelifted.TLDExtract.__call__)`

## Dependency / Oracle Evidence

- allowed dependencies: `certifi, charset-normalizer, filelock, idna, requests, requests-file, urllib3`
- forbidden imports: `tldextract`
- source entrypoints: `none`
- oracle source files: `tldextract/tldextract.py, tldextract/.tld_set_snapshot`
- runtime dependencies: `certifi, charset-normalizer, filelock, idna, requests, requests-file, urllib3`
- oracle notes: Composite TLDExtract offline with suffix_list_urls=().
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
