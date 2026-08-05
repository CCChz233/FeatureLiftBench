# jinja2__filters_tests_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `7/18`

## Required API

- `featurelifted.Environment` (class) `(block_start_string: str = '{%', block_end_string: str = '%}', variable_start_string: str = '{{', variable_end_string: str = '}}', comment_start_string: str = '{#', comment_end_string: str = '#}', line_statement_prefix: Optional[str] = None, line_comment_prefix: Optional[str] = None, trim_blocks: bool = False, lstrip_blocks: bool = False, newline_sequence: "te.Literal['\\n', '\\r\\n', '\\r']" = '\n', keep_trailing_newline: bool = False, extensions: Sequence[Union[str, Type[ForwardRef('Extension')]]] = (), optimized: bool = True, undefined: Type[Undefined] = <class 'Undefined'>, finalize: Optional[Callable[..., Any]] = None, autoescape: Union[bool, Callable[[Optional[str]], bool]] = False, loader: Optional[ForwardRef('BaseLoader')] = None, cache_size: int = 400, auto_reload: bool = True, bytecode_cache: Optional[ForwardRef('BytecodeCache')] = None, enable_async: bool = False)`
- `featurelifted.Environment.call_filter` (method) `(self, name: str, value: Any, args: Optional[Sequence[Any]] = None, kwargs: Optional[Mapping[str, Any]] = None, context: Optional[Context] = None, eval_ctx: Optional[EvalContext] = None) -> Any`
- `featurelifted.Environment.call_test` (method) `(self, name: str, value: Any, args: Optional[Sequence[Any]] = None, kwargs: Optional[Mapping[str, Any]] = None, context: Optional[Context] = None, eval_ctx: Optional[EvalContext] = None) -> Any`
- `featurelifted.Environment.from_string` (method) `(self, source: Union[str, Template], globals: Optional[MutableMapping[str, Any]] = None, template_class: Optional[Type[ForwardRef('Template')]] = None) -> 'Template'`
- `featurelifted.filters` (module)
- `featurelifted.tests` (module)
- `featurelifted.runtime` (module)
- `featurelifted.runtime.Undefined` (class) `(hint: Optional[str] = None, obj: Any = missing, name: Optional[str] = None, exc: Type[TemplateRuntimeError] = <class 'UndefinedError'>) -> None`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: apply built-in filters in templates and via call_filter. Required observable cases include capitalize filter in template; call filter directly; defined test in template.
- **B002**: The extracted feature must support this observable behavior: evaluate built-in tests in templates and via call_test. Required observable cases include defined test in template.
- **B003**: The extracted feature must support this observable behavior: support common filters: capitalize, default, length, join, map, select. Required observable cases include capitalize filter in template; default filter with boolean; filters module required for join.
- **B004**: The extracted feature must support this observable behavior: support common tests: defined, undefined, even, odd, number, string. Required observable cases include tests module required for even.
- **B005**: The extracted feature must support this observable behavior: default filter honors boolean true to treat falsey values as missing. Required observable cases include default filter with boolean.
- **B006**: The extracted feature must support this observable behavior: runtime Undefined and filters/tests registries must be available for call_filter/call_test. Required observable cases include call filter directly; tests module required for even.
- **B007**: The package exposes the required task API paths `featurelifted.Environment`, `featurelifted.Environment.call_filter`, `featurelifted.Environment.call_test`, `featurelifted.Environment.from_string`, `featurelifted.filters`, `featurelifted.tests`, `featurelifted.runtime`, `featurelifted.runtime.Undefined` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_capitalize_filter_in_template`

- mapping: `B001, B003`
- API: `featurelifted.Environment`
- risk: `none`
- A001 `assert` L7: `tmpl.render() == 'Hello'`

### `public_tests/test_public_api.py::test_call_filter_directly`

- mapping: `B001, B006`
- API: `featurelifted.Environment`
- risk: `none`
- A001 `assert` L12: `env.call_filter('upper', 'abc') == 'ABC'`

### `hidden_tests/test_hidden_behavior.py::test_default_filter_with_boolean`

- mapping: `B003, B005`
- API: `featurelifted.Environment`
- risk: `none`
- A001 `assert` L9: `tmpl.render() == 'no'`

### `hidden_tests/test_hidden_behavior.py::test_defined_test_in_template`

- mapping: `B001, B002`
- API: `featurelifted.Environment, featurelifted.runtime`
- risk: `none`
- A001 `assert` L16: `env.call_test('defined', 1) is True`
- A002 `assert` L17: `env.call_test('undefined', Undefined()) is True`
- A003 `assert` L18: `env.call_test('even', 4) is True`

### `hidden_tests/test_hidden_behavior.py::test_filters_module_required_for_join`

- mapping: `B003`
- API: `featurelifted.Environment, featurelifted.filters, featurelifted.filters.FILTERS`
- risk: `none`
- A001 `assert` L23: `env.call_filter('join', ['a', 'b'], ':') == 'a:b'`
- A002 `assert` L24: `'join' in filters.FILTERS`

### `hidden_tests/test_hidden_behavior.py::test_tests_module_required_for_even`

- mapping: `B004, B006`
- API: `featurelifted.Environment, featurelifted.tests, featurelifted.tests.TESTS`
- risk: `none`
- A001 `assert` L29: `env.call_test('even', 4) is True`
- A002 `assert` L30: `'even' in jinja_tests.TESTS`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.Environment, featurelifted.filters, featurelifted.runtime, featurelifted.tests`
- risk: `none`
- A001 `assert` L12: `isinstance(Environment, type)`
- A002 `assert` L13: `hasattr(Environment, 'call_filter')`
- A003 `assert` L14: `hasattr(Environment, 'call_test')`
- A004 `assert` L15: `hasattr(Environment, 'from_string')`
- A005 `assert` L16: `filters is not None`
- A006 `assert` L17: `tests is not None`
- A007 `assert` L18: `runtime is not None`
- A008 `assert` L19: `isinstance(getattr(runtime, 'Undefined'), type)`

## Dependency / Oracle Evidence

- allowed dependencies: `MarkupSafe`
- forbidden imports: `jinja2, jinja`
- source entrypoints: `jinja2.filters.FILTERS, jinja2.tests.TESTS, jinja2.environment.Environment.call_filter, jinja2.environment.Environment.call_test`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Filters/tests with compile/render support for template usage.

## Machine Issues

- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.filters.FILTERS
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.tests.TESTS
