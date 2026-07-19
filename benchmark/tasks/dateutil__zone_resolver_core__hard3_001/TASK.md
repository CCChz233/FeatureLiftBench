# FeatureLift Task: ZoneResolver

Extract dateutil zone resolution into `featurelifted`.

## Target API

```python
from featurelifted import ZoneResolver, parse_tzfile, UnknownZoneError, InvalidTZFileError
```

## Required Behavior

- `ZoneResolver.load_zone(name, tzdata)` parses tzfile bytes and caches zones.
- Aliases resolve to canonical zone names with cycle detection.
- `parse_tzfile` validates tzfile headers and extracts metadata.
- Missing zones raise `UnknownZoneError`.

## Constraints

- Forbidden imports: `dateutil`.
- No network or tzdata downloads.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — tzfile parsing boundary
- **B002** — zone cache
- **B003** — alias resolution
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: dateutil
<!-- featureliftbench:behavior-clauses:end -->
