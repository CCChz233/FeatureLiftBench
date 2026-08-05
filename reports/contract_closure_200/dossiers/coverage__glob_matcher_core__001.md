# coverage__glob_matcher_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `8/18`

## Required API

- `featurelifted.GlobMatcher` (class) `(pats: 'Iterable[str]', name: 'str' = 'unknown') -> 'None'`
- `featurelifted.GlobMatcher.match` (method) `(self, fpath: 'str') -> 'bool'`
- `featurelifted.prep_patterns` (function) `(patterns: 'Iterable[str]') -> 'list[str]'`
- `featurelifted.globs_to_regex` (function) `(patterns: 'Iterable[str]', case_insensitive: 'bool' = False, partial: 'bool' = False) -> 're.Pattern[str]'`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.ConfigError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: prepare relative and absolute glob patterns for matching. Required observable cases include glob matcher matches simple patterns; prep patterns adds absolute path; glob matcher many patterns; glob matcher backslash pattern; glob matcher question mark single char.
- **B002**: The extracted feature must support this observable behavior: match file paths against include/omit style glob lists. Required observable cases include glob matcher respects windows style paths; glob matcher question mark single char.
- **B003**: The extracted feature must support this observable behavior: convert glob syntax to compiled regex with Windows slash tolerance. Required observable cases include glob matcher respects windows style paths.
- **B004**: The extracted feature must support this observable behavior: reject invalid glob patterns such as triple-star segments. Required observable cases include glob matcher matches simple patterns; globs to regex rejects invalid pattern; glob matcher many patterns; glob matcher backslash pattern.
- **B005**: The package exposes the required task API paths `featurelifted.GlobMatcher`, `featurelifted.GlobMatcher.match`, `featurelifted.prep_patterns`, `featurelifted.globs_to_regex`, `featurelifted.exceptions`, `featurelifted.exceptions.ConfigError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_glob_matcher_matches_simple_patterns`

- mapping: `B001, B004`
- API: `featurelifted.GlobMatcher, featurelifted.exceptions`
- risk: `filesystem_resource`
- A001 `assert` L21: `matcher.match(str(py_file)) is True`
- A002 `assert` L22: `matcher.match(str(root / 'sub' / 'file2.c')) is False`

### `public_tests/test_public_api.py::test_prep_patterns_adds_absolute_path`

- mapping: `B001`
- API: `featurelifted.exceptions, featurelifted.prep_patterns`
- risk: `filesystem_resource`
- A001 `assert` L35: `rel in patterns`
- A002 `assert` L36: `any((os.path.isabs(pattern) for pattern in patterns))`

### `public_tests/test_public_api.py::test_globs_to_regex_rejects_invalid_pattern`

- mapping: `B004`
- API: `featurelifted.exceptions, featurelifted.globs_to_regex`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L40: `pytest.raises(ConfigError, match="can't include")`

### `hidden_tests/test_hidden_behavior.py::test_glob_matcher_respects_windows_style_paths`

- mapping: `B002, B003`
- API: `featurelifted.GlobMatcher`
- risk: `filesystem_resource`
- A001 `assert` L15: `matcher.match(str(target)) is True`
- A002 `assert` L16: `matcher.match(os.path.join('dir', 'foo.py')) is True`

### `hidden_tests/test_hidden_behavior.py::test_glob_matcher_many_patterns`

- mapping: `B001, B004`
- API: `featurelifted.GlobMatcher`
- risk: `filesystem_resource`
- A001 `assert` L21: `matcher.match('x123foo.txt') is True`
- A002 `assert` L22: `matcher.match('x798bar.txt') is False`

### `hidden_tests/test_hidden_behavior.py::test_glob_matcher_backslash_pattern`

- mapping: `B001, B004`
- API: `featurelifted.GlobMatcher`
- risk: `filesystem_resource`
- A001 `assert` L27: `matcher.match('dir\\foo.py') is True`

### `hidden_tests/test_hidden_behavior.py::test_glob_matcher_question_mark_single_char`

- mapping: `B001, B002`
- API: `featurelifted.GlobMatcher`
- risk: `none`
- A001 `assert` L32: `matcher.match('file1.py') is True`
- A002 `assert` L33: `matcher.match('file12.py') is False`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.GlobMatcher, featurelifted.exceptions, featurelifted.globs_to_regex, featurelifted.prep_patterns`
- risk: `none`
- A001 `assert` L12: `isinstance(GlobMatcher, type)`
- A002 `assert` L13: `hasattr(GlobMatcher, 'match')`
- A003 `assert` L14: `callable(prep_patterns)`
- A004 `assert` L15: `callable(globs_to_regex)`
- A005 `assert` L16: `exceptions is not None`
- A006 `assert` L17: `issubclass(getattr(exceptions, 'ConfigError'), BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `coverage`
- source entrypoints: `coverage.files.prep_patterns, coverage.files.GlobMatcher, coverage.files.globs_to_regex`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Glob matching closure: prep_patterns, GlobMatcher, globs_to_regex and supporting path/regex helpers from files.py.
