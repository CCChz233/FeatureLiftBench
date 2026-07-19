# FeatureLift Task: iCalendar recurrence (rrule) core

Extract python-dateutil rrule/rruleset/rrulestr recurrence iteration for naive datetimes without timezone, general parser, or relativedelta machinery.

## Target API

- Import: `import featurelifted; from featurelifted import rrule, rruleset, rrulestr, YEARLY, MONTHLY, WEEKLY, DAILY, MO, TU, WE, TH, FR, SA, SU`
- Callable: `featurelifted.rrule`
- Signature: `rrule(freq, dtstart=None, interval=1, **kwargs)`

## Excluded Behavior

- dateutil.tz, TZID, zoneinfo, tzwin
- relativedelta and general dateutil.parser
- original dateutil package import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `dateutil`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — rrule iteration with freq, interval, count, until, and BY* filters
- **B002** — rruleset include rules with EXDATE/RDATE (naive)
- **B003** — rrulestr for RRULE lines with naive iCalendar date values
- **B004** — BYEASTER offsets via easter helper
- **B005** — weekday constants MO..SU and freq constants
- **B006** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B007** — the submitted package does not import forbidden upstream packages: dateutil
<!-- featureliftbench:behavior-clauses:end -->
