# parsel__selector_namespace_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `5/12`

## Required API

- `featurelifted.Selector` (class) `(root: 'FakeElement') -> 'None'`
- `featurelifted.Selector.css` (method) `(self, query: 'str') -> "'Selector'"`
- `featurelifted.Selector.xpath` (method) `(self, query: 'str') -> "'Selector'"`
- `featurelifted.Selector.register_namespace` (method) `(prefix: 'str', uri: 'str') -> 'None'`
- `featurelifted.Selector.remove_namespace` (method) `(prefix: 'str') -> 'None'`
- `featurelifted.FakeElement` (class) `(tag: 'str', text: 'str' = '', tail: 'str' = '', attrib: 'dict[str, str]' = <factory>, children: "list['FakeElement']" = <factory>) -> None`
- `featurelifted.extract_text` (function) `(nodes: 'list[FakeElement]', default: 'str' = '') -> 'str'`
- `featurelifted.SelectorSyntaxError` (exception)

## Public Behaviors

- **B001**: `Selector.css` and `Selector.xpath` select nodes from a lightweight element tree.
- **B002**: `Selector.register_namespace` enables prefixed XPath tag matching.
- **B003**: `extract_text` joins nested text with sensible defaults.
- **B004**: The package exposes the required task API paths `featurelifted.Selector`, `featurelifted.Selector.css`, `featurelifted.Selector.xpath`, `featurelifted.Selector.register_namespace`, `featurelifted.Selector.remove_namespace`, `featurelifted.FakeElement`, `featurelifted.extract_text`, `featurelifted.SelectorSyntaxError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_css_id_selector`

- mapping: `B001`
- API: `featurelifted.FakeElement, featurelifted.Selector, featurelifted.Selector.css, featurelifted.Selector.get`
- risk: `none`
- A001 `assert` L7: `Selector(root).css('#main').get() == 'hi'`

### `hidden_tests/test_hidden_contract.py::test_xpath_with_namespace`

- mapping: `B001, B002`
- API: `featurelifted.FakeElement, featurelifted.Selector, featurelifted.Selector.getall, featurelifted.Selector.register_namespace, featurelifted.Selector.remove_namespace, featurelifted.Selector.xpath`
- risk: `filesystem_resource`
- A001 `assert` L10: `Selector(root).xpath('//x:item').getall() == ['one']`

### `hidden_tests/test_hidden_contract.py::test_extract_text_default`

- mapping: `B003`
- API: `featurelifted.FakeElement, featurelifted.extract_text`
- risk: `none`
- A001 `assert` L17: `extract_text([root]) == 'Ainner!'`

### `hidden_tests/test_hidden_contract.py::test_empty_css_selector_raises`

- mapping: `B001`
- API: `featurelifted.FakeElement, featurelifted.Selector, featurelifted.Selector.css, featurelifted.SelectorSyntaxError`
- risk: `exception_semantics`
- A001 `raises` L22: `pytest.raises(SelectorSyntaxError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.FakeElement, featurelifted.Selector, featurelifted.SelectorSyntaxError, featurelifted.extract_text`
- risk: `none`
- A001 `assert` L12: `isinstance(Selector, type)`
- A002 `assert` L13: `hasattr(Selector, 'css')`
- A003 `assert` L14: `hasattr(Selector, 'xpath')`
- A004 `assert` L15: `hasattr(Selector, 'register_namespace')`
- A005 `assert` L16: `hasattr(Selector, 'remove_namespace')`
- A006 `assert` L17: `isinstance(FakeElement, type)`
- A007 `assert` L18: `callable(extract_text)`
- A008 `assert` L19: `issubclass(SelectorSyntaxError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `parsel`
- source entrypoints: `parsel.selector.Selector`
- oracle source files: `repo/parsel/selector.py, repo/parsel/utils.py`
- runtime dependencies: `none`
- oracle notes: Selector namespace subset without lxml/cssselect.

## Machine Issues

- public_tests/test_public_contract.py uses undeclared API reference featurelifted.Selector.get
- hidden_tests/test_hidden_contract.py uses undeclared API reference featurelifted.Selector.getall
