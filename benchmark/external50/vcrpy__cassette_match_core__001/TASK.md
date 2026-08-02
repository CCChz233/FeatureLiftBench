# FeatureLift Task: vcrpy cassette match

Extract a task-scoped subset of `vcrpy` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    Cassette,
    use_cassette,
    VCR,
)
```

## Required API Details

- `use_cassette` callable must exist
- `VCR` class must be importable
  - `VCR.use_cassette` callable must exist
  - `VCR.record_mode` attribute must exist on instances
- `VCR.use_cassette` callable must exist
- `Cassette` class must be importable
  - `Cassette.play_count` attribute must exist on instances

## Required Behavior

- The extracted feature must support this observable behavior: replay cassette via use_cassette with urllib. Required observable cases include use cassette replay.
- The extracted feature must support this observable behavior: VCR factory with record_mode and match_on. Required observable cases include vcr factory.
- The extracted feature must support this observable behavior: match_on method/uri and play_count. Required observable cases include match on method uri; cassette path record mode none.
- record_mode='none' never records new interactions in tests.
- The package exposes use_cassette and VCR with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: vcr.

## Constraints

- Forbidden imports: `vcr`.
- Do not implement recording against internet.
- Do not implement original vcr import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: replay cassette via use_cassette with urllib. Required observable cases include use cassette replay.
- **B002** — The extracted feature must support this observable behavior: VCR factory with record_mode and match_on. Required observable cases include vcr factory.
- **B003** — The extracted feature must support this observable behavior: match_on method/uri and play_count. Required observable cases include match on method uri; cassette path record mode none.
- **B004** — record_mode='none' never records new interactions in tests.
- **B005** — The package exposes use_cassette and VCR with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: vcr.
<!-- featureliftbench:behavior-clauses:end -->
