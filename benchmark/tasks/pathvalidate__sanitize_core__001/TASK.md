# FeatureLift Task: Filename and filepath sanitization core

Extract cross-platform filename and filepath sanitization with platform-specific reserved names, validation errors, and sanitize/validate helpers without importing pathvalidate.

## Target API

- Import: `import featurelifted; from featurelifted import Platform, sanitize_filename, sanitize_filepath, validate_filename, validate_filepath, is_valid_filename, is_valid_filepath, ValidationError, ErrorReason, ReservedNameError, InvalidCharError`
- Callable: `featurelifted.sanitize_filename`
- Signature: `sanitize_filename(value, platform='auto', replacement_text='', **kwargs)`

## Excluded Behavior

- click and argparse CLI integrations
- LTSV label and symbol replacement helpers
- upstream test suite and docs
- original pathvalidate import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pathvalidate`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — sanitize_filename replaces invalid characters
- **B002** — sanitize_filepath sanitizes each path segment
- **B003** — Windows reserved device names (CON, PRN, etc.) rejected or rewritten
- **B004** — ValidationError exposes ErrorReason and reserved_name metadata
- **B005** — platform parameter selects Windows/Linux/macOS/universal rules
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: pathvalidate
<!-- featureliftbench:behavior-clauses:end -->
