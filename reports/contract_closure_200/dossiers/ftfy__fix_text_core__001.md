# ftfy__fix_text_core__001

- release: `external50`
- lift: `Direct`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `8/8`

## Required API

- `featurelifted.fix_text` (function) `(text: str, ...) -> str`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: fix_text repairs latin-1 mojibake and em-dash sequences. Required observable cases include fix latin1 mojibake; fix em dash mojibake.
- **B002**: The extracted feature must support this observable behavior: fix_text leaves plain ascii unchanged. Required observable cases include fix identity ascii; fix preserves newlines.
- **B003**: The extracted feature must support this observable behavior: fix_text handles empty and partially broken utf-8. Required observable cases include fix empty; fix double encoded utf8.
- **B004**: wcwidth is the only allowed third-party dependency for formatting helpers.
- **B005**: The package exposes fix_text with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: ftfy.

## Tests

### `public_tests/test_public_api.py::test_fix_latin1_mojibake`

- mapping: `B001`
- API: `featurelifted.fix_text`
- risk: `none`
- A001 `assert` L7: `fix_text('cafÃ©') == 'café'`

### `public_tests/test_public_api.py::test_fix_em_dash_mojibake`

- mapping: `B002`
- API: `featurelifted.fix_text`
- risk: `none`
- A001 `assert` L11: `fix_text('â€”') == '—'`

### `public_tests/test_public_api.py::test_fix_identity_ascii`

- mapping: `B003`
- API: `featurelifted.fix_text`
- risk: `none`
- A001 `assert` L15: `fix_text('plain text') == 'plain text'`

### `hidden_tests/test_hidden_behavior.py::test_fix_double_encoded_utf8`

- mapping: `B001, B004`
- API: `featurelifted.fix_text`
- risk: `none`
- A001 `assert` L11: `'é' in fix_text(broken) or fix_text(broken) != broken`

### `hidden_tests/test_hidden_behavior.py::test_fix_preserves_newlines`

- mapping: `B002`
- API: `featurelifted.fix_text`
- risk: `none`
- A001 `assert` L16: `fix_text(text) == text`

### `hidden_tests/test_hidden_behavior.py::test_fix_empty`

- mapping: `B003`
- API: `featurelifted.fix_text`
- risk: `none`
- A001 `assert` L20: `fix_text('') == ''`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L29: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.fix_text`
- risk: `none`
- A001 `assert` L5: `callable(fix_text)`

## Dependency / Oracle Evidence

- allowed dependencies: `wcwidth`
- forbidden imports: `ftfy`
- source entrypoints: `none`
- oracle source files: `ftfy/__init__.py, ftfy/fixes.py`
- runtime dependencies: `wcwidth`
- oracle notes: Direct ftfy.fix_text mojibake repair.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
