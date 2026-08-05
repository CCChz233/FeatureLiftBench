# lark__parse_tree_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/17`

## Required API

- `featurelifted.Lark` (class) `(grammar: 'Union[Grammar, str, IO[str]]', **options) -> None`
- `featurelifted.Lark.parse` (method) `(self, text: str, start: Optional[str] = None, on_error: 'Optional[Callable[[UnexpectedInput], bool]]' = None) -> 'ParseTree'`
- `featurelifted.Tree` (class) `(data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta] = None) -> None`
- `featurelifted.Token` (class) `(*args, **kwargs)`
- `featurelifted.UnexpectedToken` (exception)
- `featurelifted.UnexpectedCharacters` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: parse input with inline grammars using LALR. Required observable cases include parse builds tree with precedence; unexpected characters on garbage input.
- **B002**: The extracted feature must support this observable behavior: build Tree nodes with rule data and Token leaves. Required observable cases include parse builds tree with precedence; nested lists and tokens.
- **B003**: The extracted feature must support this observable behavior: support %import, %ignore, and common terminal imports. Required observable cases include named terminal and pretty output.
- **B004**: The extracted feature must support this observable behavior: raise structured parse errors with line/column context. Required observable cases include parse error reports unexpected token; unexpected characters on garbage input.
- **B005**: The extracted feature must support this observable behavior: expose pretty() and child navigation on trees. Required observable cases include named terminal and pretty output.
- **B006**: The package exposes the required task API paths `featurelifted.Lark`, `featurelifted.Lark.parse`, `featurelifted.Tree`, `featurelifted.Token`, `featurelifted.UnexpectedToken`, `featurelifted.UnexpectedCharacters` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_parse_public.py::test_parse_builds_tree_with_precedence`

- mapping: `B001, B002`
- API: `featurelifted.Lark, featurelifted.Tree`
- risk: `none`
- A001 `assert` L23: `isinstance(tree, Tree)`
- A002 `assert` L24: `tree.data == 'start'`
- A003 `assert` L25: `tree.children[0].data == 'expr'`

### `public_tests/test_parse_public.py::test_parse_error_reports_unexpected_token`

- mapping: `B004`
- API: `featurelifted.Lark, featurelifted.UnexpectedToken`
- risk: `exception_semantics`
- A001 `raises` L31: `pytest.raises(UnexpectedToken)`

### `hidden_tests/test_parse_hidden.py::test_nested_lists_and_tokens`

- mapping: `B002`
- API: `featurelifted.Lark`
- risk: `none`
- A001 `assert` L23: `tree.data == 'start'`
- A002 `assert` L25: `items.data == 'items'`
- A003 `assert` L26: `len(items.children) == 3`

### `hidden_tests/test_parse_hidden.py::test_unexpected_characters_on_garbage_input`

- mapping: `B001, B004`
- API: `featurelifted.Lark, featurelifted.UnexpectedCharacters, featurelifted.UnexpectedToken`
- risk: `exception_semantics`
- A001 `raises` L32: `pytest.raises((UnexpectedToken, UnexpectedCharacters))`

### `hidden_tests/test_parse_hidden.py::test_named_terminal_and_pretty_output`

- mapping: `B003, B005`
- API: `featurelifted.Lark`
- risk: `none`
- A001 `assert` L48: `'greet' in pretty`
- A002 `assert` L49: `'Ada' in pretty`
- A003 `assert` L50: `tree.children[0].data == 'greet'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.Lark, featurelifted.Token, featurelifted.Tree, featurelifted.UnexpectedCharacters, featurelifted.UnexpectedToken`
- risk: `none`
- A001 `assert` L13: `isinstance(Lark, type)`
- A002 `assert` L14: `hasattr(Lark, 'parse')`
- A003 `assert` L15: `isinstance(Tree, type)`
- A004 `assert` L16: `isinstance(Token, type)`
- A005 `assert` L17: `issubclass(UnexpectedToken, BaseException)`
- A006 `assert` L18: `issubclass(UnexpectedCharacters, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `lark`
- source entrypoints: `lark.Lark, lark.Lark.parse, lark.Tree, lark.Token, lark.exceptions.UnexpectedToken, lark.exceptions.UnexpectedCharacters`
- oracle source files: `none`
- runtime dependencies: `none`
