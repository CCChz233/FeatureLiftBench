# FeatureLift Task: Backend discovery, priority sorting, and failover selection

Extract a task-scoped subset of `keyring` backend selection into a standalone `featurelifted` package.

The implementation must not import `keyring`, must not read from `repo/`, must not use the network, and must not access OS keychains. Use only the standard library.

## Target API

```python
from featurelifted import (
    Backend,
    BackendNotFound,
    ChainerBackend,
    Credential,
    ErrorBackend,
    FailBackend,
    MemoryBackend,
    PasswordDeleteError,
    PasswordSetError,
    select_backend,
)
```

Required behavior:

- `select_backend(backends, env=None) -> Backend`
- `ChainerBackend(backends).get_password(service, username)`
- `ChainerBackend(backends).set_password(service, username, password)`
- `MemoryBackend.get_credential(service, username=None)`

## Required Behavior

- Select the highest-priority viable backend by default.
- Exclude negative-priority backends from automatic selection.
- Return `FailBackend` when no viable backend exists.
- Honor `PYTHON_KEYRING_BACKEND` in `env` by matching backend name, class path, or class name.
- Raise `BackendNotFound` when an override requests an unavailable or non-viable backend.
- `ChainerBackend` sorts viable backends by priority descending.
- `ChainerBackend.get_password()` skips backend exceptions and returns the first non-`None` password.
- `ChainerBackend.set_password()` falls back after backend failures and raises `PasswordSetError` if all fail.
- `MemoryBackend.get_credential(service, None)` may discover a stored username.

## Constraints

- Forbidden imports: `keyring`.
- Forbidden path access: `repo/`, `keyring/`.
- Do not access macOS Keychain, Windows credential vault, SecretService, KWallet, config files, or CLI behavior.

## Public vs Hidden Tests

Public tests cover highest-priority selection, environment override, and basic chained password lookup.
Hidden tests cover negative priority exclusion, non-viable override rejection, backend error fallback, set-password fallback/failure, and credential username discovery.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — Backend base API
- **B002** — MemoryBackend for deterministic storage
- **B003** — FailBackend
- **B004** — ErrorBackend for failure-path tests
- **B005** — ChainerBackend priority sorting and fallback
- **B006** — select_backend priority selection
- **B007** — PYTHON_KEYRING_BACKEND override
- **B008** — Credential and password set/delete errors
- **B009** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B010** — the submitted package does not import forbidden upstream packages: keyring
<!-- featureliftbench:behavior-clauses:end -->
