# FeatureLift Task: Request matcher registry and call history

Extract an offline responses matcher/registry subset into `featurelifted`.

## Target API

```python
from featurelifted import MockResponseRegistry, MockResponse, query_string_matcher, header_matcher
```

## Required Behavior

- Register `MockResponse` objects and find the first matching `PreparedRequest`.
- Support `query_string_matcher` and `header_matcher` helper matchers.
- `once=True` responses are removed after the first successful match.
- `reset()` clears registered responses and call history.

## Constraints

- Forbidden imports: `responses`.
- Allowed dependency: `requests` from `requirements.lock`.
- No real network or adapter patching.
