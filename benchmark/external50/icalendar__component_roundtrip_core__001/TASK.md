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

- `Calendar()` class constructor
  - `Calendar.from_ical(st: str | bytes, multiple=False)`
  - `Calendar.to_ical(self, sorted=True) -> bytes`
  - `Calendar.add_component(self, component) -> None`
  - `Calendar.subcomponents` attribute must exist on instances
- `Calendar.from_ical(st: str | bytes, multiple=False)`
- `Calendar.to_ical(self, sorted=True) -> bytes`
- `Event()` class constructor
  - `Event.add(self, name, value, parameters=None, encode=True)`

## Required Behavior

- When an `Event` with a summary and start value is added to a `Calendar`, serializing and parsing the calendar preserves the event and its summary.
- `Calendar.from_ical` accepts existing iCalendar text as well as serialized bytes, exposes calendar properties by key, and preserves event subcomponent order.
- When events include an end value or multiple summaries, a serialize/parse roundtrip retains the end property and all events in insertion order.
- Calling `Calendar.to_ical` returns bytes that can be passed directly to `Calendar.from_ical` to reconstruct the calendar.
- The package exposes Calendar/Event/from_ical/to_ical with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: icalendar.

## Constraints

- Forbidden imports: `icalendar`.
- Do not implement full RRULE engines.
- Do not implement original icalendar import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — When an `Event` with a summary and start value is added to a `Calendar`, serializing and parsing the calendar preserves the event and its summary.
- **B002** — `Calendar.from_ical` accepts existing iCalendar text as well as serialized bytes, exposes calendar properties by key, and preserves event subcomponent order.
- **B003** — When events include an end value or multiple summaries, a serialize/parse roundtrip retains the end property and all events in insertion order.
- **B004** — Calling `Calendar.to_ical` returns bytes that can be passed directly to `Calendar.from_ical` to reconstruct the calendar.
- **B005** — The package exposes Calendar/Event/from_ical/to_ical with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: icalendar.
<!-- featureliftbench:behavior-clauses:end -->
