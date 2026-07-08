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
