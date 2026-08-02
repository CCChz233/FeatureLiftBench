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

- `parse(date_string: str, date_formats=None, languages=None, locales=None, region=None, settings=None)`
- `Settings(**options)` class constructor
- `detect_languages(text: str, languages: list[str] | None = None) -> list[str]`

## Required Behavior

- The extracted feature must support this observable behavior: parse ISO/English/Spanish/French dates. Required observable cases include parse iso and english; parse with languages.
- The extracted feature must support this observable behavior: settings timezone-aware and DATE_ORDER from the allowlist (PREFER_DATES_FROM, RETURN_AS_TIMEZONE_AWARE, TIMEZONE, TO_TIMEZONE, DATE_ORDER, STRICT_PARSING, REQUIRE_PARTS). Required observable cases include settings timezone aware; date order dmy; prefer dates from past.
- The extracted feature must support this observable behavior: detect_languages returns list[str] shortcodes for the en/es/fr subset. Required observable cases include detect languages es fr.
- Parsing remains offline using bundled locale/date data without network access.
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

- **B001** — The extracted feature must support this observable behavior: parse ISO/English/Spanish/French dates. Required observable cases include parse iso and english; parse with languages.
- **B002** — The extracted feature must support this observable behavior: settings timezone-aware and DATE_ORDER from the allowlist (PREFER_DATES_FROM, RETURN_AS_TIMEZONE_AWARE, TIMEZONE, TO_TIMEZONE, DATE_ORDER, STRICT_PARSING, REQUIRE_PARTS). Required observable cases include settings timezone aware; date order dmy; prefer dates from past.
- **B003** — The extracted feature must support this observable behavior: detect_languages returns list[str] shortcodes for the en/es/fr subset. Required observable cases include detect languages es fr.
- **B004** — Parsing remains offline using bundled locale/date data without network access.
- **B005** — The package exposes the required task API paths `featurelifted.parse`, `featurelifted.Settings`, `featurelifted.detect_languages` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: dateparser.
<!-- featureliftbench:behavior-clauses:end -->
