# FeatureLift Task: Session token registry

Extract a task-scoped subset of `vibe_app` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    SessionRegistry,
    state,
)
```

## Required API Details

- `SessionRegistry(store: 'SessionStore | None' = None) -> 'None'` class constructor
  - `SessionRegistry.register(self, user_id: 'str', *, metadata: 'dict[str, Any] | None' = None) -> 'str'`
  - `SessionRegistry.resolve(self, token: 'str') -> 'dict[str, Any] | None'`
  - `SessionRegistry.revoke(self, token: 'str') -> 'bool'`
- `state` module must be importable
  - `state.GLOBAL_STATE` constant must exist
  - `state.reset_state() -> 'None'`

## Required Behavior

- The extracted feature must support this observable behavior: register sessions and return opaque tokens. Required observable cases include register and resolve session; revoke updates global state session list.
- The extracted feature must support this observable behavior: resolve sessions by normalized token strings. Required observable cases include register and resolve session; resolve normalizes token case; revoke updates global state session list.
- The extracted feature must support this observable behavior: revoke sessions and remove ids from GLOBAL_STATE. Required observable cases include revoke removes session; register tracks session ids in global state; revoke updates global state session list.
- The extracted feature must support this observable behavior: store user_id and metadata payloads in SessionStore. Required observable cases include revoke updates global state session list.
- The package exposes the required task API paths `featurelifted.SessionRegistry`, `featurelifted.SessionRegistry.register`, `featurelifted.SessionRegistry.resolve`, `featurelifted.SessionRegistry.revoke`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.

## Constraints

- Forbidden imports: `vibe_app`.
- Do not implement Flask-ish routes and HTTP cookie handling.
- Do not implement YAML bootstrap and pricing/CSV modules.
- Do not implement get_session_v1 and lookup_session_legacy wrong helpers.
- Do not implement app factory and middleware clutter.
- Do not implement original project tests and CLI entrypoints.

## Public vs Hidden Tests

Benchmark evaluator tests remain private. Each evaluator test maps to the public behaviors above and only deepens examples, boundaries, or combinations within those declared behaviors.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — The extracted feature must support this observable behavior: register sessions and return opaque tokens. Required observable cases include register and resolve session; revoke updates global state session list.
- **B002** — The extracted feature must support this observable behavior: resolve sessions by normalized token strings. Required observable cases include register and resolve session; resolve normalizes token case; revoke updates global state session list.
- **B003** — The extracted feature must support this observable behavior: revoke sessions and remove ids from GLOBAL_STATE. Required observable cases include revoke removes session; register tracks session ids in global state; revoke updates global state session list.
- **B004** — The extracted feature must support this observable behavior: store user_id and metadata payloads in SessionStore. Required observable cases include revoke updates global state session list.
- **B005** — The package exposes the required task API paths `featurelifted.SessionRegistry`, `featurelifted.SessionRegistry.register`, `featurelifted.SessionRegistry.resolve`, `featurelifted.SessionRegistry.revoke`, `featurelifted.state`, `featurelifted.state.GLOBAL_STATE`, `featurelifted.state.reset_state` with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: vibe_app.
<!-- featureliftbench:behavior-clauses:end -->
