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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — PreparedRequest matching
- **B002** — matcher helpers
- **B003** — registry find/add/reset
- **B004** — call history
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: responses
<!-- featureliftbench:behavior-clauses:end -->
