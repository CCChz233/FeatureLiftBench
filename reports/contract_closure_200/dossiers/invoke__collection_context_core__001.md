# invoke__collection_context_core__001

- release: `external50`
- lift: `Composite`
- coupling: `framework_coupling`
- strict validation: `PASS`
- tests/assertions: `6/14`

## Required API

- `featurelifted.task` (function)
- `featurelifted.Collection` (class)
- `featurelifted.Collection.add_task` (method)
- `featurelifted.Collection.add_collection` (method)
- `featurelifted.Context` (class)
- `featurelifted.MockContext` (class)
- `featurelifted.MockContext.run` (method)
- `featurelifted.UnexpectedExit` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: Collection task invocation with Context. Required observable cases include collection task call.
- **B002**: The extracted feature must support this observable behavior: MockContext stubs run without shell. Required observable cases include mock context run.
- **B003**: The extracted feature must support this observable behavior: nested collections and UnexpectedExit. Required observable cases include nested collection; task exception type.
- **B004**: Tasks are accessed via Collection.__getitem__ by name.
- **B005**: The package exposes task/Collection/Context/MockContext/UnexpectedExit with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: invoke.

## Tests

### `public_tests/test_public_api.py::test_collection_task_call`

- mapping: `B001`
- API: `featurelifted.Collection, featurelifted.Context`
- risk: `none`
- A001 `assert` L14: `ns['hello'](Context(), name='Ada') == 'hi Ada'`

### `public_tests/test_public_api.py::test_mock_context_run`

- mapping: `B002`
- API: `featurelifted.Collection, featurelifted.MockContext`
- risk: `none`
- A001 `assert` L27: `ns['run_cmd'](ctx) == 1`
- A002 `assert` L28: `ctx.run.called`

### `hidden_tests/test_hidden_behavior.py::test_nested_collection`

- mapping: `B001, B003, B004`
- API: `featurelifted.Collection, featurelifted.Context`
- risk: `none`
- A001 `assert` L16: `outer['tools.add'](Context(), 2, 3) == 5`

### `hidden_tests/test_hidden_behavior.py::test_task_exception_type`

- mapping: `B002`
- API: `featurelifted.Collection, featurelifted.Context, featurelifted.UnexpectedExit`
- risk: `none`
- A001 `assert` L29: `False`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L45: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Collection, featurelifted.Collection.add_collection, featurelifted.Collection.add_task, featurelifted.MockContext, featurelifted.MockContext.run`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'Collection')`
- A002 `assert` L6: `hasattr(featurelifted, 'Context')`
- A003 `assert` L7: `hasattr(featurelifted, 'MockContext')`
- A004 `assert` L8: `hasattr(featurelifted, 'UnexpectedExit')`
- A005 `assert` L9: `hasattr(featurelifted, 'task')`
- A006 `assert` L10: `callable(featurelifted.Collection.add_task)`
- A007 `assert` L11: `callable(featurelifted.Collection.add_collection)`
- A008 `assert` L12: `callable(featurelifted.MockContext.run)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `invoke`
- source entrypoints: `none`
- oracle source files: `invoke/collection.py, invoke/context.py, invoke/tasks.py`
- runtime dependencies: `none`
- oracle notes: Composite @task + Collection + Context/MockContext; no real shell.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
