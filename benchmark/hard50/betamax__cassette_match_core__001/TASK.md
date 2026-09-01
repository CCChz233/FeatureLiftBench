# FeatureLift Task: Cassette replay matching

Build a standalone `featurelifted` package providing Betamax-style cassette replay on a `requests.Session` from offline JSON fixtures, matching URI without live HTTP.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Betamax,
    BetamaxError,
)
```

## Required API Details

- `Betamax(session, cassette_library_dir=None, default_cassette_options={})` class constructor
  - `Betamax.__init__(self, session, cassette_library_dir=None, default_cassette_options={})`
  - `Betamax.use_cassette(self, cassette_name, **kwargs)`
- `BetamaxError` must be importable and raisable

## Required Behavior

- With `record='none'` and a JSON cassette on disk, `Betamax(session, cassette_library_dir=...).use_cassette(name)` replays a GET to the recorded URI and returns the cassette response body and status 200.
- A GET whose URI does not match the cassette interaction raises `BetamaxError` and does not return a successful response.
- `use_cassette` with `record='none'` for a cassette name that has no JSON file in the library directory raises `ValueError`.
- The package exposes `Betamax`, `use_cassette`, and `BetamaxError` as listed in this contract.
- The submitted package source does not import the forbidden upstream package `betamax`.

## Constraints

- Forbidden imports: `betamax`.
- Do not implement live recording to network.
- Do not implement runtime import of betamax.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — With `record='none'` and a JSON cassette on disk, `Betamax(session, cassette_library_dir=...).use_cassette(name)` replays a GET to the recorded URI and returns the cassette response body and status 200.
- **B002** — A GET whose URI does not match the cassette interaction raises `BetamaxError` and does not return a successful response.
- **B003** — `use_cassette` with `record='none'` for a cassette name that has no JSON file in the library directory raises `ValueError`.
- **B004** — The package exposes `Betamax`, `use_cassette`, and `BetamaxError` as listed in this contract.
- **B005** — The submitted package source does not import the forbidden upstream package `betamax`.
<!-- featureliftbench:behavior-clauses:end -->
