# python_dotenv__env_parse_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `16/20`

## Required API

- `featurelifted.dotenv_values` (function) `(dotenv_path: Union[str, ForwardRef('os.PathLike[str]'), NoneType] = None, stream: Optional[IO[str]] = None, verbose: bool = False, interpolate: bool = True, encoding: Optional[str] = 'utf-8') -> Dict[str, Optional[str]]`
- `featurelifted.set_key` (function) `(dotenv_path: Union[str, ForwardRef('os.PathLike[str]')], key_to_set: str, value_to_set: str, quote_mode: str = 'always', export: bool = False, encoding: Optional[str] = 'utf-8', follow_symlinks: bool = False) -> Tuple[Optional[bool], str, str]`
- `featurelifted.get_key` (function) `(dotenv_path: Union[str, ForwardRef('os.PathLike[str]')], key_to_get: str, encoding: Optional[str] = 'utf-8') -> Optional[str]`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse key=value pairs from stream with export prefix and comments. Required observable cases include dotenv values simple pairs; dotenv values export prefix; inline comment after whitespace; key without value is none.
- **B002**: The extracted feature must support this observable behavior: single- and double-quoted values with escape sequences. Required observable cases include dotenv values quoted value; double quote escape sequences; single quote escape only backslash and quote.
- **B003**: The extracted feature must support this observable behavior: UTF-8 BOM stripping at file start. Required observable cases include utf8 bom stripped.
- **B004**: The extracted feature must support this observable behavior: POSIX ${VAR} and ${VAR:-default} variable interpolation. Required observable cases include variable interpolation chain; variable default when missing.
- **B005**: The extracted feature must support this observable behavior: set_key creates or updates keys with auto-quoting. Required observable cases include set key creates file; set key updates existing; set key quotes special characters; set key appends without trailing newline.
- **B006**: The package exposes the required task API paths `featurelifted.dotenv_values`, `featurelifted.set_key`, `featurelifted.get_key` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_dotenv_values_simple_pairs`

- mapping: `B001`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L10: `dotenv_values(stream=stream) == {'FOO': 'bar', 'BAZ': 'qux'}`

### `public_tests/test_public_api.py::test_dotenv_values_quoted_value`

- mapping: `B002`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L15: `dotenv_values(stream=stream) == {'GREETING': 'hello world'}`

### `public_tests/test_public_api.py::test_dotenv_values_export_prefix`

- mapping: `B001`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L20: `dotenv_values(stream=stream) == {'PORT': '8000'}`

### `public_tests/test_public_api.py::test_set_key_creates_file`

- mapping: `B005`
- API: `featurelifted.set_key`
- risk: `filesystem_resource`
- A001 `assert` L26: `result == (True, 'API_KEY', 'secret')`
- A002 `assert` L27: `env_path.read_text() == "API_KEY='secret'\n"`

### `public_tests/test_public_api.py::test_set_key_updates_existing`

- mapping: `B005`
- API: `featurelifted.dotenv_values, featurelifted.set_key`
- risk: `filesystem_resource, state_mutation`
- A001 `assert` L34: `dotenv_values(stream=io.StringIO(env_path.read_text())) == {'FOO': 'new'}`

### `hidden_tests/test_hidden_behavior.py::test_double_quote_escape_sequences`

- mapping: `B002`
- API: `featurelifted.dotenv_values`
- risk: `ordering_semantics`
- A001 `assert` L14: `dotenv_values(stream=stream)['a'] == 'b\nc'`

### `hidden_tests/test_hidden_behavior.py::test_single_quote_escape_only_backslash_and_quote`

- mapping: `B002`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L19: `dotenv_values(stream=stream)['a'] == 'b\\nc'`

### `hidden_tests/test_hidden_behavior.py::test_utf8_bom_stripped`

- mapping: `B003`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L24: `dotenv_values(stream=stream) == {'KEY': 'value'}`

### `hidden_tests/test_hidden_behavior.py::test_inline_comment_after_whitespace`

- mapping: `B001`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L29: `dotenv_values(stream=stream) == {'FOO': 'bar'}`

### `hidden_tests/test_hidden_behavior.py::test_key_without_value_is_none`

- mapping: `B001`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L34: `dotenv_values(stream=stream) == {'EMPTY_VAR': None}`

### `hidden_tests/test_hidden_behavior.py::test_variable_interpolation_chain`

- mapping: `B004`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L39: `dotenv_values(stream=stream)['FULL'] == 'hello world'`

### `hidden_tests/test_hidden_behavior.py::test_variable_default_when_missing`

- mapping: `B004`
- API: `featurelifted.dotenv_values`
- risk: `none`
- A001 `assert` L44: `dotenv_values(stream=stream)['X'] == 'fallback'`

### `hidden_tests/test_hidden_behavior.py::test_set_key_quotes_special_characters`

- mapping: `B005`
- API: `featurelifted.set_key`
- risk: `filesystem_resource`
- A001 `assert` L50: `env_path.read_text() == 'MSG=\'say "hi"\'\n'`

### `hidden_tests/test_hidden_behavior.py::test_set_key_appends_without_trailing_newline`

- mapping: `B005`
- API: `featurelifted.dotenv_values, featurelifted.set_key`
- risk: `filesystem_resource`
- A001 `assert` L58: `text == "A=1\nB='2'\n"`
- A002 `assert` L59: `dotenv_values(stream=io.StringIO(text)) == {'A': '1', 'B': '2'}`

### `hidden_tests/test_hidden_behavior.py::test_no_dotenv_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L69: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.dotenv_values, featurelifted.get_key, featurelifted.set_key`
- risk: `none`
- A001 `assert` L11: `callable(dotenv_values)`
- A002 `assert` L12: `callable(set_key)`
- A003 `assert` L13: `callable(get_key)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `dotenv`
- source entrypoints: `dotenv.dotenv_values, dotenv.set_key, dotenv.get_key, dotenv.parser.parse_stream, dotenv.variables.parse_variables, dotenv.main.DotEnv`
- oracle source files: `src/dotenv/parser.py, src/dotenv/variables.py, src/dotenv/main.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies parser, variables, and main modules; excludes CLI and IPython helpers.
