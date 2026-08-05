# readme_renderer__content_type_core__hard3_001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/7`

## Required API

- `featurelifted.render_readme` (function) `(content: 'str', content_type: 'str') -> 'tuple[str, list[str]]'`

## Public Behaviors

- **B001**: `render_readme(content, content_type)` selects plain, markdown, or reST renderers.
- **B002**: Unknown media types fall back to plain text with warnings.
- **B003**: Unsupported charset parameters produce warnings.
- **B004**: The package exposes the required task API paths `featurelifted.render_readme` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_render_markdown_content_type`

- mapping: `B001`
- API: `featurelifted.render_readme`
- risk: `none`
- A001 `assert` L7: `'markdown' in html`
- A002 `assert` L8: `warnings == []`

### `hidden_tests/test_hidden_contract.py::test_unknown_media_type_falls_back_to_plain`

- mapping: `B001, B002`
- API: `featurelifted.render_readme`
- risk: `none`
- A001 `assert` L7: `'hello' in html`
- A002 `assert` L8: `any(('Unknown content type' in item for item in warnings))`

### `hidden_tests/test_hidden_contract.py::test_plain_text_renders_with_line_breaks`

- mapping: `B004`
- API: `featurelifted.render_readme`
- risk: `none`
- A001 `assert` L13: `'<br' in html`

### `hidden_tests/test_hidden_contract.py::test_unknown_charset_warns`

- mapping: `B003`
- API: `featurelifted.render_readme`
- risk: `none`
- A001 `assert` L18: `any(('charset' in item for item in warnings))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B004`
- API: `featurelifted.render_readme`
- risk: `none`
- A001 `assert` L9: `callable(render_readme)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `readme_renderer`
- source entrypoints: `readme_renderer.render_readme`
- oracle source files: `repo/readme_renderer/__init__.py, repo/readme_renderer/markdown.py`
- runtime dependencies: `none`
- oracle notes: Content-type renderer selector without full docutils stack.
