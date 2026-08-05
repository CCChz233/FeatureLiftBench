# pygments__formatter_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/15`

## Required API

- `featurelifted.highlight` (function) `(code, lexer, formatter, outfile=None)`
- `featurelifted.HtmlFormatter` (class) `(**options)`
- `featurelifted.get_lexer_by_name` (function) `(_alias, **options)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: render token streams to HTML spans with HtmlFormatter. Required observable cases include html formatter wraps tokens; linenos and cssclass options.
- **B002**: The extracted feature must support this observable behavior: highlight source with highlight(code, lexer, formatter). Required observable cases include full document and keyword highlighting.
- **B003**: The extracted feature must support this observable behavior: support nowrap, linenos, cssclass, and title options. Required observable cases include nowrap option omits outer div; linenos and cssclass options.
- **B004**: The extracted feature must support this observable behavior: escape HTML in source text and preserve token class names. Required observable cases include html formatter wraps tokens; html escapes angle brackets in source.
- **B005**: The extracted feature must support this observable behavior: resolve Python lexer for integrated highlighting. Required observable cases include full document and keyword highlighting.
- **B006**: The package exposes the required task API paths `featurelifted.highlight`, `featurelifted.HtmlFormatter`, `featurelifted.get_lexer_by_name` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_formatter_public.py::test_html_formatter_wraps_tokens`

- mapping: `B001, B004`
- API: `featurelifted.HtmlFormatter, featurelifted.get_lexer_by_name, featurelifted.highlight`
- risk: `none`
- A001 `assert` L15: `'<span class="' in html`
- A002 `assert` L16: `'x' in html`
- A003 `assert` L17: `'&lt;' not in html`

### `public_tests/test_formatter_public.py::test_nowrap_option_omits_outer_div`

- mapping: `B003`
- API: `featurelifted.HtmlFormatter, featurelifted.get_lexer_by_name, featurelifted.highlight`
- risk: `none`
- A001 `assert` L25: `'<div' not in html`
- A002 `assert` L26: `'pass' in html`

### `hidden_tests/test_formatter_hidden.py::test_linenos_and_cssclass_options`

- mapping: `B001, B003`
- API: `featurelifted.HtmlFormatter, featurelifted.get_lexer_by_name, featurelifted.highlight`
- risk: `none`
- A001 `assert` L11: `'class="source"' in html`
- A002 `assert` L12: `'linenos' in html or '1' in html`
- A003 `assert` L13: `'a' in html and 'b' in html`

### `hidden_tests/test_formatter_hidden.py::test_html_escapes_angle_brackets_in_source`

- mapping: `B004`
- API: `featurelifted.HtmlFormatter, featurelifted.get_lexer_by_name, featurelifted.highlight`
- risk: `none`
- A001 `assert` L21: `'&lt;tag&gt;' in html`

### `hidden_tests/test_formatter_hidden.py::test_full_document_and_keyword_highlighting`

- mapping: `B002, B005`
- API: `featurelifted.HtmlFormatter, featurelifted.get_lexer_by_name, featurelifted.highlight`
- risk: `none`
- A001 `assert` L29: `'snippet.py' in html`
- A002 `assert` L30: `'def' in html`
- A003 `assert` L31: `'run' in html`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.HtmlFormatter, featurelifted.get_lexer_by_name, featurelifted.highlight`
- risk: `none`
- A001 `assert` L11: `callable(highlight)`
- A002 `assert` L12: `isinstance(HtmlFormatter, type)`
- A003 `assert` L13: `callable(get_lexer_by_name)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pygments`
- source entrypoints: `pygments.highlight, pygments.formatters.html.HtmlFormatter, pygments.formatter.Formatter, pygments.style.Style, pygments.lexers.get_lexer_by_name`
- oracle source files: `none`
- runtime dependencies: `none`
