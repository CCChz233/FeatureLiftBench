# poetry_core__dependency_groups_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/9`

## Required API

- `featurelifted.parse_project_dependencies` (function) `(project: 'dict') -> 'dict[str, DependencyGroup]'`
- `featurelifted.resolve_group` (function) `(name: 'str', groups: 'dict[str, DependencyGroup]', seen: 'set[str] | None' = None) -> 'list[DependencySpec]'`
- `featurelifted.DependencyGroup` (class) `(name: 'str', optional: 'bool' = False, dependencies: 'list[DependencySpec]' = <factory>, includes: 'list[str]' = <factory>) -> None`
- `featurelifted.DependencySpec` (class) `(name: 'str', constraint: 'str' = '*', optional: 'bool' = False, group: 'str | None' = None, marker: 'str | None' = None) -> None`

## Public Behaviors

- **B001**: `parse_project_dependencies` builds `DependencyGroup` objects from PEP 621 project metadata.
- **B002**: `resolve_group` resolves a group's dependencies including transitive `include-group` references.
- **B003**: Circular includes raise `ValueError`.
- **B004**: The package exposes the required task API paths `featurelifted.parse_project_dependencies`, `featurelifted.resolve_group`, `featurelifted.DependencyGroup`, `featurelifted.DependencySpec` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_parse_main_and_optional_groups`

- mapping: `B002, B003`
- API: `featurelifted.parse_project_dependencies, featurelifted.resolve_group`
- risk: `none`
- A001 `assert` L11: `'main' in groups`
- A002 `assert` L12: `groups['dev'].optional is True`
- A003 `assert` L13: `resolve_group('dev', groups)[0].name == 'pytest'`

### `hidden_tests/test_hidden_contract.py::test_dependency_group_includes`

- mapping: `B001, B002, B003`
- API: `featurelifted.parse_project_dependencies, featurelifted.resolve_group`
- risk: `none`
- A001 `assert` L17: `names == ['pytest', 'ruff']`

### `hidden_tests/test_hidden_contract.py::test_circular_include_group_raises`

- mapping: `B003`
- API: `featurelifted.parse_project_dependencies, featurelifted.resolve_group`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L28: `pytest.raises(ValueError, match='circular')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.DependencyGroup, featurelifted.DependencySpec, featurelifted.parse_project_dependencies, featurelifted.resolve_group`
- risk: `none`
- A001 `assert` L12: `callable(parse_project_dependencies)`
- A002 `assert` L13: `callable(resolve_group)`
- A003 `assert` L14: `isinstance(DependencyGroup, type)`
- A004 `assert` L15: `isinstance(DependencySpec, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `poetry, poetry_core`
- source entrypoints: `poetry.core.packages.dependency_group.DependencyGroup`
- oracle source files: `repo/src/poetry/core/packages/dependency_group.py, repo/src/poetry/core/factory.py`
- runtime dependencies: `none`
- oracle notes: Dependency group resolver subset without build backend.
