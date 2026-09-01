# FeatureLift Task: ISBN validate

Build a standalone `featurelifted` package that validates and converts ISBN numbers like python-stdnum `isbn`, including compact form and checksum errors, without the remaining country-code modules.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    exceptions,
    isbn,
)
```

## Required API Details

- `isbn.validate(number: str, convert: bool = False) -> str`
- `isbn.compact(number: str, convert: bool = False) -> str`
- `isbn.isbn_type(number: str) -> str | None`
- `isbn.to_isbn13(number: str) -> str`
- `exceptions.InvalidChecksum` class constructor

## Required Behavior

- `validate("978-9024538270")` returns `"9789024538270"`; `validate("978-0-471-11709-4")` returns `"9780471117094"`.
- `compact("1-85798-218-5")` returns `"1857982185"`; `compact("978-9024538270")` returns `"9789024538270"`.
- `validate("978-9024538271")` raises `InvalidChecksum`.
- `isbn_type("1-85798-218-5")` is `"ISBN10"`, `isbn_type("978-0-471-11709-4")` is `"ISBN13"`, and `to_isbn13("1-85798-218-5")` equals `"978-1-85798-218-3"`.
- The package exposes `isbn.validate`, `isbn.compact`, `isbn.isbn_type`, `isbn.to_isbn13`, and `InvalidChecksum`.
- The submitted package source does not import the forbidden upstream package `stdnum`.

## Constraints

- Forbidden imports: `stdnum`.
- Do not implement country modules.
- Do not implement IBAN.
- Do not implement runtime import of stdnum.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `validate("978-9024538270")` returns `"9789024538270"`; `validate("978-0-471-11709-4")` returns `"9780471117094"`.
- **B002** — `compact("1-85798-218-5")` returns `"1857982185"`; `compact("978-9024538270")` returns `"9789024538270"`.
- **B003** — `validate("978-9024538271")` raises `InvalidChecksum`.
- **B004** — `isbn_type("1-85798-218-5")` is `"ISBN10"`, `isbn_type("978-0-471-11709-4")` is `"ISBN13"`, and `to_isbn13("1-85798-218-5")` equals `"978-1-85798-218-3"`.
- **B005** — The package exposes `isbn.validate`, `isbn.compact`, `isbn.isbn_type`, `isbn.to_isbn13`, and `InvalidChecksum`.
- **B006** — The submitted package source does not import the forbidden upstream package `stdnum`.
<!-- featureliftbench:behavior-clauses:end -->
