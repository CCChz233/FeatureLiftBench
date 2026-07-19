# FeatureLift Task: Email syntax validation core

Extract validate_email with ValidatedEmail normalization and typed EmailNotValidError hierarchy for offline syntax validation without DNS deliverability checks.

## Target API

- Import: `import featurelifted; from featurelifted import validate_email, ValidatedEmail, EmailNotValidError, EmailSyntaxError, EmailUndeliverableError`
- Callable: `featurelifted.validate_email`
- Signature: `validate_email(email, /, *, check_deliverability=False, **options) -> ValidatedEmail`

## Excluded Behavior

- DNS deliverability checks and caching_resolver
- CLI entry point (__main__)
- original email_validator import at runtime
- network access

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `email_validator`, `emailvalidator`, `dns`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — validate_email returns ValidatedEmail with normalized/local_part/domain fields
- **B002** — EmailSyntaxError and EmailNotValidError for invalid addresses
- **B003** — IDNA domain encoding and internationalized local parts (SMTPUTF8)
- **B004** — quoted local part parsing and de-quoting when allowed
- **B005** — display name angle-bracket parsing when allowed
- **B006** — reserved/special-use domain rejection and test_environment bypass
- **B007** — case-insensitive mailbox names (e.g. POSTMASTER)
- **B008** — Unicode NFC normalization of local parts
- **B009** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B010** — the submitted package does not import forbidden upstream packages: email_validator, emailvalidator, dns
<!-- featureliftbench:behavior-clauses:end -->
