# lark__visitor_transform_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/14`

## Required API

- `featurelifted.Lark` (class) `(grammar: 'Union[Grammar, str, IO[str]]', **options) -> None`
- `featurelifted.Lark.parse` (method) `(self, text: str, start: Optional[str] = None, on_error: 'Optional[Callable[[UnexpectedInput], bool]]' = None) -> 'ParseTree'`
- `featurelifted.Tree` (class) `(data: str, children: 'List[Branch[_Leaf_T]]', meta: Optional[Meta] = None) -> None`
- `featurelifted.Transformer` (class) `(visit_tokens: bool = True) -> None`
- `featurelifted.Transformer.transform` (method) `(self, tree: Tree[~_Leaf_T]) -> ~_Return_T`
- `featurelifted.Visitor` (class) `()`
- `featurelifted.v_args` (function) `(inline: bool = False, meta: bool = False, tree: bool = False, wrapper: Optional[Callable] = None) -> Callable[[Union[Callable[..., ~_Return_T], type]], Union[Callable[..., ~_Return_T], type]]`
- `featurelifted.Discard` (object)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: walk trees with Visitor callbacks. Required observable cases include visitor walks tree nodes.
- **B002**: The extracted feature must support this observable behavior: transform trees bottom-up with Transformer. Required observable cases include transformer evaluates expression; v args inline transform; visitor walks tree nodes.
- **B003**: The extracted feature must support this observable behavior: decorate transformer methods with v_args inline and tree modes. Required observable cases include transformer evaluates expression; v args inline transform; v args tree mode.
- **B004**: The extracted feature must support this observable behavior: discard nodes using Discard sentinel. Required observable cases include discard removes nodes.
- **B005**: The extracted feature must support this observable behavior: parse grammars needed to produce trees for transformation. Required observable cases include visitor walks tree nodes.
- **B006**: The package exposes the required task API paths `featurelifted.Lark`, `featurelifted.Lark.parse`, `featurelifted.Tree`, `featurelifted.Transformer`, `featurelifted.Transformer.transform`, `featurelifted.Visitor`, `featurelifted.v_args`, `featurelifted.Discard` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_visitor_public.py::test_transformer_evaluates_expression`

- mapping: `B002, B003`
- API: `featurelifted.Lark`
- risk: `none`
- A001 `assert` L49: `value == 7`

### `public_tests/test_visitor_public.py::test_v_args_inline_transform`

- mapping: `B002, B003`
- API: `featurelifted.Lark`
- risk: `none`
- A001 `assert` L73: `InlineAdder().transform(tree) == 7`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.Discard, featurelifted.Lark, featurelifted.Transformer, featurelifted.Tree, featurelifted.Visitor, featurelifted.v_args`
- risk: `none`
- A001 `assert` L14: `isinstance(Lark, type)`
- A002 `assert` L15: `hasattr(Lark, 'parse')`
- A003 `assert` L16: `isinstance(Tree, type)`
- A004 `assert` L17: `isinstance(Transformer, type)`
- A005 `assert` L18: `hasattr(Transformer, 'transform')`
- A006 `assert` L19: `isinstance(Visitor, type)`
- A007 `assert` L20: `callable(v_args)`
- A008 `assert` L21: `Discard is not None`

### `hidden_tests/test_visitor_hidden.py::test_discard_removes_nodes`

- mapping: `B004`
- API: `featurelifted.Lark`
- risk: `none`
- A001 `assert` L37: `values == [1, 2, 3]`

### `hidden_tests/test_visitor_hidden.py::test_visitor_walks_tree_nodes`

- mapping: `B001, B002, B005`
- API: `featurelifted.Lark`
- risk: `none`
- A001 `assert` L61: `'start' in counter.seen`
- A002 `assert` L62: `counter.seen.count('pair') == 2`

### `hidden_tests/test_visitor_hidden.py::test_v_args_tree_mode`

- mapping: `B003`
- API: `featurelifted.Lark`
- risk: `none`
- A001 `assert` L82: `UpperNames().transform(tree) == 'LARK'`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `lark`
- source entrypoints: `lark.visitors.Transformer, lark.visitors.Visitor, lark.visitors.v_args, lark.visitors.Discard, lark.Lark.parse, lark.Tree`
- oracle source files: `none`
- runtime dependencies: `none`
