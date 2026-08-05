# omegaconf__merge_interpolate_core__001

- release: `external50`
- lift: `Composite`
- coupling: `config_environment_coupling`
- strict validation: `PASS`
- tests/assertions: `9/20`

## Required API

- `featurelifted.OmegaConf.create` (method)
- `featurelifted.OmegaConf.merge` (method)
- `featurelifted.OmegaConf.to_container` (method)
- `featurelifted.OmegaConf.select` (method)
- `featurelifted.OmegaConf.resolve` (method)
- `featurelifted.OmegaConf.is_missing` (method)
- `featurelifted.OmegaConf.is_config` (method)
- `featurelifted.OmegaConf.set_struct` (method)
- `featurelifted.errors.InterpolationResolutionError` (exception)
- `featurelifted.errors.ConfigKeyError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: create/merge/to_container with interpolation resolve and select. Required observable cases include create merge resolve; select.
- **B002**: The extracted feature must support this observable behavior: is_missing/is_config helpers and resolve inplace. Required observable cases include is helpers; resolve inplace.
- **B003**: The extracted feature must support this observable behavior: InterpolationResolutionError and struct-mode key errors. Required observable cases include interpolation error; struct mode key error.
- **B004**: ListConfig merge replaces list values as upstream default merge semantics used in tests.
- **B005**: The package exposes the required OmegaConf methods and InterpolationResolutionError/ConfigKeyError with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: omegaconf.

## Tests

### `public_tests/test_public_api.py::test_create_merge_resolve`

- mapping: `B001`
- API: `featurelifted.OmegaConf, featurelifted.OmegaConf.create, featurelifted.OmegaConf.merge, featurelifted.OmegaConf.to_container`
- risk: `none`
- A001 `assert` L10: `OmegaConf.to_container(m, resolve=True) == {'x': 1, 'y': 1, 'z': 2}`

### `public_tests/test_public_api.py::test_select`

- mapping: `B002`
- API: `featurelifted.OmegaConf, featurelifted.OmegaConf.create, featurelifted.OmegaConf.select`
- risk: `none`
- A001 `assert` L15: `OmegaConf.select(cfg, 'a.b') == 3`
- A002 `assert` L16: `OmegaConf.select(cfg, 'a.c', default=9) == 9`

### `public_tests/test_public_api.py::test_is_helpers`

- mapping: `B003`
- API: `featurelifted.OmegaConf, featurelifted.OmegaConf.create, featurelifted.OmegaConf.is_config, featurelifted.OmegaConf.is_missing, featurelifted.OmegaConf.select`
- risk: `none`
- A001 `assert` L21: `OmegaConf.is_missing(cfg, 'm')`
- A002 `assert` L22: `OmegaConf.select(cfg, 'n') is None`
- A003 `assert` L23: `OmegaConf.is_config(cfg)`

### `hidden_tests/test_hidden_behavior.py::test_resolve_inplace`

- mapping: `B001`
- API: `featurelifted.OmegaConf, featurelifted.OmegaConf.create, featurelifted.OmegaConf.resolve, featurelifted.errors`
- risk: `none`
- A001 `assert` L14: `cfg.b == 1`

### `hidden_tests/test_hidden_behavior.py::test_interpolation_error`

- mapping: `B002`
- API: `featurelifted.OmegaConf, featurelifted.OmegaConf.create, featurelifted.OmegaConf.to_container, featurelifted.errors`
- risk: `exception_semantics`
- A001 `raises` L19: `pytest.raises(InterpolationResolutionError)`

### `hidden_tests/test_hidden_behavior.py::test_struct_mode_key_error`

- mapping: `B003`
- API: `featurelifted.OmegaConf, featurelifted.OmegaConf.create, featurelifted.OmegaConf.set_struct, featurelifted.errors`
- risk: `exception_semantics`
- A001 `raises` L26: `pytest.raises((ConfigKeyError, KeyError, Exception))`

### `hidden_tests/test_hidden_behavior.py::test_list_config_merge`

- mapping: `B004`
- API: `featurelifted.OmegaConf, featurelifted.OmegaConf.create, featurelifted.OmegaConf.merge, featurelifted.OmegaConf.to_container, featurelifted.errors`
- risk: `none`
- A001 `assert` L34: `OmegaConf.to_container(m)['items'] == [3]`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__, featurelifted.errors`
- risk: `filesystem_resource`
- A001 `assert` L43: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.OmegaConf, featurelifted.errors`
- risk: `none`
- A001 `assert` L6: `hasattr(OmegaConf, 'create')`
- A002 `assert` L7: `hasattr(OmegaConf, 'merge')`
- A003 `assert` L8: `hasattr(OmegaConf, 'to_container')`
- A004 `assert` L9: `hasattr(OmegaConf, 'select')`
- A005 `assert` L10: `hasattr(OmegaConf, 'resolve')`
- A006 `assert` L11: `hasattr(OmegaConf, 'is_missing')`
- A007 `assert` L12: `hasattr(OmegaConf, 'is_config')`
- A008 `assert` L13: `hasattr(OmegaConf, 'set_struct')`
- A009 `assert` L14: `InterpolationResolutionError is not None and ConfigKeyError is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `antlr4-python3-runtime, pyyaml`
- forbidden imports: `omegaconf`
- source entrypoints: `none`
- oracle source files: `omegaconf/omegaconf.py, omegaconf/base.py, omegaconf/grammar/`
- runtime dependencies: `antlr4-python3-runtime, pyyaml`
- oracle notes: repo git tree omits generated grammar/gen; reference uses release wheel artifacts.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
