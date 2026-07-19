# FeatureLift Task: CryptContext hash and verify

Extract passlib CryptContext multi-scheme hashing and verification without importing passlib.

## Target API

- Import: `from featurelifted import CryptContext`
- Callable: `featurelifted.CryptContext`
- Signature: `CryptContext(schemes=None, **kw)`

## Excluded Behavior

- apache htpasswd helpers and TOTP
- django extension and host-specific handlers
- original passlib import at runtime

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `passlib`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — CryptContext hash and verify for pbkdf2_sha256
- **B002** — scheme options like default_rounds and deprecated schemes
- **B003** — needs_update and identify handlers
- **B004** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B005** — the submitted package does not import forbidden upstream packages: passlib
<!-- featureliftbench:behavior-clauses:end -->
