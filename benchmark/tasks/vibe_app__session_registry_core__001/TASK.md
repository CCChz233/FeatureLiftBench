# FeatureLift Task: Session token registry

Extract VibeShop session registration, resolution, and revocation as a standalone package.

## Target API

- Import: `from featurelifted import SessionRegistry; from featurelifted.state import GLOBAL_STATE, reset_state`
- Callable: `featurelifted.SessionRegistry.register`
- Signature: `SessionRegistry.register(user_id: str, *, metadata: dict | None = None) -> str`

## Excluded Behavior

- Flask-ish routes and HTTP cookie handling
- YAML bootstrap and pricing/CSV modules
- get_session_v1 and lookup_session_legacy wrong helpers
- app factory and middleware clutter
- original project tests and CLI entrypoints

## Constraints

- Output package: `featurelifted`
- Network access: `false`
- Forbidden upstream imports: `vibe_app`

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise
these clauses but do not introduce additional requirements.

- **B001** — register sessions and return opaque tokens
- **B002** — resolve sessions by normalized token strings
- **B003** — revoke sessions and remove ids from GLOBAL_STATE
- **B004** — store user_id and metadata payloads in SessionStore
- **B005** — the declared target API remains importable and preserves upstream-observable semantics within the included and excluded feature scope
- **B006** — the submitted package does not import forbidden upstream packages: vibe_app
<!-- featureliftbench:behavior-clauses:end -->
