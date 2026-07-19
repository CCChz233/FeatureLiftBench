# FeatureLift Task: Wheel metadata normalization helpers

Extract wheel metadata helpers into `featurelifted`.

## Target API

```python
from featurelifted import safe_name, safe_extra, split_sections, parse_wheel_filename, urlsafe_b64encode, WheelError
```

## Constraints

- Forbidden imports: `wheel`.
- No wheel pack/unpack execution.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — metadata normalization
- **B002** — wheel filename parsing
- **B003** — section splitting
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: wheel
<!-- featureliftbench:behavior-clauses:end -->
