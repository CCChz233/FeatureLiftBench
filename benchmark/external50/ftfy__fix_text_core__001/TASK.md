# FeatureLift Task: ftfy fix text

Extract a task-scoped subset of `ftfy` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    fix_text,
)
```

## Required API Details

- `fix_text(text: str, ...) -> str`

## Required Behavior

- `fix_text` accepts Unicode strings containing common encoding mojibake, including Latin-1 and punctuation corruption, and returns the repaired text.
- `fix_text` leaves already-correct plain ASCII text unchanged, including embedded newline characters.
- `fix_text` accepts an empty string and returns an empty string.
- `fix_text` accepts partially damaged or multiply encoded Unicode text and returns text that repairs or otherwise changes the damaged representation.
- The package exposes fix_text with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: ftfy.

## Constraints

- Forbidden imports: `ftfy`.
- Do not implement ftfy CLI.
- Do not implement original ftfy import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `fix_text` accepts Unicode strings containing common encoding mojibake, including Latin-1 and punctuation corruption, and returns the repaired text.
- **B002** — `fix_text` leaves already-correct plain ASCII text unchanged, including embedded newline characters.
- **B003** — `fix_text` accepts an empty string and returns an empty string.
- **B004** — `fix_text` accepts partially damaged or multiply encoded Unicode text and returns text that repairs or otherwise changes the damaged representation.
- **B005** — The package exposes fix_text with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: ftfy.
<!-- featureliftbench:behavior-clauses:end -->
