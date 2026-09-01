# FeatureLift Task: dateparser settings parse pipeline

Extract a task-scoped subset of `dateparser` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    detect_languages,
    parse,
    Settings,
)
```

## Required API Details

- `parse(date_string: str, date_formats=None, languages=None, locales=None, region=None, settings=None, detect_languages_function=None)`
- `Settings(settings=None)` class constructor
- `detect_languages(text: str, languages: list[str] | None = None) -> list[str]`

## Required Behavior

- Given ISO-formatted or English month-name input, `parse` returns the corresponding midnight `datetime`; when Spanish or French is explicitly selected, localized month-name input returns the corresponding date.
- When `Settings` supplies supported options, `parse` honors day-month-year ordering and a preference for past dates, and returns a timezone-aware value when UTC awareness and conversion are requested.
- Given localized Spanish or French date text and an en/es/fr candidate list, `detect_languages` returns a list of language shortcodes containing the matching language.
- Constructing `Settings` with a supported setting assigned a value of an invalid type raises `TypeError` before parsing.
- The package exposes the required task API paths `featurelifted.parse`, `featurelifted.Settings`, `featurelifted.detect_languages` with the kinds and callable signatures listed in this contract.
- the submitted package does not import forbidden upstream packages: dateparser.

## Constraints

- Forbidden imports: `dateparser`.
- Do not implement search_dates.
- Do not implement network downloads.
- Do not implement settings keys outside allowlist.
- Do not implement languages outside en/es/fr for required tests.
- Do not implement original dateparser import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Given ISO-formatted or English month-name input, `parse` returns the corresponding midnight `datetime`; when Spanish or French is explicitly selected, localized month-name input returns the corresponding date.
- **B002** — When `Settings` supplies supported options, `parse` honors day-month-year ordering and a preference for past dates, and returns a timezone-aware value when UTC awareness and conversion are requested.
- **B003** — Given localized Spanish or French date text and an en/es/fr candidate list, `detect_languages` returns a list of language shortcodes containing the matching language.
- **B004** — Constructing `Settings` with a supported setting assigned a value of an invalid type raises `TypeError` before parsing.
- **B005** — The package exposes the required task API paths `featurelifted.parse`, `featurelifted.Settings`, `featurelifted.detect_languages` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: dateparser.
<!-- featureliftbench:behavior-clauses:end -->
