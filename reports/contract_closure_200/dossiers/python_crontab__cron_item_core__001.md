# python_crontab__cron_item_core__001

- release: `external50`
- lift: `Adapted`
- coupling: `parser_state_coupling`
- strict validation: `PASS`
- tests/assertions: `7/20`

## Required API

- `featurelifted.CronSlices` (class)
- `featurelifted.CronSlices.is_valid` (method)
- `featurelifted.CronSlices.setall` (method)
- `featurelifted.CronSlices.render` (method)
- `featurelifted.CronSlices.special` (attribute)
- `featurelifted.CronSlices.is_valid` (method)
- `featurelifted.CronItem` (class)
- `featurelifted.CronItem.render` (method)
- `featurelifted.CronItem.is_valid` (method)
- `featurelifted.CronItem.is_enabled` (method)
- `featurelifted.CronItem.render` (method)
- `featurelifted.CronItem.is_valid` (method)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: CronSlices parse/render/is_valid. Required observable cases include cron slices valid; slices setall.
- **B002**: The extracted feature must support this observable behavior: CronItem constructor render/is_valid. Required observable cases include cron item from line; cron item invalid line.
- **B003**: The extracted feature must support this observable behavior: special @reboot slices. Required observable cases include special reboot.
- **B004**: No OS crontab file access is required.
- **B005**: The package exposes CronSlices/CronItem with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: crontab.

## Tests

### `public_tests/test_public_api.py::test_cron_slices_valid`

- mapping: `B001`
- API: `featurelifted.CronSlices, featurelifted.CronSlices.is_valid`
- risk: `none`
- A001 `assert` L7: `CronSlices.is_valid('* * * * *')`
- A002 `assert` L9: `slices.render().startswith('*')`

### `public_tests/test_public_api.py::test_cron_item_from_line`

- mapping: `B002`
- API: `featurelifted.CronItem`
- risk: `none`
- A001 `assert` L14: `item.is_valid()`
- A002 `assert` L16: `'/bin/echo' in rendered or 'echo' in rendered`
- A003 `assert` L17: `item.is_enabled()`

### `public_tests/test_public_api.py::test_cron_item_invalid_line`

- mapping: `B003`
- API: `featurelifted.CronSlices, featurelifted.CronSlices.is_valid`
- risk: `none`
- A001 `assert` L21: `not CronSlices.is_valid('not five fields')`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L13: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_hidden_behavior.py::test_slices_setall`

- mapping: `B001, B002, B004`
- API: `featurelifted.CronSlices`
- risk: `none`
- A001 `assert` L22: `'0' in slices.render() and '12' in slices.render()`

### `hidden_tests/test_hidden_behavior.py::test_special_reboot`

- mapping: `B003`
- API: `featurelifted.CronSlices`
- risk: `none`
- A001 `assert` L27: `'@reboot' in slices.render() or slices.special == '@reboot'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.CronItem, featurelifted.CronItem.is_enabled, featurelifted.CronItem.is_valid, featurelifted.CronItem.render, featurelifted.CronSlices, featurelifted.CronSlices.is_valid, featurelifted.CronSlices.render, featurelifted.CronSlices.setall`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'CronItem')`
- A002 `assert` L6: `hasattr(featurelifted, 'CronSlices')`
- A003 `assert` L7: `callable(featurelifted.CronSlices.is_valid)`
- A004 `assert` L8: `callable(featurelifted.CronSlices.setall)`
- A005 `assert` L9: `callable(featurelifted.CronSlices.render)`
- A006 `assert` L10: `callable(featurelifted.CronSlices.is_valid)`
- A007 `assert` L11: `callable(featurelifted.CronItem.render)`
- A008 `assert` L12: `callable(featurelifted.CronItem.is_valid)`
- A009 `assert` L13: `callable(featurelifted.CronItem.is_enabled)`
- A010 `assert` L14: `callable(featurelifted.CronItem.render)`
- A011 `assert` L15: `callable(featurelifted.CronItem.is_valid)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `crontab`
- source entrypoints: `none`
- oracle source files: `crontab.py, crontabs.py, cronlog.py`
- runtime dependencies: `none`
- oracle notes: Wheel flat modules for CronSlices/CronItem without system crontab IO.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
