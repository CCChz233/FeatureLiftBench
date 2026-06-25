# Task Design: vibe_app__session_registry_core__001

Status: oracle-verified

## Why This Task

Extract session token registry from VibeShop where legacy utils shortcuts and GLOBAL_STATE bookkeeping obscure the canonical registry path.

## Source

| Field | Value |
| --- | --- |
| Source repo | `sources/vibe_app/` |
| Commit | curated |
| License | MIT |
| Difficulty | hard |
| Tags | extreme, multi-task-repo, legacy_vibe_clutter |

## Output API

```python
from featurelifted import SessionRegistry
```

## Module Probes

| Probe | Remove module | Hidden test(s) that must fail |
| --- | --- | --- |
| Token normalization | `session_registry/tokens.py` | `test_resolve_normalizes_token_case` (public) |
| Session store | `session_registry/store.py` | `test_revoke_removes_session` |
| Registry + GLOBAL_STATE | `session_registry/registry.py` | `test_register_tracks_session_ids_in_global_state` |
