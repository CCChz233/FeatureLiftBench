# setuptools_scm__version_normalize_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/5`

## Required API

- `featurelifted.version_from_scm` (function) `(root, *, tag: 'str' = 'v1.0.0', distance: 'int' = 0, dirty: 'bool' = False, node: 'str' = 'g1234567') -> 'str'`

## Public Behaviors

- **B001**: version_from_scm normalizes SCM-style tags into a valid base version and incorporates distance, dirty state, and node information.
- **B002**: When distance from the tag is positive, version_from_scm appends the corresponding development-distance suffix.
- **B003**: When node or dirty information is present, version_from_scm appends a normalized local version segment.
- **B004**: The package exposes the required task API paths `featurelifted.version_from_scm` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_version_from_tag`

- mapping: `B001`
- API: `featurelifted.version_from_scm`
- risk: `none`
- A001 `assert` L6: `version_from_scm('.', tag='v1.2.3', distance=0, dirty=False) == '1.2.3'`

### `hidden_tests/test_hidden_contract.py::test_distance_adds_dev_suffix`

- mapping: `B002`
- API: `featurelifted.version_from_scm`
- risk: `none`
- A001 `assert` L7: `version.startswith('1.0.1.dev3+')`

### `hidden_tests/test_hidden_contract.py::test_dirty_adds_local_suffix`

- mapping: `B003`
- API: `featurelifted.version_from_scm`
- risk: `none`
- A001 `assert` L12: `version.endswith('+g1234567')`

### `hidden_tests/test_hidden_contract.py::test_node_normalization`

- mapping: `B001, B003`
- API: `featurelifted.version_from_scm`
- risk: `none`
- A001 `assert` L17: `'+gabcdef0' in version`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.version_from_scm`
- risk: `none`
- A001 `assert` L9: `callable(version_from_scm)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `setuptools_scm`
- source entrypoints: `setuptools_scm.version.version_from_scm`
- oracle source files: `repo/setuptools-scm/src/setuptools_scm/version.py`
- runtime dependencies: `none`
- oracle notes: SCM version normalization without subprocess git.
