# astroid__nodes_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/17`

## Required API

- `featurelifted.parse` (function) `(code: 'str', module_name: 'str' = '', path: 'str | None' = None, apply_transforms: 'bool' = True) -> 'nodes.Module'`
- `featurelifted.ClassDef` (class) `(name=None, doc: 'str | None' = None, lineno=None, col_offset=None, parent=None, *, end_lineno=None, end_col_offset=None)`
- `featurelifted.FunctionDef` (class) `(name=None, doc: 'str | None' = None, lineno=None, col_offset=None, parent=None, *, end_lineno=None, end_col_offset=None)`
- `featurelifted.AsyncFunctionDef` (class) `(name=None, doc: 'str | None' = None, lineno=None, col_offset=None, parent=None, *, end_lineno=None, end_col_offset=None)`
- `featurelifted.Match` (class) `(lineno: 'int | None' = None, col_offset: 'int | None' = None, parent: 'NodeNG | None' = None, *, end_lineno: 'int | None' = None, end_col_offset: 'int | None' = None) -> 'None'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse Python source into astroid Module trees. Required observable cases include parse function and class; module as string contains def.
- **B002**: The extracted feature must support this observable behavior: rebuild functions, classes, async, and match statements. Required observable cases include async and match statements.
- **B003**: The extracted feature must support this observable behavior: preserve docstrings, annotations, and default arguments. Required observable cases include defaults and docstring.
- **B004**: The extracted feature must support this observable behavior: NodeNG as_string and basic structural attributes. Required observable cases include module as string contains def.
- **B005**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.ClassDef`, `featurelifted.FunctionDef`, `featurelifted.AsyncFunctionDef`, `featurelifted.Match` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_function_and_class`

- mapping: `B001`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L13: `cls.name == 'C'`
- A002 `assert` L15: `fn.name == 'm'`
- A003 `assert` L16: `fn.returns.as_string() == 'int'`

### `hidden_tests/test_hidden_behavior.py::test_async_and_match_statements`

- mapping: `B002`
- API: `featurelifted.parse`
- risk: `state_mutation`
- A001 `assert` L8: `async_mod.body[0].name == 'f'`
- A002 `assert` L10: `await_node.value.func.name == 'g'`
- A003 `assert` L14: `match_stmt.__class__.__name__ == 'Match'`
- A004 `assert` L15: `match_stmt.cases[0].pattern.value.value == 1`

### `hidden_tests/test_hidden_behavior.py::test_defaults_and_docstring`

- mapping: `B003`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L27: `cls.doc_node.value == 'docstring'`
- A002 `assert` L29: `fn.args.annotations[1].as_string() == 'int'`
- A003 `assert` L30: `fn.args.defaults[0].value == 1`

### `hidden_tests/test_hidden_behavior.py::test_module_as_string_contains_def`

- mapping: `B001, B004`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L36: `'def f' in text`
- A002 `assert` L37: `'return 1' in text`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.AsyncFunctionDef, featurelifted.ClassDef, featurelifted.FunctionDef, featurelifted.Match, featurelifted.parse`
- risk: `none`
- A001 `assert` L13: `callable(parse)`
- A002 `assert` L14: `isinstance(ClassDef, type)`
- A003 `assert` L15: `isinstance(FunctionDef, type)`
- A004 `assert` L16: `isinstance(AsyncFunctionDef, type)`
- A005 `assert` L17: `isinstance(Match, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `lazy-object-proxy, wrapt`
- forbidden imports: `astroid`
- source entrypoints: `astroid.builder.parse, astroid.rebuilder.TreeRebuilder, astroid.nodes`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle is parse/rebuilder/nodes closure without brain or inference; repo is full astroid package.
