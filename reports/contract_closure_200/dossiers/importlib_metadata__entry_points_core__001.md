# importlib_metadata__entry_points_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `4/19`

## Required API

- `featurelifted.EntryPoint` (class) `(name: 'str', value: 'str', group: 'str') -> 'None'`
- `featurelifted.EntryPoint.name` (attribute)
- `featurelifted.EntryPoint.value` (attribute)
- `featurelifted.EntryPoints` (class) `(iterable=(), /)`
- `featurelifted.EntryPoints.select` (method) `(self, **params)`
- `featurelifted.PathDistribution` (class) `(path: 'SimplePath') -> 'None'`
- `featurelifted.PathDistribution.entry_points` (attribute)
- `featurelifted.Sectioned` (class) `()`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse entry point definitions from metadata. Required observable cases include path distribution entry points.
- **B002**: The extracted feature must support this observable behavior: select entry points by group and name. Required observable cases include entry point value parsing and selection; path distribution entry points.
- **B003**: The extracted feature must support this observable behavior: load entry point targets. Required observable cases include path distribution entry points.
- **B004**: The extracted feature must support this observable behavior: read entry points from PathDistribution metadata directories. Required observable cases include path distribution entry points.
- **B005**: The extracted feature must support this observable behavior: parse INI-style sectioned entry point config. Required observable cases include entry point value parsing and selection; sectioned entry point config; path distribution entry points.
- **B006**: The package exposes the required task API paths `featurelifted.EntryPoint`, `featurelifted.EntryPoint.name`, `featurelifted.EntryPoint.value`, `featurelifted.EntryPoints`, `featurelifted.EntryPoints.select`, `featurelifted.PathDistribution`, `featurelifted.PathDistribution.entry_points`, `featurelifted.Sectioned` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_entry_point_value_parsing_and_selection`

- mapping: `B002, B005`
- API: `featurelifted.EntryPoint, featurelifted.EntryPoints, featurelifted.EntryPoints.select`
- risk: `none`
- A001 `assert` L8: `ep.module == 'pkg.mod'`
- A002 `assert` L9: `ep.attr == 'main'`
- A003 `assert` L11: `len(selected) == 1`
- A004 `assert` L12: `selected['console'].matches(name='console', group='console_scripts')`

### `public_tests/test_public_api.py::test_sectioned_entry_point_config`

- mapping: `B005`
- API: `featurelifted.Sectioned, featurelifted.Sectioned.section_pairs`
- risk: `none`
- A001 `assert` L21: `pairs[0].name == 'console_scripts'`
- A002 `assert` L22: `pairs[0].value.name == 'tool'`
- A003 `assert` L23: `pairs[0].value.value == 'pkg.tool:run'`

### `hidden_tests/test_hidden_behavior.py::test_path_distribution_entry_points`

- mapping: `B001, B002, B003, B004, B005`
- API: `featurelifted.EntryPoint, featurelifted.EntryPoints, featurelifted.PathDistribution`
- risk: `filesystem_resource`
- A001 `assert` L28: `len(eps.select(group='console_scripts')) == 1`
- A002 `assert` L30: `isinstance(ep, EntryPoint)`
- A003 `assert` L31: `ep.name == 'demo'`
- A004 `assert` L32: `ep.value == 'demo.cli:main'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.EntryPoint, featurelifted.EntryPoints, featurelifted.PathDistribution, featurelifted.Sectioned`
- risk: `none`
- A001 `assert` L12: `isinstance(EntryPoint, type)`
- A002 `assert` L13: `EntryPoint is not None`
- A003 `assert` L14: `EntryPoint is not None`
- A004 `assert` L15: `isinstance(EntryPoints, type)`
- A005 `assert` L16: `hasattr(EntryPoints, 'select')`
- A006 `assert` L17: `isinstance(PathDistribution, type)`
- A007 `assert` L18: `PathDistribution is not None`
- A008 `assert` L19: `isinstance(Sectioned, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `importlib_metadata`
- source entrypoints: `importlib_metadata.entry_points, importlib_metadata.EntryPoint, importlib_metadata.EntryPoints, importlib_metadata.PathDistribution, importlib_metadata.Sectioned`
- oracle source files: `none`
- runtime dependencies: `none`

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.Sectioned.section_pairs
