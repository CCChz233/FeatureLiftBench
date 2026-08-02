# FeatureLift Task: joserfc jwt claims

Extract a task-scoped subset of `joserfc` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    errors,
    jwk,
    jwt,
)
```

## Required API Details

- `jwt` module must be importable
- `jwt.encode` callable must exist
- `jwt.decode` callable must exist
- `jwt.Token` class must be importable
- `jwk.OctKey` class must be importable
- `errors.ExpiredTokenError` class must be importable

## Required Behavior

- The extracted feature must support this observable behavior: HS256 encode/decode roundtrip. Required observable cases include encode decode hs256.
- The extracted feature must support this observable behavior: OctKey import/generate. Required observable cases include generate key.
- The extracted feature must support this observable behavior: exp claim validation raises ExpiredTokenError. Required observable cases include exp claim.
- Decoded tokens expose .claims mapping.
- The package exposes jwt/OctKey/ExpiredTokenError with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: joserfc.

## Constraints

- Forbidden imports: `joserfc`.
- Do not implement JWKS URL fetch.
- Do not implement original joserfc import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: HS256 encode/decode roundtrip. Required observable cases include encode decode hs256.
- **B002** — The extracted feature must support this observable behavior: OctKey import/generate. Required observable cases include generate key.
- **B003** — The extracted feature must support this observable behavior: exp claim validation raises ExpiredTokenError. Required observable cases include exp claim.
- **B004** — Decoded tokens expose .claims mapping.
- **B005** — The package exposes jwt/OctKey/ExpiredTokenError with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: joserfc.
<!-- featureliftbench:behavior-clauses:end -->
