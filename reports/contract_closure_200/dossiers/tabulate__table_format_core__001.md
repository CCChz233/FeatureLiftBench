# tabulate__table_format_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `14/28`

## Required API

- `featurelifted.tabulate` (function) `(tabular_data, headers=(), tablefmt='simple', floatfmt='g', intfmt='', numalign='default', stralign='default', missingval='', showindex='default', disable_numparse=False, colglobalalign=None, colalign=None, preserve_whitespace=False, maxcolwidths=None, headersglobalalign=None, headersalign=None, rowalign=None, maxheadercolwidths=None, break_long_words=True, break_on_hyphens=True)`
- `featurelifted.tabulate_formats` (object)
- `featurelifted.simple_separated_format` (function) `(separator)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: tabulate() renders simple, grid, pipe, and plain table formats. Required observable cases include tabulate simple ascii; tabulate with headers; tabulate grid basic; tabulate formats registry; wide char grid alignment; pipe format colalign; latex booktabs format; dict rows headers keys.
- **B002**: The extracted feature must support this observable behavior: automatic numeric decimal alignment and string column padding. Required observable cases include decimal column alignment.
- **B003**: The extracted feature must support this observable behavior: colalign and colglobalalign per-column alignment overrides. Required observable cases include decimal column alignment; colglobalalign center column.
- **B004**: The extracted feature must support this observable behavior: Unicode wide-character display width via wcwidth when available. Required observable cases include wide char grid alignment.
- **B005**: The extracted feature must support this observable behavior: ANSI escape sequences excluded from visible column width. Required observable cases include ansi visible width plain; html escapes angle brackets.
- **B006**: The extracted feature must support this observable behavior: simple_separated_format builds custom separator TableFormat. Required observable cases include wide char grid alignment.
- **B007**: The extracted feature must support this observable behavior: tabulate_formats lists supported output format names. Required observable cases include tabulate with headers; tabulate formats registry; latex booktabs format; dict rows headers keys.
- **B008**: The package exposes the required task API paths `featurelifted.tabulate`, `featurelifted.tabulate_formats`, `featurelifted.simple_separated_format` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_tabulate_simple_ascii`

- mapping: `B001`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L9: `lines[0].startswith('---')`
- A002 `assert` L10: `'1' in lines[1] and '2.34' in lines[1]`
- A003 `assert` L11: `'-56' in lines[2] and '8.999' in lines[2]`
- A004 `assert` L12: `lines[-1].startswith('---')`

### `public_tests/test_public_api.py::test_tabulate_with_headers`

- mapping: `B001, B007`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L22: `lines[0].startswith('Name') and 'Age' in lines[0]`
- A002 `assert` L23: `'Alice' in lines[2] and '24' in lines[2]`
- A003 `assert` L24: `'Bob' in lines[3] and '19' in lines[3]`

### `public_tests/test_public_api.py::test_tabulate_grid_basic`

- mapping: `B001`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L29: `result == '+---+---+\n| a | b |\n+---+---+\n| c | d |\n+---+---+'`

### `public_tests/test_public_api.py::test_tabulate_formats_registry`

- mapping: `B001, B007`
- API: `featurelifted.tabulate_formats`
- risk: `none`
- A001 `assert` L33: `'simple' in tabulate_formats`
- A002 `assert` L34: `'grid' in tabulate_formats`
- A003 `assert` L35: `'pipe' in tabulate_formats`
- A004 `assert` L36: `len(tabulate_formats) >= 30`

### `hidden_tests/test_hidden_behavior.py::test_decimal_column_alignment`

- mapping: `B002, B003`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L13: `result == ' 1.234\n 2.3\n10.1'`

### `hidden_tests/test_hidden_behavior.py::test_wide_char_grid_alignment`

- mapping: `B001, B004, B006`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L24: `'| 한글   |   1 |' in result`
- A002 `assert` L25: `'| en     |   2 |' in result`

### `hidden_tests/test_hidden_behavior.py::test_colglobalalign_center_column`

- mapping: `B003`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L35: `result == ' a   1\nbbb  2'`

### `hidden_tests/test_hidden_behavior.py::test_pipe_format_colalign`

- mapping: `B001`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L45: `'|:-----|' in result`
- A002 `assert` L46: `'|----:|' in result`
- A003 `assert` L47: `'| left |   1 |' in result`

### `hidden_tests/test_hidden_behavior.py::test_ansi_visible_width_plain`

- mapping: `B005`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L53: `result == f'{colored}  x'`

### `hidden_tests/test_hidden_behavior.py::test_latex_booktabs_format`

- mapping: `B001, B007`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L58: `'\\toprule' in result`
- A002 `assert` L59: `'\\bottomrule' in result`

### `hidden_tests/test_hidden_behavior.py::test_html_escapes_angle_brackets`

- mapping: `B005`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L64: `'&lt;b&gt;' in result`

### `hidden_tests/test_hidden_behavior.py::test_dict_rows_headers_keys`

- mapping: `B001, B007`
- API: `featurelifted.tabulate`
- risk: `none`
- A001 `assert` L69: `'name' in result and 'a' in result`

### `hidden_tests/test_hidden_behavior.py::test_no_tabulate_import_surface`

- mapping: `B009`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L79: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B008`
- API: `featurelifted.simple_separated_format, featurelifted.tabulate, featurelifted.tabulate_formats`
- risk: `none`
- A001 `assert` L11: `callable(tabulate)`
- A002 `assert` L12: `tabulate_formats is not None`
- A003 `assert` L13: `callable(simple_separated_format)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `tabulate`
- source entrypoints: `tabulate.tabulate, tabulate.tabulate_formats, tabulate.simple_separated_format, tabulate._visible_width, tabulate._align_column, tabulate._format_table, tabulate._normalize_tabular_data, tabulate._table_formats`
- oracle source files: `tabulate/__init__.py`
- runtime dependencies: `none`
- oracle notes: Oracle splits tabulate/__init__.py into formats, layout, and render modules; excludes CLI and __main__.
