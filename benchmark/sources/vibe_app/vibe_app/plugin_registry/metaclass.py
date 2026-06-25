"""Metaclass that registers plugin subclasses."""

from __future__ import annotations

from typing import Any

from vibe_app.state import GLOBAL_STATE


class PluginMeta(type):
    """Register concrete plugin subclasses in GLOBAL_STATE."""

    def __init__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        if name == "BasePlugin":
            return
        if not getattr(cls, "name", ""):
            return
        registry = GLOBAL_STATE.setdefault("plugin_classes", {})
        registry[cls.name] = cls
