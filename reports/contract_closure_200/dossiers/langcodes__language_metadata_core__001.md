# langcodes__language_metadata_core__001

- release: `external50`
- lift: `Composite`
- coupling: `third_party_dependency_coupling`
- strict validation: `PASS`
- tests/assertions: `7/11`

## Required API

- `featurelifted.Language` (class)
- `featurelifted.Language.get` (method) `(tag, normalize=True) -> Language`
- `featurelifted.Language.to_tag` (method) `() -> str`
- `featurelifted.Language.language_name` (method) `(language=None) -> str`
- `featurelifted.Language.maximize` (method) `() -> Language`
- `featurelifted.Language.script` (attribute)
- `featurelifted.standardize_tag` (function) `(tag, macro: bool = False) -> str`
- `featurelifted.best_match` (function) `(desired_language, supported_languages, min_score=0) -> tuple[str, int]`

## Public Behaviors

- **B001**: standardize_tag and Language.get normalize overlong, deprecated, script, and territory subtags.
- **B002**: language_name and maximize resolve localized CLDR metadata from the locked language-data package offline.
- **B003**: best_match ranks supported language tags using normalized language distance and returns a score.
- **B004**: The submitted package uses only locked language-data and marisa-trie dependencies and does not import langcodes.

## Tests

### `public_tests/test_public_api.py::test_standardize_and_language_object`

- mapping: `B001`
- API: `featurelifted.Language, featurelifted.Language.get, featurelifted.standardize_tag`
- risk: `none`
- A001 `assert` L5: `standardize_tag('eng_US') == 'en-US'`
- A002 `assert` L7: `language.to_tag() == 'zh-Hant'`

### `public_tests/test_public_api.py::test_cldr_name_and_maximize`

- mapping: `B002`
- API: `featurelifted.Language, featurelifted.Language.get, featurelifted.Language.language_name, featurelifted.Language.maximize, featurelifted.Language.script`
- risk: `none`
- A001 `assert` L11: `Language.get('fr').language_name('en') == 'French'`
- A002 `assert` L12: `Language.get('zh-TW').maximize().script == 'Hant'`

### `hidden_tests/test_hidden_behavior.py::test_deprecated_tag_normalization`

- mapping: `B001`
- API: `featurelifted.standardize_tag`
- risk: `none`
- A001 `assert` L5: `standardize_tag('en-uk') == 'en-GB'`

### `hidden_tests/test_hidden_behavior.py::test_hidden_cldr_name_lookup`

- mapping: `B002`
- API: `featurelifted.Language, featurelifted.Language.get, featurelifted.Language.language_name`
- risk: `none`
- A001 `assert` L9: `Language.get('de').language_name('en') == 'German'`

### `hidden_tests/test_hidden_behavior.py::test_best_match_prefers_closest_supported_tag`

- mapping: `B003`
- API: `featurelifted.best_match`
- risk: `none`
- A001 `assert` L14: `match == 'en-GB' and score > 0`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.Language, featurelifted.best_match, featurelifted.standardize_tag`
- risk: `none`
- A001 `assert` L19: `isinstance(Language, type)`
- A002 `assert` L20: `all((callable(getattr(Language, n)) for n in ('get', 'to_tag', 'language_name', 'maximize')))`
- A003 `assert` L21: `callable(standardize_tag) and callable(best_match)`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L30: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `language-data, marisa-trie`
- forbidden imports: `langcodes`
- source entrypoints: `none`
- oracle source files: `langcodes/__init__.py, langcodes/language_distance.py, langcodes/data_dicts.py`
- runtime dependencies: `language-data, marisa-trie`
- oracle notes: Balanced Python-200 replacement slot resource-composite-third-party-03; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
