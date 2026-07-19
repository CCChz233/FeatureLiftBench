# FeatureLift Task: Datetime parse, format, and duration core

Extract Pendulum ISO8601/common parsing, strftime-style formatting, and Duration helpers without bundling tzdata, locale packs, or the full timezone database.

## Target API

- Import: `import featurelifted; from featurelifted import UTC, Date, DateTime, Duration, ParserError, Time, datetime, duration, fixed_timezone, parse`
- Callable: `featurelifted.parse`
- Signature: `parse(text: str, **options) -> Date | Time | DateTime | Duration`

## Excluded Behavior

- bundled tzdata or IANA timezone database traversal
- named timezone scheduling (Europe/Paris, America/New_York, etc.)
- humanize/diff-for-humans and locale packs beyond English
- interval iteration, now()/travel mocking, and CLI
- original pendulum import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `pendulum`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — parse ISO8601 dates, datetimes with Z or numeric offsets, and durations
- **B002** — parse common YYYY-MM-DD and HH:mm:ss combinations
- **B003** — construct DateTime and Duration instances
- **B004** — format datetimes with Pendulum tokens (YYYY, MM, DD, HH, mm, ss, Z)
- **B005** — duration component properties (years, months, weeks, days, hours, minutes, seconds)
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: pendulum
<!-- featureliftbench:behavior-clauses:end -->
