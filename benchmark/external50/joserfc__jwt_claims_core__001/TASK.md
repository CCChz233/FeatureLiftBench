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
- `jwt.encode(header: dict, claims: dict, key, algorithms=None, registry=None, encoder_cls=None, default_type='JWT') -> str`
- `jwt.decode(value: bytes | str, key, algorithms=None, registry=None, decoder_cls=None) -> Token`
- `jwt.Token(header: dict, claims: dict)` class constructor
- `jwt.JWTClaimsRegistry` class must be importable
  - `jwt.JWTClaimsRegistry.validate(self, claims: dict) -> None`
- `jwk.OctKey` class must be importable
- `errors.ExpiredTokenError` class must be importable

## Required Behavior

- Given an octet key and an HS256 header, `jwt.encode` returns a token string and `jwt.decode` with the same key returns a token whose claims preserve the encoded subject or issuer value.
- `OctKey.import_key` accepts symmetric secret material and `OctKey.generate_key` creates a key of the requested bit size; either key can sign and verify an HS256 token.
- jwt.decode returns a token even when the exp claim is already expired; JWTClaimsRegistry.validate then raises ExpiredTokenError for that expired exp claim.
- Decoded tokens expose .claims mapping.
- The package exposes jwt, jwt.encode, jwt.decode, jwt.Token, jwt.JWTClaimsRegistry, OctKey, and ExpiredTokenError with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: joserfc.

## Constraints

- Forbidden imports: `joserfc`.
- Do not implement JWKS URL fetch.
- Do not implement original joserfc import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — Given an octet key and an HS256 header, `jwt.encode` returns a token string and `jwt.decode` with the same key returns a token whose claims preserve the encoded subject or issuer value.
- **B002** — `OctKey.import_key` accepts symmetric secret material and `OctKey.generate_key` creates a key of the requested bit size; either key can sign and verify an HS256 token.
- **B003** — jwt.decode returns a token even when the exp claim is already expired; JWTClaimsRegistry.validate then raises ExpiredTokenError for that expired exp claim.
- **B004** — Decoded tokens expose .claims mapping.
- **B005** — The package exposes jwt, jwt.encode, jwt.decode, jwt.Token, jwt.JWTClaimsRegistry, OctKey, and ExpiredTokenError with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: joserfc.
<!-- featureliftbench:behavior-clauses:end -->
