# stevedore__extension_manager_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `9/29`

## Required API

- `featurelifted.EntryPointSpec` (class) `(name: 'str', value: 'str', group: 'str', loader: 'Callable[[], Any] | None' = None) -> None`
- `featurelifted.ExtensionManager` (class) `(namespace: 'str', entry_points: 'Iterable[Any] | None' = None, invoke_on_load: 'bool' = False, invoke_args: 'tuple[Any, ...] | None' = None, invoke_kwds: 'dict[str, Any] | None' = None, propagate_map_exceptions: 'bool' = False, on_load_failure_callback: "Callable[['ExtensionManager', Any, BaseException], None] | None" = None, *, conflict_resolver: 'Callable[[str, str, list[Extension]], Extension]' = <function ignore_conflicts>) -> 'None'`
- `featurelifted.ExtensionManager.map` (method) `(self, func: 'Callable[..., Any]', *args: 'Any', **kwds: 'Any') -> 'list[Any]'`
- `featurelifted.ExtensionManager.names` (method) `(self) -> 'list[str]'`
- `featurelifted.ExtensionManager.namespace` (attribute)
- `featurelifted.NamedExtensionManager` (class) `(namespace: 'str', names: 'Iterable[str]', entry_points: 'Iterable[Any] | None' = None, invoke_on_load: 'bool' = False, invoke_args: 'tuple[Any, ...] | None' = None, invoke_kwds: 'dict[str, Any] | None' = None, name_order: 'bool' = False, propagate_map_exceptions: 'bool' = False, on_load_failure_callback: 'Callable[[ExtensionManager, Any, BaseException], None] | None' = None, on_missing_entrypoints_callback: 'Callable[[Iterable[str]], None] | None' = None, *, conflict_resolver: 'Callable[[str, str, list[Extension]], Extension]' = <function ignore_conflicts>) -> 'None'`
- `featurelifted.NamedExtensionManager.names` (method) `(self) -> 'list[str]'`
- `featurelifted.NoMatches` (exception)
- `featurelifted.MultipleMatches` (exception)
- `featurelifted.error_on_conflict` (function) `(namespace: 'str', name: 'str', entrypoints)`
- `featurelifted.ignore_conflicts` (function) `(namespace: 'str', name: 'str', entrypoints)`
- `featurelifted.Extension` (class) `(name: 'str', entry_point: 'Any', plugin: 'Any', obj: 'Any') -> 'None'`
- `featurelifted.Extension.obj` (attribute)

## Public Behaviors

