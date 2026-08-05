# flake8__plugin_options_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/10`

## Required API

- `featurelifted.OptionManager` (class) `() -> 'None'`
- `featurelifted.PluginSpec` (class) `(name: 'str', codes: 'list[str]', checker_type: 'str', options: 'list[OptionSpec]' = <factory>) -> None`
- `featurelifted.classify_plugins` (function) `(plugins: 'list[PluginSpec]') -> 'Plugins'`
- `featurelifted.apply_select_ignore` (function) `(plugins: 'Plugins', select: 'set[str] | None', ignore: 'set[str] | None') -> 'Plugins'`
- `featurelifted.OptionSpec` (class) `(dest: 'str', parse_from_config: 'bool' = False, default: 'Any' = None) -> None`

## Public Behaviors

- **B001**: Register per-plugin options in `OptionManager`.
- **B002**: Classify plugins into tree, logical_line, and physical_line checker groups.
- **B003**: `apply_select_ignore` enables plugins whose codes intersect `select` and not `ignore`; when `select` is empty, ignore disables matching plugins.
- **B004**: The package exposes the required task API paths `featurelifted.OptionManager`, `featurelifted.PluginSpec`, `featurelifted.classify_plugins`, `featurelifted.apply_select_ignore`, `featurelifted.OptionSpec` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_option_manager_registers_plugin_options`

- mapping: `B001`
- API: `featurelifted.OptionManager, featurelifted.OptionSpec, featurelifted.PluginSpec`
- risk: `none`
- A001 `assert` L9: `manager.options['max_line_length'].default == 79`

### `public_tests/test_public_contract.py::test_classify_plugins_groups_checkers`

- mapping: `B001, B002`
- API: `featurelifted.PluginSpec, featurelifted.classify_plugins`
- risk: `none`
- A001 `assert` L17: `len(plugins.checkers.tree) == 1`
- A002 `assert` L18: `len(plugins.checkers.logical_line) == 1`

### `hidden_tests/test_hidden_contract.py::test_select_and_ignore_precedence`

- mapping: `B001, B002, B003`
- API: `featurelifted.PluginSpec, featurelifted.apply_select_ignore, featurelifted.classify_plugins`
- risk: `none`
- A001 `assert` L11: `[p.plugin.name for p in selected.checkers.logical_line] == ['a']`
- A002 `assert` L13: `[p.plugin.name for p in ignored.checkers.tree] == []`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.OptionManager, featurelifted.OptionSpec, featurelifted.PluginSpec, featurelifted.apply_select_ignore, featurelifted.classify_plugins`
- risk: `none`
- A001 `assert` L13: `isinstance(OptionManager, type)`
- A002 `assert` L14: `isinstance(PluginSpec, type)`
- A003 `assert` L15: `callable(classify_plugins)`
- A004 `assert` L16: `callable(apply_select_ignore)`
- A005 `assert` L17: `isinstance(OptionSpec, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `flake8`
- source entrypoints: `flake8.options.manager.OptionManager, flake8.plugins.finder.Plugins`
- oracle source files: `repo/src/flake8/options/manager.py, repo/src/flake8/plugins/finder.py`
- runtime dependencies: `none`
- oracle notes: Plugin planning subset without lint execution.
