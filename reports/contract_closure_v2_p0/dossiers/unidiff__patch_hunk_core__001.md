# Contract V2 P0: unidiff__patch_hunk_core__001

- release: `external50`
- lift: `Composite`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `8/32`

## Required API

- `featurelifted.PatchSet` (class) `(f: 'Union[StringIO, str, bytes, Iterable[str]]', encoding: 'Optional[str]' = None, metadata_only: 'bool' = False) -> 'None'`
- `featurelifted.PatchSet.__len__` (method) `(self) -> int`
- `featurelifted.PatchSet.__getitem__` (method) `(self, index: int) -> PatchedFile`
- `featurelifted.PatchSet.__iter__` (method) `(self) -> iterator[PatchedFile]`
- `featurelifted.PatchedFile` (class) `(patch_info: 'Optional[PatchInfo]' = None, source: 'str' = '', target: 'str' = '', source_timestamp: 'Optional[str]' = None, target_timestamp: 'Optional[str]' = None, is_binary_file: 'bool' = False, source_mode: 'Optional[str]' = None, target_mode: 'Optional[str]' = None, diff_line_no: 'Optional[int]' = None) -> 'None'`
- `featurelifted.PatchedFile.__len__` (method) `(self) -> int`
- `featurelifted.PatchedFile.__getitem__` (method) `(self, index: int) -> Hunk`
- `featurelifted.PatchedFile.__iter__` (method) `(self) -> iterator[Hunk]`
- `featurelifted.PatchedFile.path` (attribute)
- `featurelifted.PatchedFile.added` (attribute)
- `featurelifted.PatchedFile.removed` (attribute)
- `featurelifted.Hunk` (class) `(src_start: 'Union[str, int]' = 0, src_len: 'Optional[Union[str, int]]' = 0, tgt_start: 'Union[str, int]' = 0, tgt_len: 'Optional[Union[str, int]]' = 0, section_header: 'str' = '') -> 'None'`
- `featurelifted.Hunk.__iter__` (method) `(self) -> iterator[patch.Line]`
- `featurelifted.UnidiffParseError` (exception)
- `featurelifted.LINE_TYPE_ADDED` (constant)
- `featurelifted.LINE_TYPE_REMOVED` (constant)
- `featurelifted.LINE_TYPE_CONTEXT` (constant)
- `featurelifted.patch.Line` (class)
- `featurelifted.patch.Line.value` (attribute)
- `featurelifted.patch.Line.line_type` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: PatchSet parses unified diffs into PatchedFile/Hunk. Required observable cases include parse patchset.
- **B002**: The extracted feature must support this observable behavior: hunk lines expose added/removed/context types. Required observable cases include hunk lines; context lines.
- **B003**: PatchSet raises UnidiffParseError for malformed or internally inconsistent short hunks while accepting valid patches containing multiple files.
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

- mapping: `B001, B003`
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

- mapping: `B004`
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
- API: `featurelifted.Hunk, featurelifted.LINE_TYPE_ADDED, featurelifted.LINE_TYPE_CONTEXT, featurelifted.LINE_TYPE_REMOVED, featurelifted.PatchSet, featurelifted.PatchedFile, featurelifted.UnidiffParseError, featurelifted.patch`
- risk: `none`
- A001 `assert` L16: `isinstance(PatchSet, type)`
- A002 `assert` L17: `hasattr(PatchSet, '__len__')`
- A003 `assert` L18: `hasattr(PatchSet, '__getitem__')`
- A004 `assert` L19: `hasattr(PatchSet, '__iter__')`
- A005 `assert` L20: `isinstance(PatchedFile, type)`
- A006 `assert` L21: `hasattr(PatchedFile, '__len__')`
- A007 `assert` L22: `hasattr(PatchedFile, '__getitem__')`
- A008 `assert` L23: `hasattr(PatchedFile, '__iter__')`
- A009 `assert` L24: `PatchedFile is not None`
- A010 `assert` L25: `PatchedFile is not None`
- A011 `assert` L26: `PatchedFile is not None`
- A012 `assert` L27: `isinstance(Hunk, type)`
- A013 `assert` L28: `hasattr(Hunk, '__iter__')`
- A014 `assert` L29: `issubclass(UnidiffParseError, BaseException)`
- A015 `assert` L30: `LINE_TYPE_ADDED is not None`
- A016 `assert` L31: `LINE_TYPE_REMOVED is not None`
- A017 `assert` L32: `LINE_TYPE_CONTEXT is not None`
- A018 `assert` L33: `isinstance(getattr(patch, 'Line'), type)`
- A019 `assert` L34: `getattr(patch, 'Line') is not None`
- A020 `assert` L35: `getattr(patch, 'Line') is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `unidiff`
- source entrypoints: `none`
- oracle source files: `unidiff/patch.py, unidiff/__init__.py`
- runtime dependencies: `none`
- oracle notes: Composite PatchSet + PatchedFile + Hunk model (W2 libcst native-blocked backup).
