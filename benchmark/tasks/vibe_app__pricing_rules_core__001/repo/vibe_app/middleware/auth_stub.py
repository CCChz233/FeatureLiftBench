"""Unused auth stub."""

from vibe_app.state import GLOBAL_STATE


def fake_auth(token: str | None) -> bool:
    GLOBAL_STATE.setdefault("auth_checks", 0)
    GLOBAL_STATE["auth_checks"] += 1
    return bool(token)
