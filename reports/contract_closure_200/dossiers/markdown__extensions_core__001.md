# markdown__extensions_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `8/14`

## Required API

- `featurelifted.markdown` (function) `(text, **kwargs)`
- `featurelifted.Markdown` (class) `(**kwargs)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: pipe table rendering. Required observable cases include simple table; table header align; table row span.
- **B002**: The extracted feature must support this observable behavior: footnote reference and backlink HTML. Required observable cases include basic footnote; footnote backlink; multiple footnotes order.
- **B003**: The extracted feature must support this observable behavior: extension registration on Markdown class. Required observable cases include table row span.
- **B004**: The package exposes the required task API paths `featurelifted.markdown`, `featurelifted.Markdown` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_simple_table`

- mapping: `B001`
- API: `featurelifted.markdown`
- risk: `none`
- A001 `assert` L9: `'<table>' in html`
- A002 `assert` L10: `'<th>h1</th>' in html`
- A003 `assert` L11: `'<td>a</td>' in html`

### `public_tests/test_public_api.py::test_basic_footnote`

- mapping: `B002`
- API: `featurelifted.markdown`
- risk: `none`
- A001 `assert` L17: `'class="footnote"' in html or 'footnote' in html`
- A002 `assert` L18: `'note' in html`

### `hidden_tests/test_hidden_behavior.py::test_table_header_align`

- mapping: `B001`
- API: `featurelifted.markdown`
- risk: `none`
- A001 `assert` L16: `'text-align: left' in html`
- A002 `assert` L17: `'text-align: center' in html`
- A003 `assert` L18: `'text-align: right' in html`

### `hidden_tests/test_hidden_behavior.py::test_footnote_backlink`

- mapping: `B002`
- API: `featurelifted.markdown`
- risk: `none`
- A001 `assert` L24: `'footnote-backref' in html or '↩' in html`

### `hidden_tests/test_hidden_behavior.py::test_table_row_span`

- mapping: `B001, B003`
- API: `featurelifted.markdown`
- risk: `none`
- A001 `assert` L30: `html.count('<tr>') >= 3`

### `hidden_tests/test_hidden_behavior.py::test_multiple_footnotes_order`

- mapping: `B002`
- API: `featurelifted.markdown`
- risk: `ordering_semantics`
- A001 `assert` L36: `html.index('first') < html.index('second') or 'first' in html`

### `hidden_tests/test_hidden_behavior.py::test_no_markdown_import_surface`

- mapping: `B005`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L46: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.Markdown, featurelifted.markdown`
- risk: `none`
- A001 `assert` L10: `callable(markdown)`
- A002 `assert` L11: `isinstance(Markdown, type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `markdown`
- source entrypoints: `markdown.markdown, markdown.extensions.tables.TableExtension, markdown.extensions.footnotes.FootnoteExtension`
- oracle source files: `markdown/__init__.py, markdown/__meta__.py, markdown/blockparser.py, markdown/blockprocessors.py, markdown/core.py, markdown/extensions/__init__.py, markdown/extensions/tables.py, markdown/extensions/footnotes.py, markdown/htmlparser.py, markdown/inlinepatterns.py, markdown/postprocessors.py, markdown/preprocessors.py, markdown/serializers.py, markdown/treeprocessors.py, markdown/util.py`
- runtime dependencies: `none`
- oracle notes: Core markdown pipeline plus tables/footnotes extensions.
