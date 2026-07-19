# FeatureLift Task: ISO8601 duration parse and format

Extract isodate Duration parsing and isoformat helpers without importing isodate.

## Target API

- Import: `import featurelifted; from featurelifted import Duration, ISO8601Error, duration_isoformat, parse_duration; from featurelifted.isodates import parse_date`
- Callable: `featurelifted.parse_duration`
- Signature: `parse_duration(datestring, as_timedelta_if_possible=True)`

## Excluded Behavior

- full date/time/tz parsing surface
- strftime locale tables beyond duration chain
- original isodate import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `isodate`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse P-period durations to timedelta or Duration
- **B002** — duration_isoformat for Duration and timedelta
- **B003** — decimal comma fractions in components
- **B004** — ISO8601Error on invalid input
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: isodate
<!-- featureliftbench:behavior-clauses:end -->
