# hatch__project_metadata_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/9`

## Required API

- `featurelifted.normalize_project_metadata` (function) `(project: 'dict') -> 'dict'`
- `featurelifted.select_environment` (function) `(envs: 'dict', name: 'str') -> 'dict'`
- `featurelifted.MetadataValidationError` (exception)

## Public Behaviors

- **B001**: `normalize_project_metadata` lowercases names, sorts dependencies, and validates classifiers.
- **B002**: `select_environment` resolves environment inheritance and include chains.
- **B003**: Circular inheritance raises `ValueError`; invalid classifiers raise `MetadataValidationError`.
- **B004**: The package exposes the required task API paths `featurelifted.normalize_project_metadata`, `featurelifted.select_environment`, `featurelifted.MetadataValidationError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_normalize_project_metadata`

- mapping: `B001`
- API: `featurelifted.normalize_project_metadata`
- risk: `none`
- A001 `assert` L12: `normalized['name'] == 'my-package'`
- A002 `assert` L13: `normalized['dependencies'] == ['click>=8', 'requests>=2']`

### `hidden_tests/test_hidden_contract.py::test_select_environment_inheritance`

- mapping: `B001, B002`
- API: `featurelifted.select_environment`
- risk: `none`
- A001 `assert` L13: `resolved['dependencies'] == ['requests']`
- A002 `assert` L14: `resolved['scripts']['pytest'] == 'pytest'`

### `hidden_tests/test_hidden_contract.py::test_circular_environment_raises`

- mapping: `B002`
- API: `featurelifted.select_environment`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L19: `pytest.raises(ValueError, match='circular')`

### `hidden_tests/test_hidden_contract.py::test_invalid_classifier_raises`

- mapping: `B003`
- API: `featurelifted.MetadataValidationError, featurelifted.normalize_project_metadata`
- risk: `exception_semantics`
- A001 `raises` L24: `pytest.raises(MetadataValidationError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.MetadataValidationError, featurelifted.normalize_project_metadata, featurelifted.select_environment`
- risk: `none`
- A001 `assert` L11: `callable(normalize_project_metadata)`
- A002 `assert` L12: `callable(select_environment)`
- A003 `assert` L13: `issubclass(MetadataValidationError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `hatch, hatchling`
- source entrypoints: `hatchling.metadata.core.normalize_project_metadata`
- oracle source files: `repo/backend/src/hatchling/metadata/core.py`
- runtime dependencies: `none`
- oracle notes: Hatchling metadata subset without build runner.
