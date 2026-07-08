# FeatureLift Task: Environment factor expression and ini filtering

Extract tox factor expression helpers into `featurelifted`.

## Target API

```python
from featurelifted import expand_factors, find_envs, filter_for_env
```

## Required Behavior

- `expand_factors` yields factor groups and remaining line content for ini-style factor prefixes.
- `find_envs` discovers environment names from brace factor expressions.
- `filter_for_env` keeps lines whose factor expressions match `env_name` and/or `env_factors`.

## Constraints

- Forbidden imports: `tox`.
- No virtualenv creation or subprocess execution.
