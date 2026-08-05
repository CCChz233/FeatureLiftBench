# bleach__sanitize_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/16`

## Required API

- `featurelifted.clean` (function) `(text, tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul'], attributes={'a': ['href', 'title'], 'abbr': ['title'], 'acronym': ['title']}, styles=[], protocols=['http', 'https', 'mailto'], strip=False, strip_comments=True)`
- `featurelifted.Cleaner` (class) `(tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul'], attributes={'a': ['href', 'title'], 'abbr': ['title'], 'acronym': ['title']}, styles=[], protocols=['http', 'https', 'mailto'], strip=False, strip_comments=True, filters=None)`
- `featurelifted.ALLOWED_TAGS` (constant)
- `featurelifted.ALLOWED_ATTRIBUTES` (constant)
- `featurelifted.ALLOWED_PROTOCOLS` (constant)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: XSS tag stripping. Required observable cases include clean escapes unknown tags; javascript href stripped.
- **B002**: The extracted feature must support this observable behavior: allowed attributes and protocols. Required observable cases include clean allows safe link; strip mode removes tag.
- **B003**: The extracted feature must support this observable behavior: strip and strip_comments modes. Required observable cases include clean strips script; strip disallowed script; strip mode removes tag; strip comments removed.
- **B004**: The extracted feature must support this observable behavior: callable attribute filters. Required observable cases include custom attributes callable.
- **B005**: The package exposes the required task API paths `featurelifted.clean`, `featurelifted.Cleaner`, `featurelifted.ALLOWED_TAGS`, `featurelifted.ALLOWED_ATTRIBUTES`, `featurelifted.ALLOWED_PROTOCOLS` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_clean_strips_script`

- mapping: `B003`
- API: `featurelifted.clean`
- risk: `none`
- A001 `assert` L8: `clean(dirty) == '<b>ok</b>&lt;script&gt;alert(1)&lt;/script&gt;'`

### `public_tests/test_public_api.py::test_clean_allows_safe_link`

- mapping: `B002`
- API: `featurelifted.clean`
- risk: `none`
- A001 `assert` L14: `'href="https://example.com"' in out`
- A002 `assert` L15: `'link' in out`

### `public_tests/test_public_api.py::test_clean_escapes_unknown_tags`

- mapping: `B001`
- API: `featurelifted.clean`
- risk: `none`
- A001 `assert` L20: `clean(dirty) == '&lt;custom&gt;text&lt;/custom&gt;'`

### `hidden_tests/test_hidden_behavior.py::test_strip_disallowed_script`

- mapping: `B003`
- API: `featurelifted.clean`
- risk: `none`
- A001 `assert` L11: `clean(dirty, tags=['b'], strip=True) == '<b>keep</b>x'`

### `hidden_tests/test_hidden_behavior.py::test_strip_mode_removes_tag`

- mapping: `B002, B003`
- API: `featurelifted.clean`
- risk: `none`
- A001 `assert` L16: `clean(dirty, tags=[], strip=True) == 'bold plain'`

### `hidden_tests/test_hidden_behavior.py::test_javascript_href_stripped`

- mapping: `B001`
- API: `featurelifted.clean`
- risk: `none`
- A001 `assert` L21: `'href=' not in clean(dirty)`

### `hidden_tests/test_hidden_behavior.py::test_strip_comments_removed`

- mapping: `B003`
- API: `featurelifted.clean`
- risk: `none`
- A001 `assert` L26: `clean(dirty, strip_comments=True) == '<b>hi</b>'`

### `hidden_tests/test_hidden_behavior.py::test_custom_attributes_callable`

- mapping: `B004`
- API: `featurelifted.clean`
- risk: `none`
- A001 `assert` L35: `'href="https://ok"' in out`
- A002 `assert` L36: `'http://no' not in out`

### `hidden_tests/test_hidden_behavior.py::test_no_bleach_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L46: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.ALLOWED_ATTRIBUTES, featurelifted.ALLOWED_PROTOCOLS, featurelifted.ALLOWED_TAGS, featurelifted.Cleaner, featurelifted.clean`
- risk: `none`
- A001 `assert` L13: `callable(clean)`
- A002 `assert` L14: `isinstance(Cleaner, type)`
- A003 `assert` L15: `ALLOWED_TAGS is not None`
- A004 `assert` L16: `ALLOWED_ATTRIBUTES is not None`
- A005 `assert` L17: `ALLOWED_PROTOCOLS is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `bleach`
- source entrypoints: `bleach.clean, bleach.sanitizer.Cleaner`
- oracle source files: `bleach/sanitizer.py, bleach/html5lib_shim.py, bleach/utils.py, bleach/_vendor/parse.py, bleach/_vendor/html5lib`
- runtime dependencies: `none`
- oracle notes: Oracle sanitizer stack; repo includes linkifier for copy-all penalty.
