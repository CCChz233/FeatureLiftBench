# FeatureLift Task: Run-section config merge

Extract coverage.py configuration reading and merging for the run section from rc files, environment, and constructor arguments.

## Target API

- Import: `from featurelifted import CoverageConfig, read_run_config`
- Callable: `featurelifted.read_run_config`
- Signature: `read_run_config(config_file: bool | str = True, warn=None, **kwargs) -> CoverageConfig`

## Excluded Behavior

- glob matching and file selection
- path alias remapping
- coverage collection, data storage, and reporting
- plugin loading and HTML/XML report sections beyond parsing
- original project tests and CLI

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `coverage`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — read .coveragerc and prefixed sections from setup.cfg or tox.ini
- **B002** — parse run include, omit, source, branch, and related list options
- **B003** — merge constructor kwargs and COVERAGE_* environment overrides
- **B004** — apply post-processing such as user path expansion
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: coverage
<!-- featureliftbench:behavior-clauses:end -->
