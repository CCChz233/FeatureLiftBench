"""Process-wide mutable registry used throughout the app."""

from __future__ import annotations

from typing import Any

GLOBAL_STATE: dict[str, Any] = {
    "bootstrapped": False,
    "config": {},
    "config_paths": [],
    "load_count": 0,
    "feature_flags": {},
    "last_csv_job": None,
    "sessions": [],
    "rules_evaluated": 0,
}


def reset_state() -> None:
    """Testing helper — not part of benchmark APIs."""
    GLOBAL_STATE.clear()
    GLOBAL_STATE.update(
        {
            "bootstrapped": False,
            "config": {},
            "config_paths": [],
            "load_count": 0,
            "feature_flags": {},
            "last_csv_job": None,
            "sessions": [],
            "rules_evaluated": 0,
        }
    )


def touch(key: str, value: Any = True) -> None:
    GLOBAL_STATE.setdefault("touches", []).append((key, value))
