# FeatureLift Task: parse_wheel_record find_dist_info

Extract installer wheel RECORD helpers into `featurelifted`.

## Target API

```python
from featurelifted import parse_wheel_record, find_dist_info, script_name
```

## Required Behavior

- `parse_wheel_record` parses CSV RECORD rows into `(path, digest, size)` tuples.
- `find_dist_info` locates a unique `.dist-info` directory among archive names.
- `script_name` derives console script names from entry point targets.

## Constraints

- Forbidden imports: `installer`.
- No actual install to system paths.
