# FeatureLift Task: pyjwt encode decode

Extract a task-scoped subset of `PyJWT` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    decode,
    encode,
    exceptions,
)
```

## Required API Details

- `encode` callable must exist
- `decode` callable must exist
- `exceptions.InvalidTokenError` must be importable and raisable
- `exceptions.InvalidSignatureError` must be importable and raisable
- `exceptions.ExpiredSignatureError` must be importable and raisable

## Required Behavior

- The extracted feature must support this observable behavior: encode/decode HS256 roundtrip. Required observable cases include encode decode hs256.
- The extracted feature must support this observable behavior: wrong secret and expired tokens raise signature/expiry errors. Required observable cases include wrong secret; expired token.
- The extracted feature must support this observable behavior: optional headers and InvalidTokenError hierarchy. Required observable cases include custom header; invalid token error base.
- cryptography is required for HS256 via PyJWT[crypto].
- The package exposes encode/decode and JWT exceptions with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: jwt.

## Constraints

- Forbidden imports: `jwt`.
- Do not implement JWKS fetch.
- Do not implement original jwt import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: encode/decode HS256 roundtrip. Required observable cases include encode decode hs256.
- **B002** — The extracted feature must support this observable behavior: wrong secret and expired tokens raise signature/expiry errors. Required observable cases include wrong secret; expired token.
- **B003** — The extracted feature must support this observable behavior: optional headers and InvalidTokenError hierarchy. Required observable cases include custom header; invalid token error base.
- **B004** — cryptography is required for HS256 via PyJWT[crypto].
- **B005** — The package exposes encode/decode and JWT exceptions with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: jwt.
<!-- featureliftbench:behavior-clauses:end -->
