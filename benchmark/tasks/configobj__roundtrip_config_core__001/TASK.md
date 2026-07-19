# FeatureLift Task: INI-like config round-trip and configspec validation

Extract ConfigObj parsing/writing with comment preservation and Validator configspec checks without original configobj import.

## Target API

- Import: `import featurelifted; from featurelifted import ConfigObj, DuplicateError, flatten_errors, get_extra_values; from featurelifted.validate import Validator, VdtValueTooSmallError`
- Callable: `featurelifted.ConfigObj`
- Signature: `ConfigObj(infile=None, ...)`

## Excluded Behavior

- original configobj import at runtime
- project tests and packaging

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `configobj`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse INI-like config from strings with nested sections
- **B002** — write configs preserving comments and key order metadata
- **B003** — validate values against configspec via Validator
- **B004** — report validation failures with flatten_errors
- **B005** — detect duplicate sections and parse errors
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: configobj
<!-- featureliftbench:behavior-clauses:end -->
