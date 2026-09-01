# FeatureLift Task: Person and address fake data

Build a standalone `featurelifted` package providing Mimesis-style `Person` and `Address` generators for the English locale, including seeded names and invalid-locale errors.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Address,
    Locale,
    LocaleError,
    Person,
)
```

## Required API Details

- `Person(locale=..., seed=...)` class constructor
  - `Person.name(self, gender=None)`
  - `Person.full_name(self, gender=None, reverse=False)`
- `Address(locale=..., seed=...)` class constructor
  - `Address.city(self)`
- `Locale` class constructor
- `LocaleError` class constructor

## Required Behavior

- `Person(locale=Locale("en"), seed=7).name()` returns a non-empty string, and a second instance constructed with the same arguments returns the same name.
- `Address(locale=Locale("en"), seed=7).city()` returns a non-empty string.
- `Person(locale="not-a-locale")` raises `LocaleError`.
- `full_name()` returns a string with at least two whitespace-separated parts for a seeded English person.
- The package exposes `Person`, `Address`, `Locale`, and `LocaleError`.
- The submitted package source does not import the forbidden upstream package `mimesis`.

## Constraints

- Forbidden imports: `mimesis`.
- Do not implement Generic provider bundle.
- Do not implement binary files.
- Do not implement runtime import of mimesis.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `Person(locale=Locale("en"), seed=7).name()` returns a non-empty string, and a second instance constructed with the same arguments returns the same name.
- **B002** — `Address(locale=Locale("en"), seed=7).city()` returns a non-empty string.
- **B003** — `Person(locale="not-a-locale")` raises `LocaleError`.
- **B004** — `full_name()` returns a string with at least two whitespace-separated parts for a seeded English person.
- **B005** — The package exposes `Person`, `Address`, `Locale`, and `LocaleError`.
- **B006** — The submitted package source does not import the forbidden upstream package `mimesis`.
<!-- featureliftbench:behavior-clauses:end -->
