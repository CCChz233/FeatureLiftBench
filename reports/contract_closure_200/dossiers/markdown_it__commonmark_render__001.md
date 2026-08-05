# markdown_it__commonmark_render__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `FAIL`
- tests/assertions: `6/20`

## Required API

- `featurelifted.MarkdownIt` (class) `(config: 'str | Mapping' = 'commonmark', options_update: 'Mapping | None' = None, *, renderer_cls: 'Callable[[MarkdownIt], RendererProtocol]' = <class 'RendererHTML'>)`
- `featurelifted.MarkdownIt.render` (method) `(self, src: 'str', env: 'MutableMapping | None' = None) -> 'Any'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: render headings, paragraphs, emphasis, lists, blockquotes, links, images, code spans, and fenced code blocks. Required observable cases include nested blocks code escaping and images; strikethrough and reference links.
- **B002**: The extracted feature must support this observable behavior: escape raw text correctly in rendered HTML. Required observable cases include commonmark basic html rendering; strikethrough and reference links.
- **B003**: The extracted feature must support this observable behavior: parse Markdown into Token objects with nesting, tags, attrs, content, and markup. Required observable cases include parse returns useful tokens; strikethrough and reference links.
- **B004**: The extracted feature must support this observable behavior: support the commonmark preset and enable/disable rules. Required observable cases include fence rule disable and link attributes.
- **B005**: The package exposes the required task API paths `featurelifted.MarkdownIt`, `featurelifted.MarkdownIt.render` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_commonmark_basic_html_rendering`

- mapping: `B002`
- API: `featurelifted.MarkdownIt`
- risk: `none`
- A001 `assert` L9: `markdown.render('# Title').strip() == '<h1>Title</h1>'`
- A002 `assert` L10: `markdown.render('- a\n- b').strip() == '<ul>\n<li>a</li>\n<li>b</li>\n</ul>'`
- A003 `assert` L11: `markdown.render('[x](https://example.com)').strip() == '<p><a href="https://example.com">x</a></p>'`

### `public_tests/test_public_api.py::test_parse_returns_useful_tokens`

- mapping: `B003`
- API: `featurelifted.MarkdownIt, featurelifted.MarkdownIt.parse`
- risk: `none`
- A001 `assert` L19: `tokens[0].type == 'paragraph_open'`
- A002 `assert` L20: `tokens[1].type == 'inline'`
- A003 `assert` L21: `tokens[1].children is not None`
- A004 `assert` L22: `[child.type for child in tokens[1].children] == ['text', 'strong_open', 'text', 'strong_close', 'text']`

### `hidden_tests/test_hidden_behavior.py::test_nested_blocks_code_escaping_and_images`

- mapping: `B001`
- API: `featurelifted.MarkdownIt`
- risk: `none`
- A001 `assert` L9: `markdown.render('> quote\n>\n> - item\n').strip() == '<blockquote>\n<p>quote</p>\n<ul>\n<li>item</li>\n</ul>\n</blockquote>'`
- A002 `assert` L12: `markdown.render('1. one\n2. two\n').strip() == '<ol>\n<li>one</li>\n<li>two</li>\n</ol>'`
- A003 `assert` L15: `markdown.render('`code & <tag>`').strip() == '<p><code>code &amp; &lt;tag&gt;</code></p>'`
- A004 `assert` L18: `markdown.render('![alt](img.png "title")').strip() == '<p><img src="img.png" alt="alt" title="title" /></p>'`

### `hidden_tests/test_hidden_behavior.py::test_fence_rule_disable_and_link_attributes`

- mapping: `B004`
- API: `featurelifted.MarkdownIt, featurelifted.MarkdownIt.disable, featurelifted.MarkdownIt.parse`
- risk: `none`
- A001 `assert` L26: `rendered == '<pre><code class="language-python">print(\'x\')\n</code></pre>'`
- A002 `assert` L29: `without_fence.render('```python\nx\n```').strip() == '<p><code>python x </code></p>'`
- A003 `assert` L32: `token.children is not None`
- A004 `assert` L34: `link_open.type == 'link_open'`
- A005 `assert` L35: `link_open.attrGet('href') == 'https://example.com'`

### `hidden_tests/test_hidden_behavior.py::test_strikethrough_and_reference_links`

- mapping: `B001, B002, B003`
- API: `featurelifted.MarkdownIt, featurelifted.MarkdownIt.enable`
- risk: `none`
- A001 `assert` L41: `'<s>gone</s>' in html`
- A002 `assert` L42: `'href="https://example.com"' in html`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.MarkdownIt`
- risk: `none`
- A001 `assert` L9: `isinstance(MarkdownIt, type)`
- A002 `assert` L10: `hasattr(MarkdownIt, 'render')`

## Dependency / Oracle Evidence

- allowed dependencies: `mdurl`
- forbidden imports: `markdown_it`
- source entrypoints: `markdown_it.MarkdownIt, markdown_it.token.Token, markdown_it.utils`
- oracle source files: `none`
- runtime dependencies: `none`

## Machine Issues

- public_tests/test_public_api.py uses undeclared API reference featurelifted.MarkdownIt.parse
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.MarkdownIt.disable
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.MarkdownIt.enable
- hidden_tests/test_hidden_behavior.py uses undeclared API reference featurelifted.MarkdownIt.parse
