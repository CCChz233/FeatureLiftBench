# FeatureLift Task: pyotp totp hotp

Extract a task-scoped subset of `pyotp` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    HOTP,
    random_base32,
    TOTP,
)
```

## Required API Details

- `TOTP` class must be importable
- `TOTP.at` callable must exist
- `TOTP.verify` callable must exist
- `HOTP` class must be importable
- `HOTP.at` callable must exist
- `HOTP.verify` callable must exist
- `random_base32(length=32)`

## Required Behavior

- The extracted feature must support this observable behavior: TOTP.at/verify for fixed timestamps. Required observable cases include totp at verify; totp verify rejects wrong.
- The extracted feature must support this observable behavior: HOTP.at/verify for counters. Required observable cases include hotp at verify; hotp counter increments.
- The extracted feature must support this observable behavior: random_base32 generates base32 secrets with minimum length guard. Required observable cases include random base32; random base32 length guard.
- Tests use at(timestamp) rather than now() to avoid time dependence.
- The package exposes TOTP/HOTP/random_base32 with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: pyotp.

## Constraints

- Forbidden imports: `pyotp`.
- Do not implement QR provisioning network.
- Do not implement original pyotp import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: TOTP.at/verify for fixed timestamps. Required observable cases include totp at verify; totp verify rejects wrong.
- **B002** — The extracted feature must support this observable behavior: HOTP.at/verify for counters. Required observable cases include hotp at verify; hotp counter increments.
- **B003** — The extracted feature must support this observable behavior: random_base32 generates base32 secrets with minimum length guard. Required observable cases include random base32; random base32 length guard.
- **B004** — Tests use at(timestamp) rather than now() to avoid time dependence.
- **B005** — The package exposes TOTP/HOTP/random_base32 with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: pyotp.
<!-- featureliftbench:behavior-clauses:end -->
