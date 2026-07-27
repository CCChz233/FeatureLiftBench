"""Session token helpers."""

from __future__ import annotations

import secrets


def generate_token() -> str:
    """Create a new opaque session token."""
    return secrets.token_hex(16)


def normalize_token(token: str) -> str:
    """Normalize token strings for registry lookup."""
    return token.strip().lower()
