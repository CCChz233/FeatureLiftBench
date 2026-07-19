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

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — brace factor expansion
- **B002** — negated factors
- **B003** — env list discovery
- **B004** — factor-filtered ini lines
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: tox
<!-- featureliftbench:behavior-clauses:end -->
