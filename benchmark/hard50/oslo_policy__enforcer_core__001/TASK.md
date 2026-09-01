# FeatureLift Task: Policy enforcer

Build a standalone `featurelifted` package providing oslo.policy-style rule registration and enforcement against credentials.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    ConfigOpts,
    Enforcer,
    PolicyNotAuthorized,
    RuleDefault,
)
```

## Required API Details

- `ConfigOpts()` class constructor
  - `ConfigOpts.__call__(self, args=None, project=None, prog=None, version=None, usage=None, default_config_files=None, default_config_dirs=None, validate_default_values=False, description=None, epilog=None, use_env=True)`
- `Enforcer(conf, policy_file=None, rules=None, default_rule=None, use_conf=True, overwrite=True, fallback_to_json_file=None)` class constructor
  - `Enforcer.__init__(self, conf, policy_file=None, rules=None, default_rule=None, use_conf=True, overwrite=True, fallback_to_json_file=None) -> None`
  - `Enforcer.register_default(self, default: RuleDefault) -> None`
  - `Enforcer.enforce(self, rule, target, creds, do_raise=False, exc=None, *args, **kwargs) -> bool`
- `RuleDefault(name: str, check_str: str, description: str | None = None, deprecated_rule=None, deprecated_for_removal=False, deprecated_reason=None, deprecated_since=None, scope_types=None)` class constructor
  - `RuleDefault.__init__(self, name: str, check_str: str, description: str | None = None, deprecated_rule=None, deprecated_for_removal=False, deprecated_reason=None, deprecated_since=None, scope_types=None) -> None`
- `PolicyNotAuthorized` must be importable and raisable

## Required Behavior

- After `ConfigOpts` is initialized with `args=[]` and `register_default` installs `role:admin`, `enforce` returns True for credentials whose `roles` include `admin` and False otherwise.
- A registered rule of `@` authorizes empty credentials.
- When `do_raise=True` and the check fails, `enforce` raises `PolicyNotAuthorized` whose message includes the rule name.
- A `policy.yaml` beside a `--config-file` overrides a stricter registered default for the same rule name.
- The package exposes `ConfigOpts`, `Enforcer`, `RuleDefault`, and `PolicyNotAuthorized` with the signatures listed in this contract.
- The submitted package source does not import the forbidden upstream package `oslo_policy`.

## Constraints

- Forbidden imports: `oslo_policy`.
- Do not implement http:/https: external checks.
- Do not implement OpenStack service policy farms.
- Do not implement runtime import of oslo_policy.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After `ConfigOpts` is initialized with `args=[]` and `register_default` installs `role:admin`, `enforce` returns True for credentials whose `roles` include `admin` and False otherwise.
- **B002** — A registered rule of `@` authorizes empty credentials.
- **B003** — When `do_raise=True` and the check fails, `enforce` raises `PolicyNotAuthorized` whose message includes the rule name.
- **B004** — A `policy.yaml` beside a `--config-file` overrides a stricter registered default for the same rule name.
- **B005** — The package exposes `ConfigOpts`, `Enforcer`, `RuleDefault`, and `PolicyNotAuthorized` with the signatures listed in this contract.
- **B006** — The submitted package source does not import the forbidden upstream package `oslo_policy`.
<!-- featureliftbench:behavior-clauses:end -->
