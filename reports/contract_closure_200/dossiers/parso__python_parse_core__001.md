# parso__python_parse_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `8/11`

## Required API

- `featurelifted.parse` (function) `(code=None, **kwargs)`
- `featurelifted.load_grammar` (function) `(*, version: str = None, path: str = None)`
- `featurelifted.Grammar` (class) `(text: str, *, tokenizer, parser=<class 'BaseParser'>, diff_parser=None)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse Python source to syntax tree. Required observable cases include parse simple expr; parse version 39; error recovery partial tree.
- **B002**: The extracted feature must support this observable behavior: get_code round-trip on nodes. Required observable cases include name node positions; get code roundtrip.
- **B003**: The extracted feature must support this observable behavior: iter_errors for multiple syntax issues. Required observable cases include iter errors multiple; error recovery partial tree.
- **B004**: The extracted feature must support this observable behavior: version-specific grammars. Required observable cases include parse version 39.
- **B005**: The package exposes the required task API paths `featurelifted.parse`, `featurelifted.load_grammar`, `featurelifted.Grammar` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_parse_simple_expr`

- mapping: `B001`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L9: `expr.get_code().strip() == '1 + 2'`

### `public_tests/test_public_api.py::test_name_node_positions`

- mapping: `B002`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L15: `name.start_pos == (1, 0)`
- A002 `assert` L16: `name.value == 'hello'`

### `hidden_tests/test_hidden_behavior.py::test_get_code_roundtrip`

- mapping: `B002`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L12: `module.get_code() == src`

### `hidden_tests/test_hidden_behavior.py::test_iter_errors_multiple`

- mapping: `B003`
- API: `featurelifted.load_grammar`
- risk: `none`
- A001 `assert` L19: `len(errors) >= 2`

### `hidden_tests/test_hidden_behavior.py::test_parse_version_39`

- mapping: `B001, B004`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L24: `module.get_code().startswith('match')`

### `hidden_tests/test_hidden_behavior.py::test_error_recovery_partial_tree`

- mapping: `B001, B003`
- API: `featurelifted.parse`
- risk: `none`
- A001 `assert` L29: `module.children`

### `hidden_tests/test_hidden_behavior.py::test_no_parso_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L39: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Grammar, featurelifted.load_grammar, featurelifted.parse`
- risk: `none`
- A001 `assert` L11: `callable(parse)`
- A002 `assert` L12: `callable(load_grammar)`
- A003 `assert` L13: `isinstance(Grammar, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `parso`
- source entrypoints: `parso.parse, parso.load_grammar, parso.Grammar.parse`
- oracle source files: `parso/__init__.py, parso/_compatibility.py, parso/cache.py, parso/file_io.py, parso/grammar.py, parso/normalizer.py, parso/parser.py, parso/tree.py, parso/utils.py, parso/pgen2/__init__.py, parso/pgen2/generator.py, parso/pgen2/grammar_parser.py, parso/python/__init__.py, parso/python/errors.py, parso/python/grammar310.txt, parso/python/grammar311.txt, parso/python/grammar312.txt, parso/python/grammar36.txt, parso/python/grammar37.txt, parso/python/grammar38.txt, parso/python/grammar39.txt, parso/python/parser.py, parso/python/prefix.py, parso/python/token.py, parso/python/tokenize.py, parso/python/tree.py`
- runtime dependencies: `none`
- oracle notes: Core grammar/parser tree; copy-all adds diff/pep8 modules.
