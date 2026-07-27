"""Canonical session registry with global bookkeeping."""

from __future__ import annotations

from typing import Any

from vibe_app.session_registry.store import SessionStore
from vibe_app.session_registry.tokens import generate_token, normalize_token
from vibe_app.state import GLOBAL_STATE


class SessionRegistry:
    """Register, resolve, and revoke user sessions."""

    def __init__(self, store: SessionStore | None = None) -> None:
        self._store = store or SessionStore()

    def register(self, user_id: str, *, metadata: dict[str, Any] | None = None) -> str:
        token = generate_token()
        session_id = normalize_token(token)
        self._store.create(
            session_id,
            {"user_id": user_id, "metadata": dict(metadata or {})},
        )
        sessions = GLOBAL_STATE.setdefault("sessions", [])
        sessions.append(session_id)
        return token

    def resolve(self, token: str) -> dict[str, Any] | None:
        return self._store.get(normalize_token(token))

    def revoke(self, token: str) -> bool:
        session_id = normalize_token(token)
        destroyed = self._store.destroy(session_id)
        if destroyed:
            sessions = GLOBAL_STATE.get("sessions", [])
            if session_id in sessions:
                sessions.remove(session_id)
        return destroyed
