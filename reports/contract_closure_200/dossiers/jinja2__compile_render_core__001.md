# jinja2__compile_render_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/12`

## Required API

- `featurelifted.Environment` (class) `(block_start_string: str = '{%', block_end_string: str = '%}', variable_start_string: str = '{{', variable_end_string: str = '}}', comment_start_string: str = '{#', comment_end_string: str = '#}', line_statement_prefix: Optional[str] = None, line_comment_prefix: Optional[str] = None, trim_blocks: bool = False, lstrip_blocks: bool = False, newline_sequence: "te.Literal['\\n', '\\r\\n', '\\r']" = '\n', keep_trailing_newline: bool = False, extensions: Sequence[Union[str, Type[ForwardRef('Extension')]]] = (), optimized: bool = True, undefined: Type[Undefined] = <class 'Undefined'>, finalize: Optional[Callable[..., Any]] = None, autoescape: Union[bool, Callable[[Optional[str]], bool]] = False, loader: Optional[ForwardRef('BaseLoader')] = None, cache_size: int = 400, auto_reload: bool = True, bytecode_cache: Optional[ForwardRef('BytecodeCache')] = None, enable_async: bool = False)`
- `featurelifted.Environment.from_string` (method) `(self, source: Union[str, Template], globals: Optional[MutableMapping[str, Any]] = None, template_class: Optional[Type[ForwardRef('Template')]] = None) -> 'Template'`
- `featurelifted.Environment.parse` (method) `(self, source: str, name: Optional[str] = None, filename: Optional[str] = None) -> Template`
- `featurelifted.compiler` (module)
- `featurelifted.compiler.generate` (function) `(node: Template, environment: 'Environment', name: Optional[str], filename: Optional[str], stream: Optional[TextIO] = None, defer_init: bool = False, optimized: bool = True) -> Optional[str]`
- `featurelifted.runtime` (module)
- `featurelifted.runtime.Context` (class) `(environment: 'Environment', parent: Dict[str, Any], name: Optional[str], blocks: Dict[str, Callable[[ForwardRef('Context')], Iterator[str]]], globals: Optional[MutableMapping[str, Any]] = None)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: compile template source to executable code. Required observable cases include runtime context exported vars.
- **B002**: The extracted feature must support this observable behavior: render templates with context variables. Required observable cases include render simple interpolation; render if for blocks; macro render and caller; runtime context exported vars.
- **B003**: The extracted feature must support this observable behavior: support if/for/set/macro blocks and expressions. Required observable cases include render if for blocks; macro render and caller; compiler module required for set block.
- **B004**: The extracted feature must support this observable behavior: preserve undefined variable behavior with default Undefined. Required observable cases include runtime context exported vars.
- **B005**: The package exposes the required task API paths `featurelifted.Environment`, `featurelifted.Environment.from_string`, `featurelifted.Environment.parse`, `featurelifted.compiler`, `featurelifted.compiler.generate`, `featurelifted.runtime`, `featurelifted.runtime.Context` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_render_simple_interpolation`

- mapping: `B002`
- API: `featurelifted.Environment`
- risk: `none`
- A001 `assert` L7: `tmpl.render(name='World') == 'Hello World!'`

### `public_tests/test_public_api.py::test_render_if_for_blocks`

- mapping: `B002, B003`
- API: `featurelifted.Environment`
- risk: `none`
- A001 `assert` L15: `tmpl.render(items=[1, 0, 2]) == '12'`

### `hidden_tests/test_hidden_behavior.py::test_macro_render_and_caller`

- mapping: `B002, B003`
- API: `featurelifted.Environment, featurelifted.compiler, featurelifted.runtime`
- risk: `none`
- A001 `assert` L11: `tmpl.render() == 'Hi Ann'`

### `hidden_tests/test_hidden_behavior.py::test_compiler_module_required_for_set_block`

- mapping: `B003`
- API: `featurelifted.Environment, featurelifted.compiler, featurelifted.runtime`
- risk: `none`
- A001 `assert` L18: `'x' in source`

### `hidden_tests/test_hidden_behavior.py::test_runtime_context_exported_vars`

- mapping: `B001, B002, B004`
- API: `featurelifted.Environment, featurelifted.compiler, featurelifted.runtime`
- risk: `none`
- A001 `assert` L24: `tmpl.render() == '5'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Environment, featurelifted.compiler, featurelifted.runtime`
- risk: `none`
- A001 `assert` L11: `isinstance(Environment, type)`
- A002 `assert` L12: `hasattr(Environment, 'from_string')`
- A003 `assert` L13: `hasattr(Environment, 'parse')`
- A004 `assert` L14: `compiler is not None`
- A005 `assert` L15: `callable(getattr(compiler, 'generate'))`
- A006 `assert` L16: `runtime is not None`
- A007 `assert` L17: `isinstance(getattr(runtime, 'Context'), type)`

## Dependency / Oracle Evidence

- allowed dependencies: `MarkupSafe`
- forbidden imports: `jinja2, jinja`
- source entrypoints: `jinja2.environment.Environment.from_string, jinja2.environment.Environment.compile, jinja2.environment.Template.render, jinja2.compiler, jinja2.runtime`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Compile/render closure without loaders or extensions.
