# rich__markup_parse_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/24`

## Required API

- `featurelifted.errors` (module)
- `featurelifted.errors.MarkupError` (exception)
- `featurelifted.markup` (module)
- `featurelifted.markup.escape` (function) `(markup: str, _escape: Callable[[Callable[[Match[str]], str], str], str] = <built-in method sub of re.Pattern object>) -> str`
- `featurelifted.markup.render` (function) `(markup: str, style: Union[str, Style] = '', emoji: bool = True, emoji_variant: Optional[Literal['emoji', 'text']] = None) -> Text`
- `featurelifted.text` (module)
- `featurelifted.text.Text` (class) `(text: str = '', style: Union[str, Style] = '', *, justify: Optional[ForwardRef('JustifyMethod')] = None, overflow: Optional[ForwardRef('OverflowMethod')] = None, no_wrap: Optional[bool] = None, end: str = '\n', tab_size: Optional[int] = None, spans: Optional[List[Span]] = None) -> None`
- `featurelifted.text.Text.from_markup` (method) `(text: str, *, style: Union[str, Style] = '', emoji: bool = True, emoji_variant: Optional[Literal['emoji', 'text']] = None, justify: Optional[ForwardRef('JustifyMethod')] = None, overflow: Optional[ForwardRef('OverflowMethod')] = None, end: str = '\n') -> 'Text'`
- `featurelifted.text.Text.markup` (attribute)
- `featurelifted.text.Text.plain` (attribute)
- `featurelifted.text.Text.spans` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: render markup tags into Text with style spans. Required observable cases include render escape and from markup; nested styles and implicit close; markup errors and escaped brackets; meta link handler and repr.
- **B002**: The extracted feature must support this observable behavior: escape square brackets for literal markup. Required observable cases include render escape and from markup; markup errors and escaped brackets.
- **B003**: The extracted feature must support this observable behavior: support nested/open/close tags and link metadata. Required observable cases include nested styles and implicit close; meta link handler and repr.
- **B004**: The extracted feature must support this observable behavior: raise MarkupError on mismatched closing tags. Required observable cases include nested styles and implicit close.
- **B005**: The package exposes the required task API paths `featurelifted.errors`, `featurelifted.errors.MarkupError`, `featurelifted.markup`, `featurelifted.markup.escape`, `featurelifted.markup.render`, `featurelifted.text`, `featurelifted.text.Text`, `featurelifted.text.Text.from_markup`, `featurelifted.text.Text.markup`, `featurelifted.text.Text.plain`, `featurelifted.text.Text.spans` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_render_escape_and_from_markup`

- mapping: `B001, B002`
- API: `featurelifted.markup, featurelifted.text`
- risk: `exact_error_text`
- A001 `assert` L8: `escape('plain [bold]') == 'plain \\[bold]'`
- A002 `assert` L11: `text.plain == 'Hello World'`
- A003 `assert` L12: `any(('bold' in str(span.style).lower() for span in text.spans))`
- A004 `assert` L15: `via_text.plain == 'x'`

### `hidden_tests/test_hidden_behavior.py::test_nested_styles_and_implicit_close`

- mapping: `B001, B003, B004`
- API: `featurelifted.errors, featurelifted.markup, featurelifted.text`
- risk: `none`
- A001 `assert` L12: `text.plain == 'ABC'`
- A002 `assert` L14: `any(('bold' in s.lower() for s in styles))`
- A003 `assert` L15: `any(('italic' in s.lower() for s in styles))`

### `hidden_tests/test_hidden_behavior.py::test_markup_errors_and_escaped_brackets`

- mapping: `B001, B002`
- API: `featurelifted.errors, featurelifted.markup, featurelifted.text`
- risk: `exception_semantics`
- A001 `raises` L19: `pytest.raises(MarkupError)`
- A002 `raises` L22: `pytest.raises(MarkupError)`
- A003 `assert` L26: `'[bold]' in text.plain`

### `hidden_tests/test_hidden_behavior.py::test_meta_link_handler_and_repr`

- mapping: `B001, B003`
- API: `featurelifted.errors, featurelifted.markup, featurelifted.text`
- risk: `none`
- A001 `assert` L31: `text.plain == 'Docs'`
- A002 `assert` L32: `text.spans`
- A003 `assert` L34: `roundtrip.plain == 'Docs'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.errors, featurelifted.markup, featurelifted.text`
- risk: `none`
- A001 `assert` L11: `errors is not None`
- A002 `assert` L12: `issubclass(getattr(errors, 'MarkupError'), BaseException)`
- A003 `assert` L13: `markup is not None`
- A004 `assert` L14: `callable(getattr(markup, 'escape'))`
- A005 `assert` L15: `callable(getattr(markup, 'render'))`
- A006 `assert` L16: `text is not None`
- A007 `assert` L17: `isinstance(getattr(text, 'Text'), type)`
- A008 `assert` L18: `hasattr(getattr(text, 'Text'), 'from_markup')`
- A009 `assert` L19: `getattr(text, 'Text') is not None`
- A010 `assert` L20: `getattr(text, 'Text') is not None`
- A011 `assert` L21: `getattr(text, 'Text') is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `rich`
- source entrypoints: `rich.markup.render, rich.markup.escape, rich.text.Text.from_markup, rich.errors.MarkupError`
- oracle source files: `rich/__init__.py, rich/__main__.py, rich/_cell_widths.py, rich/_emoji_codes.py, rich/_emoji_replace.py, rich/_export_format.py, rich/_extension.py, rich/_fileno.py, rich/_inspect.py, rich/_log_render.py, rich/_loop.py, rich/_null_file.py, rich/_palettes.py, rich/_pick.py, rich/_ratio.py, rich/_spinners.py, rich/_stack.py, rich/_timer.py, rich/_win32_console.py, rich/_windows.py, rich/_windows_renderer.py, rich/_wrap.py, rich/abc.py, rich/align.py, rich/ansi.py, rich/bar.py, rich/box.py, rich/cells.py, rich/color.py, rich/color_triplet.py, rich/columns.py, rich/console.py, rich/constrain.py, rich/containers.py, rich/control.py, rich/default_styles.py, rich/diagnose.py, rich/emoji.py, rich/errors.py, rich/file_proxy.py, rich/filesize.py, rich/highlighter.py, rich/json.py, rich/jupyter.py, rich/layout.py, rich/live.py, rich/live_render.py, rich/logging.py, rich/markdown.py, rich/markup.py, rich/measure.py, rich/padding.py, rich/pager.py, rich/palette.py, rich/panel.py, rich/pretty.py, rich/progress.py, rich/progress_bar.py, rich/prompt.py, rich/protocol.py, rich/py.typed, rich/region.py, rich/repr.py, rich/rule.py, rich/scope.py, rich/screen.py, rich/segment.py, rich/spinner.py, rich/status.py, rich/style.py, rich/styled.py, rich/syntax.py, rich/table.py, rich/terminal_theme.py, rich/text.py, rich/theme.py, rich/themes.py, rich/traceback.py, rich/tree.py`
- runtime dependencies: `none`
- oracle notes: Markup rendering closure includes text/style/emoji support modules.
