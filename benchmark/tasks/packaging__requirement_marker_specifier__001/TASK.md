# FeatureLift Task: Python package requirement, marker, specifier, and version semantics

Extract packaging's core PEP 440 and PEP 508 parsing/evaluation behavior as a standalone package.

## Target API

- Import: `from featurelifted import Version, Specifier, SpecifierSet, Requirement, Marker, default_environment, InvalidVersion, InvalidSpecifier, InvalidRequirement, InvalidMarker`
- Callable: `featurelifted.Requirement`
- Signature: `Requirement(requirement_string: str)`

## Excluded Behavior

- wheel tag generation and compatibility tags
- manylinux and musllinux platform probing
- package metadata validation
- filename and sdist/wheel utility helpers outside the required entrypoints
- original project tests, documentation, and release tooling

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `packaging`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse, normalize, compare, hash, and stringify PEP 440 versions including epochs, post releases, pre releases, dev releases, and local versions
- **B002** — parse and evaluate specifier sets including compatible release, equality wildcard, exclusion, prerelease handling, filtering, and containment
- **B003** — parse PEP 508 requirements with extras, URL requirements, specifiers, and environment markers
- **B004** — parse and evaluate environment markers with and/or grouping, in/not in operators, extra handling, and default environment values
- **B005** — raise stable InvalidVersion, InvalidSpecifier, InvalidRequirement, and InvalidMarker errors for malformed input
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: packaging
<!-- featureliftbench:behavior-clauses:end -->
