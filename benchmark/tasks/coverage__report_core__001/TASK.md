# FeatureLift Task: Cobertura XML report writer

Extract coverage.py XML report generation (XmlReporter) and supporting analysis types as a standalone package.

## Target API

- Import: `from featurelifted import Analysis, CoverageConfig, XmlReporter, rate, serialize_xml`
- Callable: `featurelifted.XmlReporter.report`
- Signature: `XmlReporter(coverage).report(morfs, outfile=None) -> float`

## Excluded Behavior

- coverage data collection and measurement
- HTML/JSON/LCOV report writers
- configuration file discovery beyond CoverageConfig fields
- plugin loading and CLI entrypoints
- original project tests and docs

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `coverage`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — emit Cobertura-compatible XML with coverage, packages, and classes
- **B002** — serialize line and branch hit information from Analysis objects
- **B003** — honor xml_package_depth and skip_empty config options
- **B004** — compute line-rate and branch-rate attributes
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: coverage
<!-- featureliftbench:behavior-clauses:end -->
