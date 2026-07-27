"""Base plugin type."""

from __future__ import annotations

from vibe_app.plugin_registry.metaclass import PluginMeta


class BasePlugin(metaclass=PluginMeta):
    """Base class for auto-registered plugins."""

    name: str = ""
    enabled: bool = True

    def run(self, payload: dict) -> dict:
        raise NotImplementedError
