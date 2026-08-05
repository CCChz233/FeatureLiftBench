# jinja2__extensions_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `6/13`

## Required API

- `featurelifted.Environment` (class) `(block_start_string: str = '{%', block_end_string: str = '%}', variable_start_string: str = '{{', variable_end_string: str = '}}', comment_start_string: str = '{#', comment_end_string: str = '#}', line_statement_prefix: Optional[str] = None, line_comment_prefix: Optional[str] = None, trim_blocks: bool = False, lstrip_blocks: bool = False, newline_sequence: "te.Literal['\\n', '\\r\\n', '\\r']" = '\n', keep_trailing_newline: bool = False, extensions: Sequence[Union[str, Type[ForwardRef('Extension')]]] = (), optimized: bool = True, undefined: Type[Undefined] = <class 'Undefined'>, finalize: Optional[Callable[..., Any]] = None, autoescape: Union[bool, Callable[[Optional[str]], bool]] = False, loader: Optional[ForwardRef('BaseLoader')] = None, cache_size: int = 400, auto_reload: bool = True, bytecode_cache: Optional[ForwardRef('BytecodeCache')] = None, enable_async: bool = False)`
- `featurelifted.Environment.from_string` (method) `(self, source: Union[str, Template], globals: Optional[MutableMapping[str, Any]] = None, template_class: Optional[Type[ForwardRef('Template')]] = None) -> 'Template'`
- `featurelifted.Environment.iter_extensions` (method) `(self) -> Iterator[ForwardRef('Extension')]`
- `featurelifted.Extension` (class) `(environment: Environment) -> None`
- `featurelifted.nodes` (module)
- `featurelifted.ext` (module)
- `featurelifted.ext.do` (function) `(environment: Environment) -> None`
- `featurelifted.ext.loopcontrols` (function) `(environment: Environment) -> None`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: load extensions by import path string or Extension subclass. Required observable cases include preprocess extension rewrites delimiters.
- **B002**: The extracted feature must support this observable behavior: register extension tags and preprocessors with Environment. Required observable cases include preprocess extension rewrites delimiters; custom extension tag renders.
- **B003**: The extracted feature must support this observable behavior: iterate extensions in priority order. Required observable cases include extension ordering by priority.
- **B004**: The extracted feature must support this observable behavior: render templates using bundled loopcontrols and do extensions. Required observable cases include loopcontrols extension breaks loop; do extension executes side effect; preprocess extension rewrites delimiters; custom extension tag renders.
- **B005**: The package exposes the required task API paths `featurelifted.Environment`, `featurelifted.Environment.from_string`, `featurelifted.Environment.iter_extensions`, `featurelifted.Extension`, `featurelifted.nodes`, `featurelifted.ext`, `featurelifted.ext.do`, `featurelifted.ext.loopcontrols` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_loopcontrols_extension_breaks_loop`

- mapping: `B004`
- API: `featurelifted.Environment, featurelifted.ext.loopcontrols`
- risk: `none`
- A001 `assert` L9: `tmpl.render() == '012'`

### `public_tests/test_public_api.py::test_do_extension_executes_side_effect`

- mapping: `B004`
- API: `featurelifted.Environment, featurelifted.ext.do`
- risk: `none`
- A001 `assert` L15: `tmpl.render() == '1'`

### `hidden_tests/test_hidden_behavior.py::test_extension_ordering_by_priority`

- mapping: `B003`
- API: `featurelifted.Environment, featurelifted.Extension`
- risk: `ordering_semantics`
- A001 `assert` L37: `ordered == [_T1, _T2]`

### `hidden_tests/test_hidden_behavior.py::test_preprocess_extension_rewrites_delimiters`

- mapping: `B001, B002, B004`
- API: `featurelifted.Environment`
- risk: `none`
- A001 `assert` L43: `tmpl.render(name='Ann') == 'Ann'`

### `hidden_tests/test_hidden_behavior.py::test_custom_extension_tag_renders`

- mapping: `B002, B004`
- API: `featurelifted.Environment`
- risk: `none`
- A001 `assert` L49: `tmpl.render() == 'HI:world'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Environment, featurelifted.Extension, featurelifted.ext, featurelifted.nodes`
- risk: `none`
- A001 `assert` L12: `isinstance(Environment, type)`
- A002 `assert` L13: `hasattr(Environment, 'from_string')`
- A003 `assert` L14: `hasattr(Environment, 'iter_extensions')`
- A004 `assert` L15: `isinstance(Extension, type)`
- A005 `assert` L16: `nodes is not None`
- A006 `assert` L17: `ext is not None`
- A007 `assert` L18: `callable(getattr(ext, 'do'))`
- A008 `assert` L19: `callable(getattr(ext, 'loopcontrols'))`

## Dependency / Oracle Evidence

- allowed dependencies: `MarkupSafe`
- forbidden imports: `jinja2, jinja`
- source entrypoints: `jinja2.environment.load_extensions, jinja2.environment.Environment.extensions, jinja2.ext.Extension`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Compile/render core plus ext.py for extension loading and registration.

## Machine Issues

- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.nodes.CallBlock
