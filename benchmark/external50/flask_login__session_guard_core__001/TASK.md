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
  - `LoginManager.init_app` callable must exist
  - `LoginManager.user_loader` callable must exist
  - `LoginManager.login_view` attribute must exist on instances
- `UserMixin` class must be importable
- `login_user` callable must exist
- `logout_user` callable must exist
- `login_required` callable must exist
- `current_user` attribute must exist
  - `current_user.get_id` callable must exist
  - `current_user.is_authenticated` attribute must exist

## Required Behavior

- The extracted feature must support this observable behavior: login/logout/current_user with UserMixin. Required observable cases include login logout current user; user mixin anonymous.
- The extracted feature must support this observable behavior: login_required guards anonymous users. Required observable cases include login required redirects anonymous.
- The extracted feature must support this observable behavior: remember flag on login_user. Required observable cases include remember flag.
- Tests use Flask test_request_context/test_client only; Flask is an allowed dependency.
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

- **B001** — The extracted feature must support this observable behavior: login/logout/current_user with UserMixin. Required observable cases include login logout current user; user mixin anonymous.
- **B002** — The extracted feature must support this observable behavior: login_required guards anonymous users. Required observable cases include login required redirects anonymous.
- **B003** — The extracted feature must support this observable behavior: remember flag on login_user. Required observable cases include remember flag.
- **B004** — Tests use Flask test_request_context/test_client only; Flask is an allowed dependency.
- **B005** — The package exposes LoginManager/UserMixin/login_user/logout_user/login_required/current_user with the kinds listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: flask_login.
<!-- featureliftbench:behavior-clauses:end -->
