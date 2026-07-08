# FeatureLift Task: parse_spec match_version

Extract virtualenv interpreter discovery spec parsing into `featurelifted`.

## Target API

```python
from featurelifted import parse_spec, match_version, discover_paths, InvalidInterpreterSpec
```

## Required Behavior

- `parse_spec` parses version constraints and path globs from interpreter specs.
- `match_version` evaluates constraint operators including `~=`.
- `discover_paths` filters candidate paths by spec.

## Constraints

- Forbidden imports: `virtualenv`.
- No process spawning or environment creation.
