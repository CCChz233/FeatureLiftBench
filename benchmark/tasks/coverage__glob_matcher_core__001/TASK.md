# FeatureLift Task: Glob matcher core

Extract coverage.py glob pattern preparation and file-path matching used for include/omit and report filters.

## Target API

- Import: `from featurelifted import GlobMatcher, prep_patterns, globs_to_regex; from featurelifted.exceptions import ConfigError`
- Callable: `featurelifted.GlobMatcher.match`
- Signature: `GlobMatcher(pats: Iterable[str], name: str = 'unknown').match(fpath: str) -> bool`

## Excluded Behavior

- path alias remapping for combine
- source/include/omit selection policy
- configuration file parsing
- coverage measurement, reporting, and CLI
- original project tests and packaging metadata

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `coverage`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — prepare relative and absolute glob patterns for matching
- **B002** — match file paths against include/omit style glob lists
- **B003** — convert glob syntax to compiled regex with Windows slash tolerance
- **B004** — reject invalid glob patterns such as triple-star segments
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: coverage
<!-- featureliftbench:behavior-clauses:end -->
