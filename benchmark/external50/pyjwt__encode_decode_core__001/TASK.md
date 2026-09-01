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

- `encode(payload: dict, key: str, algorithm: str = 'HS256', headers: dict | None = None) -> str`
- `decode(jwt: str, key: str = '', algorithms: list[str] | None = None, options: dict | None = None, **kwargs) -> dict`
- `exceptions.InvalidTokenError` must be importable and raisable
- `exceptions.InvalidSignatureError` must be importable and raisable
- `exceptions.ExpiredSignatureError` must be importable and raisable

## Required Behavior

- encode signs dictionary payloads with HS256, accepts optional protected headers, and decode verifies the token with an allowed algorithm before returning the payload.
- decode raises InvalidSignatureError for a wrong verification key and ExpiredSignatureError for an expired `exp` claim; the exported JWT exception types derive from Exception through InvalidTokenError.
- The package exposes encode/decode and JWT exceptions with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: jwt.

## Constraints

- Forbidden imports: `jwt`.
- Do not implement JWKS fetch.
- Do not implement original jwt import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — encode signs dictionary payloads with HS256, accepts optional protected headers, and decode verifies the token with an allowed algorithm before returning the payload.
- **B002** — decode raises InvalidSignatureError for a wrong verification key and ExpiredSignatureError for an expired `exp` claim; the exported JWT exception types derive from Exception through InvalidTokenError.
- **B003** — The package exposes encode/decode and JWT exceptions with the kinds listed in this contract.
- **B004** — the submitted package does not import forbidden upstream packages: jwt.
<!-- featureliftbench:behavior-clauses:end -->
