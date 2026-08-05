# lark__grammar_loader_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/13`

## Required API

- `featurelifted.Lark` (class) `(grammar: 'Union[Grammar, str, IO[str]]', **options) -> None`
- `featurelifted.Lark.open` (method) `(grammar_filename: str, rel_to: Optional[str] = None, **options) -> ~_T`
- `featurelifted.Lark.parse` (method) `(self, text: Union[~AnyStr, TextSlice[~AnyStr], Any], start: Optional[str] = None, on_error: 'Optional[Callable[[UnexpectedInput], bool]]' = None) -> 'ParseTree'`
- `featurelifted.exceptions` (module)
- `featurelifted.exceptions.GrammarError` (exception)
- `featurelifted.load_grammar` (module)
- `featurelifted.load_grammar.FromPackageLoader` (class) `(pkg_name: str, search_paths: Sequence[str] = ('',)) -> None`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: load grammars from strings and files with Lark.open(rel_to=...). Required observable cases include open relative import and common import; open from package and import graph.
- **B002**: The extracted feature must support this observable behavior: resolve relative %import directives across grammar files. Required observable cases include open relative import and common import; packaged common grammar import.
- **B003**: The extracted feature must support this observable behavior: load packaged grammars via open_from_package and %import common.*. Required observable cases include open relative import and common import; open from package and import graph; packaged common grammar import.
- **B004**: The extracted feature must support this observable behavior: parse inputs with lalr after grammar compilation. Required observable cases include packaged common grammar import.
- **B005**: The package exposes the required task API paths `featurelifted.Lark`, `featurelifted.Lark.open`, `featurelifted.Lark.parse`, `featurelifted.exceptions`, `featurelifted.exceptions.GrammarError`, `featurelifted.load_grammar`, `featurelifted.load_grammar.FromPackageLoader` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_open_relative_import_and_common_import`

- mapping: `B001, B002, B003`
- API: `featurelifted.Lark, featurelifted.Lark.open, featurelifted.__name__, featurelifted.load_grammar`
- risk: `filesystem_resource`
- A001 `assert` L24: `'add' in tree.pretty()`
- A002 `assert` L35: `common_parser.parse('42')`

### `hidden_tests/test_hidden_behavior.py::test_open_from_package_and_import_graph`

- mapping: `B001, B003`
- API: `featurelifted.Lark, featurelifted.Lark.open, featurelifted.exceptions`
- risk: `exception_semantics, filesystem_resource`
- A001 `assert` L32: `parser.parse('"hello"')`
- A002 `raises` L34: `pytest.raises(GrammarError)`

### `hidden_tests/test_hidden_behavior.py::test_packaged_common_grammar_import`

- mapping: `B002, B003, B004`
- API: `featurelifted.Lark, featurelifted.__name__, featurelifted.exceptions, featurelifted.load_grammar`
- risk: `exact_error_text`
- A001 `assert` L52: `len(tree.children) == 2`
- A002 `assert` L53: `str(tree.children[0]) == '2'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Lark, featurelifted.exceptions, featurelifted.load_grammar`
- risk: `none`
- A001 `assert` L11: `isinstance(Lark, type)`
- A002 `assert` L12: `hasattr(Lark, 'open')`
- A003 `assert` L13: `hasattr(Lark, 'parse')`
- A004 `assert` L14: `exceptions is not None`
- A005 `assert` L15: `issubclass(getattr(exceptions, 'GrammarError'), BaseException)`
- A006 `assert` L16: `load_grammar is not None`
- A007 `assert` L17: `isinstance(getattr(load_grammar, 'FromPackageLoader'), type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `lark`
- source entrypoints: `lark.Lark, lark.Lark.open, lark.Lark.open_from_package, lark.load_grammar.load_grammar`
- oracle source files: `lark/__init__.py, lark/ast_utils.py, lark/common.py, lark/exceptions.py, lark/grammar.py, lark/grammars/__init__.py, lark/grammars/common.lark, lark/grammars/lark.lark, lark/grammars/python.lark, lark/grammars/unicode.lark, lark/indenter.py, lark/lark.py, lark/lexer.py, lark/load_grammar.py, lark/parse_tree_builder.py, lark/parser_frontends.py, lark/parsers/__init__.py, lark/parsers/cyk.py, lark/parsers/earley.py, lark/parsers/earley_common.py, lark/parsers/earley_forest.py, lark/parsers/grammar_analysis.py, lark/parsers/lalr_analysis.py, lark/parsers/lalr_interactive_parser.py, lark/parsers/lalr_parser.py, lark/parsers/lalr_parser_state.py, lark/parsers/xearley.py, lark/py.typed, lark/reconstruct.py, lark/tree.py, lark/tree_matcher.py, lark/tree_templates.py, lark/utils.py, lark/visitors.py`
- runtime dependencies: `none`
- oracle notes: Full lark runtime minus tools/; includes grammars/ resources for %import common.
