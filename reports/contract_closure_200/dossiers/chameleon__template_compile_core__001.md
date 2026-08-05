# chameleon__template_compile_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/9`

## Required API

- `featurelifted.TemplateError` (exception)
- `featurelifted.zpt.template` (module)
- `featurelifted.zpt.template.PageTemplate` (class) `(body: 'bytes | str', **config: 'Unpack[PageTemplateConfig]')`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: compile and render PageTemplate from source strings. Required observable cases include render tal content; render python expression; tal replace marker.
- **B002**: The extracted feature must support this observable behavior: TAL attributes content/repeat/condition. Required observable cases include render tal content; tal repeat and condition; tal attributes replace; tal replace marker.
- **B003**: The extracted feature must support this observable behavior: TALES path and python expressions. Required observable cases include render python expression; tal replace marker.
- **B004**: The extracted feature must support this observable behavior: macro define/use via metal namespace. Required observable cases include tal replace marker.
- **B005**: The package exposes the required task API paths `featurelifted.TemplateError`, `featurelifted.zpt.template`, `featurelifted.zpt.template.PageTemplate` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_render_tal_content`

- mapping: `B001, B002`
- API: `featurelifted.zpt.template`
- risk: `none`
- A001 `assert` L8: `template.render(name='Ada').strip() == '<div>Ada</div>'`

### `public_tests/test_public_api.py::test_render_python_expression`

- mapping: `B001, B003`
- API: `featurelifted.zpt.template`
- risk: `none`
- A001 `assert` L13: `'ADA' in template.render(name='ada')`

### `hidden_tests/test_hidden_behavior.py::test_tal_repeat_and_condition`

- mapping: `B002`
- API: `featurelifted.zpt.template`
- risk: `none`
- A001 `assert` L16: `out.count('<li>') == 2`
- A002 `assert` L17: `'a' in out and 'b' in out`

### `hidden_tests/test_hidden_behavior.py::test_tal_attributes_replace`

- mapping: `B002`
- API: `featurelifted.zpt.template`
- risk: `none`
- A001 `assert` L23: `'href="/new"' in out`

### `hidden_tests/test_hidden_behavior.py::test_tal_replace_marker`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.zpt.template`
- risk: `none`
- A001 `assert` L29: `'<b>hi</b>' in out`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.TemplateError, featurelifted.zpt, featurelifted.zpt.template`
- risk: `none`
- A001 `assert` L12: `issubclass(TemplateError, BaseException)`
- A002 `assert` L13: `getattr(zpt, 'template') is not None`
- A003 `assert` L14: `isinstance(getattr(getattr(zpt, 'template'), 'PageTemplate'), type)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `chameleon`
- source entrypoints: `chameleon.zpt.template.PageTemplate, chameleon.compiler.ExpressionEngine, chameleon.tal, chameleon.tales, chameleon.exc.TemplateError`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: Oracle copies ZPT compile chain; repo includes benchmark/loader decoys for copy-all penalty.
