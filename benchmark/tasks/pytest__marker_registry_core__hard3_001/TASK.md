# FeatureLift Task: MarkerRegistry

Extract pytest marker registry behavior into `featurelifted`.

## Target API

```python
from featurelifted import MarkerRegistry, Marker, UnknownMarkerWarning
```

## Required Behavior

- `MarkerRegistry.from_ini` parses marker lines from ini configuration.
- `merge_plugin_markers` adds plugin-provided markers without overwriting existing ones.
- `check_unknown` warns or raises for unregistered markers.

## Constraints

- Forbidden imports: `pytest`, `_pytest`.
- No test collection or plugin loading.
