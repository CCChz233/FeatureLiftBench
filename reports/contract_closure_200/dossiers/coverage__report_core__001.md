# coverage__report_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/25`

## Required API

- `featurelifted.Analysis` (class) `(precision: 'int', filename: 'str', has_arcs: 'bool', statements: 'set[TLineNo]', excluded: 'set[TLineNo]', executed: 'set[TLineNo]', arc_possibilities_set: 'set[TArc]', arcs_executed_set: 'set[TArc]', exit_counts: 'dict[TLineNo, int]', no_branch: 'set[TLineNo]') -> None`
- `featurelifted.CoverageConfig` (class) `() -> 'None'`
- `featurelifted.CoverageConfig.skip_empty` (attribute)
- `featurelifted.CoverageConfig.xml_package_depth` (attribute)
- `featurelifted.XmlReporter` (class) `(coverage: 'Coverage') -> 'None'`
- `featurelifted.XmlReporter.report` (attribute)
- `featurelifted.XmlReporter.packages` (attribute)
- `featurelifted.XmlReporter.xml_file` (method) `(self, fr: 'FileReporter', analysis: 'Analysis', has_arcs: 'bool') -> 'None'`
- `featurelifted.XmlReporter.xml_out` (attribute)
- `featurelifted.rate` (function) `(hit: 'int', num: 'int') -> 'str'`
- `featurelifted.serialize_xml` (function) `(dom: 'xml.dom.minidom.Document') -> 'str'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: emit Cobertura-compatible XML with coverage, packages, and classes. Required observable cases include xml file emits line elements; serialize xml produces coverage root.
- **B002**: The extracted feature must support this observable behavior: serialize line and branch hit information from Analysis objects. Required observable cases include xml file emits line elements; xml package depth truncates package name.
- **B003**: The extracted feature must support this observable behavior: honor xml_package_depth and skip_empty config options. Required observable cases include xml package depth truncates package name; skip empty omits zero statement files.
- **B004**: The extracted feature must support this observable behavior: compute line-rate and branch-rate attributes. Required observable cases include rate handles zero and fraction; xml package depth truncates package name.
- **B005**: The package exposes the required task API paths `featurelifted.Analysis`, `featurelifted.CoverageConfig`, `featurelifted.CoverageConfig.skip_empty`, `featurelifted.CoverageConfig.xml_package_depth`, `featurelifted.XmlReporter`, `featurelifted.XmlReporter.report`, `featurelifted.XmlReporter.packages`, `featurelifted.XmlReporter.xml_file`, `featurelifted.XmlReporter.xml_out`, `featurelifted.rate`, `featurelifted.serialize_xml` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_rate_handles_zero_and_fraction`

- mapping: `B004`
- API: `featurelifted.rate`
- risk: `none`
- A001 `assert` L29: `rate(0, 0) == '1'`
- A002 `assert` L30: `rate(1, 4) == '0.25'`

### `public_tests/test_public_api.py::test_xml_file_emits_line_elements`

- mapping: `B001, B002`
- API: `featurelifted.Analysis, featurelifted.CoverageConfig, featurelifted.XmlReporter`
- risk: `none`
- A001 `assert` L37: `impl is not None`
- A002 `assert` L55: `'src/pkg/mod.py' in package.elements`
- A003 `assert` L61: `line_numbers == {1, 2, 3}`

### `hidden_tests/test_hidden_behavior.py::test_xml_package_depth_truncates_package_name`

- mapping: `B002, B003, B004`
- API: `featurelifted.CoverageConfig, featurelifted.XmlReporter`
- risk: `none`
- A001 `assert` L48: `impl is not None`
- A002 `assert` L57: `'src' in reporter.packages`
- A003 `assert` L58: `'src.deep' not in reporter.packages`

### `hidden_tests/test_hidden_behavior.py::test_skip_empty_omits_zero_statement_files`

- mapping: `B003`
- API: `featurelifted.CoverageConfig, featurelifted.XmlReporter`
- risk: `state_mutation`
- A001 `assert` L66: `impl is not None`
- A002 `assert` L75: `reporter.packages == {}`

### `hidden_tests/test_hidden_behavior.py::test_serialize_xml_produces_coverage_root`

- mapping: `B001`
- API: `featurelifted.serialize_xml`
- risk: `none`
- A001 `assert` L80: `impl is not None`
- A002 `assert` L86: `xml_text.startswith('<?xml')`
- A003 `assert` L87: `'<coverage' in xml_text`
- A004 `assert` L88: `'line-rate="1"' in xml_text`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Analysis, featurelifted.CoverageConfig, featurelifted.XmlReporter, featurelifted.rate, featurelifted.serialize_xml`
- risk: `none`
- A001 `assert` L13: `isinstance(Analysis, type)`
- A002 `assert` L14: `isinstance(CoverageConfig, type)`
- A003 `assert` L15: `CoverageConfig is not None`
- A004 `assert` L16: `CoverageConfig is not None`
- A005 `assert` L17: `isinstance(XmlReporter, type)`
- A006 `assert` L18: `XmlReporter is not None`
- A007 `assert` L19: `XmlReporter is not None`
- A008 `assert` L20: `hasattr(XmlReporter, 'xml_file')`
- A009 `assert` L21: `XmlReporter is not None`
- A010 `assert` L22: `callable(rate)`
- A011 `assert` L23: `callable(serialize_xml)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `coverage`
- source entrypoints: `coverage.xmlreport.XmlReporter, coverage.xmlreport.XmlReporter.report, coverage.xmlreport.rate, coverage.results.Analysis`
- oracle source files: `none`
- runtime dependencies: `none`
- oracle notes: XML report writer closure with Analysis, FileReporter, and CoverageConfig report options.
