# FeatureLift Task: Source/include/omit selection

Extract coverage.py InOrOut logic that decides whether a file should be measured based on source, include, and omit settings.

## Target API

- Import: `from featurelifted import SourceSelector`
- Callable: `featurelifted.SourceSelector.skip_reason`
- Signature: `SourceSelector(...).skip_reason(filename: str, modulename: str | None = None) -> str | None`

## Excluded Behavior

- plugin file tracers and dynamic source filenames
- coverage data collection and reporting
- path alias remapping for combine
- configuration file discovery beyond constructing a config object
- original project tests and CLI

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `coverage`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — honor --source directory and package specifications
- **B002** — apply run include and omit glob patterns after source scoping
- **B003** — exclude stdlib, third-party, and coverage.py paths when no source is set
- **B004** — return human-readable skip reasons for rejected files
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: coverage
<!-- featureliftbench:behavior-clauses:end -->
