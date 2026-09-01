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

- `use_cassette(path: str, record_mode: str = 'none', match_on: list[str] | None = None, **kwargs)`
- `VCR` class must be importable
  - `VCR.use_cassette(path: str, **kwargs)`
  - `VCR.record_mode` attribute must exist on instances
- `VCR.use_cassette(path: str, **kwargs)`
- `Cassette` class must be importable
  - `Cassette.play_count` attribute must exist on instances

## Required Behavior

- Given a YAML cassette containing a recorded GET response, entering use_cassette(path, record_mode="none") intercepts urllib.request.urlopen for the recorded URI and returns the cassette body without network access.
- Constructing VCR(record_mode="none", match_on=["method", "uri"]) preserves `record_mode` as `"none"`, and its use_cassette(path) context manager replays a request whose method and URI match the recording.
- A cassette configured to match on method and URI replays the matching interaction, and the Cassette object returned by the context manager has `play_count >= 1` after playback.
- With record_mode set to `none`, an interaction already present in the cassette can be replayed and counted without making a live HTTP request.
- The package exposes callable use_cassette and VCR.use_cassette APIs, a VCR class with `record_mode`, and a Cassette class with `play_count`, with the kinds listed in this contract.
- Scanning every Python file in the submitted package finds no `import vcr` or `from vcr ...` statement.

## Constraints

- Forbidden imports: `vcr`.
- Do not implement recording against internet.
- Do not implement original vcr import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Given a YAML cassette containing a recorded GET response, entering use_cassette(path, record_mode="none") intercepts urllib.request.urlopen for the recorded URI and returns the cassette body without network access.
- **B002** — Constructing VCR(record_mode="none", match_on=["method", "uri"]) preserves `record_mode` as `"none"`, and its use_cassette(path) context manager replays a request whose method and URI match the recording.
- **B003** — A cassette configured to match on method and URI replays the matching interaction, and the Cassette object returned by the context manager has `play_count >= 1` after playback.
- **B004** — With record_mode set to `none`, an interaction already present in the cassette can be replayed and counted without making a live HTTP request.
- **B005** — The package exposes callable use_cassette and VCR.use_cassette APIs, a VCR class with `record_mode`, and a Cassette class with `play_count`, with the kinds listed in this contract.
- **B006** — Scanning every Python file in the submitted package finds no `import vcr` or `from vcr ...` statement.
<!-- featureliftbench:behavior-clauses:end -->
