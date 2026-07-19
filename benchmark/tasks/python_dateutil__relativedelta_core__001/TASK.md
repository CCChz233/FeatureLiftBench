# FeatureLift Task: relativedelta arithmetic core

Extract python-dateutil relativedelta relative/absolute date arithmetic, normalization, and weekday helpers for naive datetime/date without rrule, parser, or timezone machinery.

## Target API

- Import: `import featurelifted; from featurelifted import relativedelta, MO, TU, WE, TH, FR, SA, SU`
- Callable: `featurelifted.relativedelta`
- Signature: `relativedelta(dt1=None, dt2=None, years=0, months=0, days=0, **kwargs)`

## Excluded Behavior

- dateutil.rrule, rrulestr, rruleset
- dateutil.parser and general string date parsing
- dateutil.tz, zoneinfo, tzwin
- original dateutil package import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `dateutil`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — relativedelta construction with relative and absolute fields
- **B002** — datetime/date addition and subtraction with month/year rollover
- **B003** — weekday nth helpers MO..SU with setpos semantics
- **B004** — normalized() for fractional day/hour cascading
- **B005** — relativedelta(dt1, dt2) difference mode
- **B006** — yearday/nlyearday and leapdays adjustments
- **B007** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B008** — the submitted package does not import forbidden upstream packages: dateutil
<!-- featureliftbench:behavior-clauses:end -->
