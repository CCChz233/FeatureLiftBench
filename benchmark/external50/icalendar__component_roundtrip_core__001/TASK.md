# FeatureLift Task: icalendar component roundtrip

Extract a task-scoped subset of `icalendar` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Calendar,
    Event,
)
```

## Required API Details

- `Calendar` class must be importable
  - `Calendar.from_ical` callable must exist
  - `Calendar.to_ical` callable must exist
  - `Calendar.add_component` callable must exist
  - `Calendar.subcomponents` attribute must exist on instances
- `Calendar.from_ical` callable must exist
- `Calendar.to_ical` callable must exist
- `Event` class must be importable
  - `Event.add` callable must exist

## Required Behavior

- The extracted feature must support this observable behavior: build Calendar/Event and roundtrip ICS. Required observable cases include build and roundtrip.
- The extracted feature must support this observable behavior: parse existing ICS strings. Required observable cases include parse existing ics.
- The extracted feature must support this observable behavior: dtend and multiple events. Required observable cases include event dtend; multiple events.
- to_ical returns bytes suitable for from_ical.
- The package exposes Calendar/Event/from_ical/to_ical with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: icalendar.

## Constraints

- Forbidden imports: `icalendar`.
- Do not implement full RRULE engines.
- Do not implement original icalendar import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: build Calendar/Event and roundtrip ICS. Required observable cases include build and roundtrip.
- **B002** — The extracted feature must support this observable behavior: parse existing ICS strings. Required observable cases include parse existing ics.
- **B003** — The extracted feature must support this observable behavior: dtend and multiple events. Required observable cases include event dtend; multiple events.
- **B004** — to_ical returns bytes suitable for from_ical.
- **B005** — The package exposes Calendar/Event/from_ical/to_ical with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: icalendar.
<!-- featureliftbench:behavior-clauses:end -->
