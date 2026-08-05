# cookiecutter__repo_finder_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/11`

## Required API

- `featurelifted.RepoFinder` (class) `(*, abbreviations: 'dict[str, str] | None' = None, template_root: 'str' = '/templates', replay_dir: 'str' = '/replay') -> 'None'`
- `featurelifted.RepoFinder.find_template` (method) `(self, repo_spec: 'str', replay: 'dict[str, str] | None' = None) -> 'dict[str, str | bool]'`
- `featurelifted.expand_abbreviation` (function) `(repo: 'str', abbreviations: 'dict[str, str]') -> 'str'`
- `featurelifted.safe_join` (function) `(base: 'str', *parts: 'str') -> 'str'`
- `featurelifted.UnsafePathError` (exception)

## Public Behaviors

- **B001**: When a repository abbreviation is supplied, expand_abbreviation and RepoFinder expand it using configured abbreviations before resolving the template path.
- **B002**: Abbreviations expand short repo prefixes; replay overrides take precedence.
- **B003**: `safe_join` rejects path traversal and absolute segments.
- **B004**: The package exposes the required task API paths `featurelifted.RepoFinder`, `featurelifted.RepoFinder.find_template`, `featurelifted.expand_abbreviation`, `featurelifted.safe_join`, `featurelifted.UnsafePathError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_find_template_with_abbreviation`

- mapping: `B001`
- API: `featurelifted.RepoFinder`
- risk: `none`
- A001 `assert` L8: `result['expanded'] == 'https://github.com/org/template.git'`
- A002 `assert` L9: `'org/template' in result['local_path']`

### `hidden_tests/test_hidden_contract.py::test_replay_override`

- mapping: `B002`
- API: `featurelifted.RepoFinder`
- risk: `none`
- A001 `assert` L10: `result['expanded'] == 'local/demo'`
- A002 `assert` L11: `result['replay_used'] is True`

### `hidden_tests/test_hidden_contract.py::test_nested_template_detection`

- mapping: `B004`
- API: `featurelifted.RepoFinder`
- risk: `none`
- A001 `assert` L17: `result['nested'] is True`

### `hidden_tests/test_hidden_contract.py::test_safe_join_rejects_parent_segments`

- mapping: `B001, B003`
- API: `featurelifted.UnsafePathError, featurelifted.safe_join`
- risk: `exception_semantics`
- A001 `raises` L21: `pytest.raises(UnsafePathError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.RepoFinder, featurelifted.UnsafePathError, featurelifted.expand_abbreviation, featurelifted.safe_join`
- risk: `none`
- A001 `assert` L12: `isinstance(RepoFinder, type)`
- A002 `assert` L13: `hasattr(RepoFinder, 'find_template')`
- A003 `assert` L14: `callable(expand_abbreviation)`
- A004 `assert` L15: `callable(safe_join)`
- A005 `assert` L16: `issubclass(UnsafePathError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `cookiecutter`
- source entrypoints: `cookiecutter.repository.RepoFinder`
- oracle source files: `repo/cookiecutter/repository.py, repo/cookiecutter/config.py`
- runtime dependencies: `none`
- oracle notes: Repository finder subset without git/network.
