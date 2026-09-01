# FeatureLift Task: flask-login session guard

Extract a task-scoped subset of `flask-login` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    current_user,
    login_required,
    login_user,
    LoginManager,
    logout_user,
    UserMixin,
)
```

## Required API Details

- `LoginManager` class must be importable
  - `LoginManager.init_app(self, app) -> None`
  - `LoginManager.user_loader(self, callback)`
  - `LoginManager.login_view` attribute must exist on instances
- `UserMixin` class must be importable
- `login_user(user, remember: bool = False) -> bool`
- `logout_user() -> None`
- `login_required(func)`
- `current_user` attribute must exist
  - `current_user.get_id(self)`
  - `current_user.is_authenticated` attribute must exist

## Required Behavior

- With a configured `LoginManager.user_loader`, `login_user` authenticates the session user and `logout_user` clears authentication; `current_user` exposes `is_authenticated` and `get_id`, and `UserMixin` users report `is_authenticated` True and `is_anonymous` False.
- When `LoginManager.login_view` is set, anonymous requests to a `login_required` route receive HTTP status 302 or 401.
- `login_user(user, remember=True)` returns True under an active Flask request context.
- Flask is an allowed runtime dependency; session helpers operate under Flask `test_request_context` or `test_client`.
- The package exposes LoginManager/UserMixin/login_user/logout_user/login_required/current_user with the kinds listed in this contract.
- the submitted package does not import forbidden upstream packages: flask_login.

## Constraints

- Forbidden imports: `flask_login`.
- Do not implement LDAP.
- Do not implement real HTTP servers.
- Do not implement original flask_login import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — With a configured `LoginManager.user_loader`, `login_user` authenticates the session user and `logout_user` clears authentication; `current_user` exposes `is_authenticated` and `get_id`, and `UserMixin` users report `is_authenticated` True and `is_anonymous` False.
- **B002** — When `LoginManager.login_view` is set, anonymous requests to a `login_required` route receive HTTP status 302 or 401.
- **B003** — `login_user(user, remember=True)` returns True under an active Flask request context.
- **B004** — Flask is an allowed runtime dependency; session helpers operate under Flask `test_request_context` or `test_client`.
- **B005** — The package exposes LoginManager/UserMixin/login_user/logout_user/login_required/current_user with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: flask_login.
<!-- featureliftbench:behavior-clauses:end -->
