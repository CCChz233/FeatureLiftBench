# jinja2__loader_inheritance_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/11`

## Required API

- `featurelifted.Environment` (class) `(block_start_string: str = '{%', block_end_string: str = '%}', variable_start_string: str = '{{', variable_end_string: str = '}}', comment_start_string: str = '{#', comment_end_string: str = '#}', line_statement_prefix: Optional[str] = None, line_comment_prefix: Optional[str] = None, trim_blocks: bool = False, lstrip_blocks: bool = False, newline_sequence: "te.Literal['\\n', '\\r\\n', '\\r']" = '\n', keep_trailing_newline: bool = False, extensions: Sequence[Union[str, Type[ForwardRef('Extension')]]] = (), optimized: bool = True, undefined: Type[Undefined] = <class 'Undefined'>, finalize: Optional[Callable[..., Any]] = None, autoescape: Union[bool, Callable[[Optional[str]], bool]] = False, loader: Optional[ForwardRef('BaseLoader')] = None, cache_size: int = 400, auto_reload: bool = True, bytecode_cache: Optional[ForwardRef('BytecodeCache')] = None, enable_async: bool = False)`
- `featurelifted.Environment.get_template` (method) `(self, name: Union[str, ForwardRef('Template')], parent: Optional[str] = None, globals: Optional[MutableMapping[str, Any]] = None) -> 'Template'`
- `featurelifted.DictLoader` (class) `(mapping: Mapping[str, str]) -> None`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.TemplateNotFound` (exception)
- `featurelifted.loaders` (module)
- `featurelifted.loaders.BaseLoader` (class) `()`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: load templates via DictLoader and BaseLoader subclasses. Required observable cases include loader module required for missing template.
- **B002**: The extracted feature must support this observable behavior: resolve extends chains and block overrides. Required observable cases include extends overrides block; multi level inheritance.
- **B003**: The extracted feature must support this observable behavior: render nested block inheritance across multiple templates. Required observable cases include multi level inheritance; base loader subclass get source.
- **B004**: The extracted feature must support this observable behavior: support trim_blocks for layout templates. Required observable cases include multi level inheritance.
- **B005**: The package exposes the required task API paths `featurelifted.Environment`, `featurelifted.Environment.get_template`, `featurelifted.DictLoader`, `featurelifted.exceptions`, `featurelifted.exceptions.TemplateNotFound`, `featurelifted.loaders`, `featurelifted.loaders.BaseLoader` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_extends_overrides_block`

- mapping: `B002`
- API: `featurelifted.DictLoader, featurelifted.Environment`
- risk: `none`
- A001 `assert` L14: `env.get_template('child').render() == '|child|'`

### `hidden_tests/test_hidden_behavior.py::test_multi_level_inheritance`

- mapping: `B002, B003, B004`
- API: `featurelifted.DictLoader, featurelifted.Environment, featurelifted.loaders`
- risk: `none`
- A001 `assert` L15: `env.get_template('leaf').render() == '|ab|'`

### `hidden_tests/test_hidden_behavior.py::test_loader_module_required_for_missing_template`

- mapping: `B001`
- API: `featurelifted.DictLoader, featurelifted.Environment, featurelifted.exceptions, featurelifted.loaders`
- risk: `none`
- A001 `assert` L25: `'missing' in str(exc)`

### `hidden_tests/test_hidden_behavior.py::test_base_loader_subclass_get_source`

- mapping: `B003`
- API: `featurelifted.Environment, featurelifted.loaders`
- risk: `none`
- A001 `assert` L36: `env.get_template('x').render() == 'static'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.DictLoader, featurelifted.Environment, featurelifted.exceptions, featurelifted.loaders`
- risk: `none`
- A001 `assert` L12: `isinstance(Environment, type)`
- A002 `assert` L13: `hasattr(Environment, 'get_template')`
- A003 `assert` L14: `isinstance(DictLoader, type)`
- A004 `assert` L15: `exceptions is not None`
- A005 `assert` L16: `issubclass(getattr(exceptions, 'TemplateNotFound'), BaseException)`
- A006 `assert` L17: `loaders is not None`
- A007 `assert` L18: `isinstance(getattr(loaders, 'BaseLoader'), type)`

## Dependency / Oracle Evidence

- allowed dependencies: `MarkupSafe`
- forbidden imports: `jinja2, jinja`
- source entrypoints: `jinja2.loaders.BaseLoader, jinja2.loaders.DictLoader, jinja2.environment.Environment.get_template, jinja2.environment.Template.render`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Loader + inheritance closure includes compile/render stack and DictLoader.
