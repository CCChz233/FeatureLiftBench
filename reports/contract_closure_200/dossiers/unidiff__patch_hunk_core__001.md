# unidiff__patch_hunk_core__001

- release: `external50`
- lift: `Composite`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `8/14`

## Required API

- `featurelifted.PatchSet` (class)
- `featurelifted.PatchedFile` (class)
- `featurelifted.Hunk` (class)
- `featurelifted.UnidiffParseError` (class)
- `featurelifted.LINE_TYPE_ADDED` (constant)
- `featurelifted.LINE_TYPE_REMOVED` (constant)
- `featurelifted.LINE_TYPE_CONTEXT` (constant)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: PatchSet parses unified diffs into PatchedFile/Hunk. Required observable cases include parse patchset.
- **B002**: The extracted feature must support this observable behavior: hunk lines expose added/removed/context types. Required observable cases include hunk lines; context lines.
- **B003**: The extracted feature must support this observable behavior: UnidiffParseError on short hunks and multi-file patches. Required observable cases include parse error short hunk; multiple files.
- **B004**: PatchedFile exposes added/removed counts.
- **B005**: The package exposes PatchSet/PatchedFile/Hunk/UnidiffParseError/LINE_TYPE_* with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: unidiff.

## Tests

### `public_tests/test_public_api.py::test_parse_patchset`

- mapping: `B001`
- API: `featurelifted.PatchSet`
- risk: `none`
- A001 `assert` L18: `len(ps) == 1`
- A002 `assert` L19: `ps[0].path == 'file.py'`
- A003 `assert` L20: `len(ps[0]) == 1`

### `public_tests/test_public_api.py::test_hunk_lines`

- mapping: `B002`
- API: `featurelifted.LINE_TYPE_ADDED, featurelifted.LINE_TYPE_REMOVED, featurelifted.PatchSet`
- risk: `none`
- A001 `assert` L27: `any(('return 2' in v for v in added))`
- A002 `assert` L28: `any(('return 1' in v for v in removed))`

### `public_tests/test_public_api.py::test_parse_error_short_hunk`

- mapping: `B003`
- API: `featurelifted.PatchSet, featurelifted.UnidiffParseError`
- risk: `none`
- A001 `assert` L35: `False`

### `hidden_tests/test_hidden_behavior.py::test_multiple_files`

- mapping: `B001, B004`
- API: `featurelifted.PatchSet, featurelifted.PatchedFile`
- risk: `none`
- A001 `assert` L24: `len(ps) == 2`
- A002 `assert` L25: `{pf.path for pf in ps} == {'a.py', 'b.py'}`
- A003 `assert` L26: `all((isinstance(pf, PatchedFile) for pf in ps))`

### `hidden_tests/test_hidden_behavior.py::test_context_lines`

- mapping: `B002`
- API: `featurelifted.LINE_TYPE_CONTEXT, featurelifted.PatchSet`
- risk: `none`
- A001 `assert` L40: `any(('def f' in v for v in ctx))`

### `hidden_tests/test_hidden_behavior.py::test_added_removed_counts`

- mapping: `B003`
- API: `featurelifted.PatchSet`
- risk: `none`
- A001 `assert` L55: `pf.added > 0 and pf.removed > 0`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L64: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Hunk, featurelifted.PatchSet, featurelifted.PatchedFile, featurelifted.UnidiffParseError`
- risk: `none`
- A001 `assert` L5: `PatchSet is not None and PatchedFile is not None`
- A002 `assert` L6: `Hunk is not None and UnidiffParseError is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `unidiff`
- source entrypoints: `none`
- oracle source files: `unidiff/patch.py, unidiff/__init__.py`
- runtime dependencies: `none`
- oracle notes: Composite PatchSet + PatchedFile + Hunk model (W2 libcst native-blocked backup).
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
