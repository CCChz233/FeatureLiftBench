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
- `TOTP.at(for_time, counter_offset=0) -> str`
- `TOTP.verify(otp, for_time=None, valid_window=0) -> bool`
- `HOTP` class must be importable
- `HOTP.at(count) -> str`
- `HOTP.verify(otp, counter) -> bool`
- `random_base32(length=32)`

## Required Behavior

- `TOTP.at` accepts a fixed timestamp and returns its one-time password, while `TOTP.verify` returns `True` for the matching code at that timestamp.
- `HOTP.at` accepts an integer counter and returns its one-time password, `HOTP.verify` accepts that code and counter, and different counters produce different codes.
- `random_base32` returns a secret containing only uppercase Base32 alphabet characters, uses a length of 32 by default, and raises `ValueError` when a requested length is below the supported minimum.
- `TOTP.verify` returns `False` when given a non-matching code for a fixed timestamp.
- The package exposes TOTP/HOTP/random_base32 with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: pyotp.

## Constraints

- Forbidden imports: `pyotp`.
- Do not implement QR provisioning network.
- Do not implement original pyotp import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — `TOTP.at` accepts a fixed timestamp and returns its one-time password, while `TOTP.verify` returns `True` for the matching code at that timestamp.
- **B002** — `HOTP.at` accepts an integer counter and returns its one-time password, `HOTP.verify` accepts that code and counter, and different counters produce different codes.
- **B003** — `random_base32` returns a secret containing only uppercase Base32 alphabet characters, uses a length of 32 by default, and raises `ValueError` when a requested length is below the supported minimum.
- **B004** — `TOTP.verify` returns `False` when given a non-matching code for a fixed timestamp.
- **B005** — The package exposes TOTP/HOTP/random_base32 with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: pyotp.
<!-- featureliftbench:behavior-clauses:end -->
