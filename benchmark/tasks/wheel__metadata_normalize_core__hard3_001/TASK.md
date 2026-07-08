# FeatureLift Task: Wheel metadata normalization helpers

Extract wheel metadata helpers into `featurelifted`.

## Target API

```python
from featurelifted import safe_name, safe_extra, split_sections, parse_wheel_filename, urlsafe_b64encode, WheelError
```

## Constraints

- Forbidden imports: `wheel`.
- No wheel pack/unpack execution.