- **B001**: EntryPointSpec supplies deterministic entry-point name, namespace, and loader behavior for extension discovery.
- **B002**: Loaded extensions retain their name, entry point, plugin, and optional invoked object for lookup and iteration.
- **B003**: ExtensionManager filters entry points by namespace, loads matching plugins, and omits unrelated entry points.
- **B004**: With invoke_on_load enabled, ExtensionManager invokes the plugin with invoke_args and invoke_kwds and stores the resulting object.
- **B005**: When plugin loading fails, on_load_failure_callback receives the manager, entry point, and exception and the failed extension is skipped.
- **B006**: names, items, iteration, containment, and keyed lookup expose the manager's successfully loaded extensions.
- **B007**: map and map_method invoke callbacks across loaded extensions and preserve or propagate results and configured exceptions.
- **B008**: Duplicate names follow ignore_conflicts or raise MultipleMatches under error_on_conflict.
- **B009**: NamedExtensionManager filters requested names, reports missing names through its callback, and can preserve requested order.
- **B010**: The package exposes the required task API paths `featurelifted.EntryPointSpec`, `featurelifted.ExtensionManager`, `featurelifted.ExtensionManager.map`, `featurelifted.ExtensionManager.names`, `featurelifted.ExtensionManager.namespace`, `featurelifted.NamedExtensionManager`, `featurelifted.NamedExtensionManager.names`, `featurelifted.NoMatches`, `featurelifted.MultipleMatches`, `featurelifted.error_on_conflict`, `featurelifted.ignore_conflicts`, `featurelifted.Extension`, and 1 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_extension_manager_loads_matching_namespace`

- mapping: `B003`
- API: `featurelifted.EntryPointSpec, featurelifted.ExtensionManager`
- risk: `none`
- A001 `assert` L22: `manager.names() == ['alpha']`
- A002 `assert` L23: `'alpha' in manager`
- A003 `assert` L24: `manager['alpha'].plugin is Plugin`
- A004 `assert` L25: `manager['alpha'].entry_point_target == 'plugins:Alpha'`

### `public_tests/test_public_contract.py::test_invoke_on_load_and_map_method`

- mapping: `B004, B007`
- API: `featurelifted.EntryPointSpec, featurelifted.ExtensionManager`
- risk: `none`
- A001 `assert` L32: `manager.map_method('label', 'value') == ['pre-value']`

### `public_tests/test_public_contract.py::test_map_raises_no_matches_when_empty`

- mapping: `B007`
- API: `featurelifted.ExtensionManager, featurelifted.NoMatches`
- risk: `exception_semantics`
- A001 `raises` L38: `pytest.raises(NoMatches)`

### `hidden_tests/test_hidden_contract.py::test_load_failure_callback_gets_manager_entrypoint_and_exception`

- mapping: `B005`
- API: `featurelifted.EntryPointSpec, featurelifted.ExtensionManager`
- risk: `none`
- A001 `assert` L38: `manager.names() == ['good']`
- A002 `assert` L39: `seen == [('demo', 'bad', 'ImportError', 'missing optional dependency')]`

### `hidden_tests/test_hidden_contract.py::test_duplicate_names_default_to_last_extension`

- mapping: `B002, B008`
- API: `featurelifted.EntryPointSpec, featurelifted.ExtensionManager`
- risk: `none`
- A001 `assert` L50: `manager.names() == ['dup', 'dup']`
- A002 `assert` L51: `manager['dup'].plugin is PluginB`

### `hidden_tests/test_hidden_contract.py::test_duplicate_names_can_raise_multiple_matches`

- mapping: `B008`
- API: `featurelifted.EntryPointSpec, featurelifted.ExtensionManager, featurelifted.MultipleMatches, featurelifted.error_on_conflict`
- risk: `exception_semantics`
- A001 `raises` L62: `pytest.raises(MultipleMatches)`

### `hidden_tests/test_hidden_contract.py::test_map_exception_policy_can_ignore_or_propagate`

- mapping: `B007`
- API: `featurelifted.EntryPointSpec, featurelifted.ExtensionManager`
- risk: `exact_error_text, exception_semantics`
- A001 `assert` L80: `tolerant.map(mapper) == ['b']`
- A002 `raises` L81: `pytest.raises(RuntimeError, match='skip')`

### `hidden_tests/test_hidden_contract.py::test_named_extension_manager_filters_reports_missing_and_orders_names`

- mapping: `B001, B003, B004, B006, B009`
- API: `featurelifted.EntryPointSpec, featurelifted.NamedExtensionManager`
- risk: `ordering_semantics`
- A001 `assert` L101: `manager.names() == ['b', 'a']`
- A002 `assert` L102: `missing == ['missing']`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B010`
- API: `featurelifted.EntryPointSpec, featurelifted.Extension, featurelifted.ExtensionManager, featurelifted.MultipleMatches, featurelifted.NamedExtensionManager, featurelifted.NoMatches, featurelifted.error_on_conflict, featurelifted.ignore_conflicts`
- risk: `none`
- A001 `assert` L16: `isinstance(EntryPointSpec, type)`
- A002 `assert` L17: `isinstance(ExtensionManager, type)`
- A003 `assert` L18: `hasattr(ExtensionManager, 'map')`
- A004 `assert` L19: `hasattr(ExtensionManager, 'names')`
- A005 `assert` L20: `ExtensionManager is not None`
- A006 `assert` L21: `isinstance(NamedExtensionManager, type)`
- A007 `assert` L22: `hasattr(NamedExtensionManager, 'names')`
- A008 `assert` L23: `issubclass(NoMatches, BaseException)`
- A009 `assert` L24: `issubclass(MultipleMatches, BaseException)`
- A010 `assert` L25: `callable(error_on_conflict)`
- A011 `assert` L26: `callable(ignore_conflicts)`
- A012 `assert` L27: `isinstance(Extension, type)`
- A013 `assert` L28: `Extension is not None`
- A014 `assert` L30: `hasattr(extension, 'obj')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `stevedore`
- source entrypoints: `stevedore.extension.ExtensionManager, stevedore.extension.Extension, stevedore.extension.ignore_conflicts, stevedore.extension.error_on_conflict, stevedore.named.NamedExtensionManager`
- oracle source files: `repo/stevedore/__init__.py, repo/stevedore/extension.py, repo/stevedore/named.py, repo/stevedore/exception.py, repo/stevedore/_cache.py`
- runtime dependencies: `none`
- oracle notes: Task-scoped extension manager extraction. Driver, dispatch, hook, Sphinx, and examples are intentionally excluded.
