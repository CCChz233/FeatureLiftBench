# venusian__scan_dispatch_core__001

- release: `external50`
- lift: `Composite`
- coupling: `framework_coupling`
- strict validation: `PASS`
- tests/assertions: `6/9`

## Required API

- `featurelifted.attach` (function) `(wrapped, callback, category=None, depth=1, name=None) -> AttachInfo`
- `featurelifted.Scanner` (class) `(**context)`
- `featurelifted.Scanner.scan` (method) `(package, categories=None, onerror=None, ignore=None) -> None`
- `featurelifted.AttachInfo` (class)
- `featurelifted.lift` (class)

## Public Behaviors

- **B001**: attach records a callback on a function or class without replacing the wrapped object.
- **B002**: Scanner.scan discovers attached objects in a module and dispatches callbacks with scanner context, name, and object.
- **B003**: Category filters select only matching registrations while preserving deterministic callback order.
- **B004**: The submitted package does not import venusian or scan the network or unrelated filesystem paths.

## Tests

### `public_tests/test_public_api.py::test_attach_and_scan_current_module`

- mapping: `B002`
- API: `featurelifted.Scanner, featurelifted.Scanner.scan, featurelifted.attach`
- risk: `none`
- A001 `assert` L13: `seen == [(7, '_flb_target', target)]`

### `public_tests/test_public_api.py::test_category_filtering`

- mapping: `B003`
- API: `featurelifted.Scanner, featurelifted.Scanner.scan, featurelifted.attach`
- risk: `none`
- A001 `assert` L26: `seen == ['b']`

### `hidden_tests/test_hidden_behavior.py::test_attach_returns_info_and_preserves_object`

- mapping: `B001`
- API: `featurelifted.AttachInfo, featurelifted.attach`
- risk: `none`
- A001 `assert` L9: `target is original and isinstance(info, AttachInfo)`

### `hidden_tests/test_hidden_behavior.py::test_callback_order_with_same_category`

- mapping: `B002, B003`
- API: `featurelifted.Scanner, featurelifted.Scanner.scan, featurelifted.attach, featurelifted.lift`
- risk: `ordering_semantics`
- A001 `assert` L20: `seen == [1, 2]`
- A002 `assert` L21: `isinstance(lift, type)`

### `hidden_tests/test_hidden_behavior.py::test_required_api_surface`

- mapping: `B003`
- API: `featurelifted.AttachInfo, featurelifted.Scanner, featurelifted.Scanner.scan, featurelifted.attach, featurelifted.lift`
- risk: `none`
- A001 `assert` L28: `callable(attach)`
- A002 `assert` L29: `isinstance(Scanner, type) and callable(Scanner.scan)`
- A003 `assert` L30: `isinstance(AttachInfo, type) and isinstance(lift, type)`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B004`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L39: `not pattern.search(path.read_text(encoding='utf-8'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `venusian`
- source entrypoints: `none`
- oracle source files: `src/venusian/__init__.py, src/venusian/advice.py`
- runtime dependencies: `none`
- oracle notes: Balanced Python-200 replacement slot registry-composite-framework-01; offline reference only.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
