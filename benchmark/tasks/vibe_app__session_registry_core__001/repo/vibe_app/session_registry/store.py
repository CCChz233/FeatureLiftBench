"""In-memory session storage."""

from __future__ import annotations

from typing import Any


class SessionStore:
    """Simple in-memory session backing store."""

    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}

    def create(self, session_id: str, data: dict[str, Any]) -> dict[str, Any]:
        payload = dict(data)
        self._sessions[session_id] = payload
        return payload

    def get(self, session_id: str) -> dict[str, Any] | None:
        stored = self._sessions.get(session_id)
        return dict(stored) if stored is not None else None

    def destroy(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None
