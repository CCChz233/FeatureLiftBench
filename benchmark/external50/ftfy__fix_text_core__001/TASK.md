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

- The extracted feature must support this observable behavior: fix_text repairs latin-1 mojibake and em-dash sequences. Required observable cases include fix latin1 mojibake; fix em dash mojibake.
- The extracted feature must support this observable behavior: fix_text leaves plain ascii unchanged. Required observable cases include fix identity ascii; fix preserves newlines.
- The extracted feature must support this observable behavior: fix_text handles empty and partially broken utf-8. Required observable cases include fix empty; fix double encoded utf8.
- wcwidth is the only allowed third-party dependency for formatting helpers.
- The package exposes fix_text with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: ftfy.

## Constraints

- Forbidden imports: `ftfy`.
- Do not implement ftfy CLI.
- Do not implement original ftfy import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: fix_text repairs latin-1 mojibake and em-dash sequences. Required observable cases include fix latin1 mojibake; fix em dash mojibake.
- **B002** — The extracted feature must support this observable behavior: fix_text leaves plain ascii unchanged. Required observable cases include fix identity ascii; fix preserves newlines.
- **B003** — The extracted feature must support this observable behavior: fix_text handles empty and partially broken utf-8. Required observable cases include fix empty; fix double encoded utf8.
- **B004** — wcwidth is the only allowed third-party dependency for formatting helpers.
- **B005** — The package exposes fix_text with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: ftfy.
<!-- featureliftbench:behavior-clauses:end -->
