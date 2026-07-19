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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — marker registration
- **B002** — ini merge
- **B003** — unknown marker warnings
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: pytest, _pytest
<!-- featureliftbench:behavior-clauses:end -->
