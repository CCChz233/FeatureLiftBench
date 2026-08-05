# sphinx__extension_registry_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/11`

## Required API

- `featurelifted.ComponentRegistry` (class) `() -> 'None'`
- `featurelifted.ComponentRegistry.add_directive` (method) `(self, name: 'str', directive: 'Any', override: 'bool' = False) -> 'None'`
- `featurelifted.ComponentRegistry.directives` (attribute)
- `featurelifted.ComponentRegistry.load_extension` (method) `(self, name: 'str', setup: "Callable[['ComponentRegistry'], ExtensionMetadata]") -> 'ExtensionMetadata'`
- `featurelifted.ExtensionMetadata` (class) `(version: 'str' = '1.0', parallel_read_safe: 'bool' = True, parallel_write_safe: 'bool' = True) -> None`
- `featurelifted.ExtensionError` (exception)

## Public Behaviors

- **B001**: `add_directive` and `add_role` register components; duplicates raise `ExtensionError` unless `override=True`.
- **B002**: `load_extension` invokes a setup callable, records the extension, and returns `ExtensionMetadata`.
- **B003**: Setup failures are wrapped in `ExtensionError`.
- **B004**: The package exposes the required task API paths `featurelifted.ComponentRegistry`, `featurelifted.ComponentRegistry.add_directive`, `featurelifted.ComponentRegistry.directives`, `featurelifted.ComponentRegistry.load_extension`, `featurelifted.ExtensionMetadata`, `featurelifted.ExtensionError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_load_extension_registers_metadata`

- mapping: `B002`
- API: `featurelifted.ComponentRegistry, featurelifted.ExtensionMetadata`
- risk: `none`
- A001 `assert` L13: `metadata.version == '1.2'`
- A002 `assert` L14: `'demo' in registry.directives`

### `hidden_tests/test_hidden_contract.py::test_duplicate_directive_requires_override`

- mapping: `B001, B003`
- API: `featurelifted.ComponentRegistry, featurelifted.ExtensionError`
- risk: `exception_semantics`
- A001 `raises` L10: `pytest.raises(ExtensionError)`
- A002 `assert` L13: `registry.directives['demo'] is list`

### `hidden_tests/test_hidden_contract.py::test_setup_errors_are_wrapped`

- mapping: `B002, B003`
- API: `featurelifted.ComponentRegistry, featurelifted.ExtensionError`
- risk: `exact_error_text, exception_semantics`
- A001 `raises` L22: `pytest.raises(ExtensionError, match='setup failed')`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.ComponentRegistry, featurelifted.ExtensionError, featurelifted.ExtensionMetadata`
- risk: `none`
- A001 `assert` L11: `isinstance(ComponentRegistry, type)`
- A002 `assert` L12: `hasattr(ComponentRegistry, 'add_directive')`
- A003 `assert` L13: `ComponentRegistry is not None`
- A004 `assert` L14: `hasattr(ComponentRegistry, 'load_extension')`
- A005 `assert` L15: `isinstance(ExtensionMetadata, type)`
- A006 `assert` L16: `issubclass(ExtensionError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `sphinx`
- source entrypoints: `sphinx.registry.SphinxComponentRegistry`
- oracle source files: `repo/sphinx/registry.py, repo/sphinx/extension.py, repo/sphinx/errors.py`
- runtime dependencies: `none`
- oracle notes: Registry/setup subset without builders or application startup.
