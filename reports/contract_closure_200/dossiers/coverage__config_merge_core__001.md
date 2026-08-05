# coverage__config_merge_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `7/15`

## Required API

- `featurelifted.CoverageConfig` (class) `() -> 'None'`
- `featurelifted.read_run_config` (function) `(config_file: bool | str = True, warn=None, **kwargs)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: read .coveragerc and prefixed sections from setup.cfg or tox.ini. Required observable cases include read run config from coveragerc; read run config from setup cfg; read run config relative files section.
- **B002**: The extracted feature must support this observable behavior: parse run include, omit, source, branch, and related list options. Required observable cases include read run config multiline lists; read run config relative files section.
- **B003**: The extracted feature must support this observable behavior: merge constructor kwargs and COVERAGE_* environment overrides. Required observable cases include read run config kwargs override; read run config env data file.
- **B004**: The extracted feature must support this observable behavior: apply post-processing such as user path expansion. Required observable cases include read run config relative files section.
- **B005**: The package exposes the required task API paths `featurelifted.CoverageConfig`, `featurelifted.read_run_config` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_read_run_config_from_coveragerc`

- mapping: `B001`
- API: `featurelifted.read_run_config`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L22: `config.branch is True`
- A002 `assert` L23: `config.run_include == ['alpha', 'beta']`
- A003 `assert` L24: `config.run_omit == ['*/tests/*']`
- A004 `assert` L25: `config.source == ['src']`

### `public_tests/test_public_api.py::test_read_run_config_kwargs_override`

- mapping: `B003`
- API: `featurelifted.read_run_config`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L37: `config.branch is True`
- A002 `assert` L38: `config.run_include == ['from_args']`

### `hidden_tests/test_hidden_behavior.py::test_read_run_config_from_setup_cfg`

- mapping: `B001`
- API: `featurelifted.read_run_config`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L21: `config.run_omit == ['one', 'two']`
- A002 `assert` L22: `config.source_pkgs == ['pkg.a', 'pkg.b']`
- A003 `assert` L23: `config.parallel is True`

### `hidden_tests/test_hidden_behavior.py::test_read_run_config_env_data_file`

- mapping: `B003`
- API: `featurelifted.read_run_config`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L36: `config.data_file == 'custom.dat'`

### `hidden_tests/test_hidden_behavior.py::test_read_run_config_multiline_lists`

- mapping: `B002`
- API: `featurelifted.read_run_config`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L52: `config.run_include == ['first', 'second', 'third']`

### `hidden_tests/test_hidden_behavior.py::test_read_run_config_relative_files_section`

- mapping: `B001, B002, B004`
- API: `featurelifted.read_run_config`
- risk: `environment_state, filesystem_resource`
- A001 `assert` L66: `config.relative_files is True`
- A002 `assert` L67: `'no-data-collected' in config.disable_warnings`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.CoverageConfig, featurelifted.read_run_config`
- risk: `none`
- A001 `assert` L10: `isinstance(CoverageConfig, type)`
- A002 `assert` L11: `callable(read_run_config)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `coverage`
- source entrypoints: `coverage.config.read_coverage_config, coverage.config.CoverageConfig.from_file, coverage.config.CoverageConfig.from_args`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Run-section configuration reading and merge closure including INI/TOML parsers and CoverageConfig.
