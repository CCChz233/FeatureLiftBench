"""Runtime plugin registry."""

from __future__ import annotations

from typing import Any

from vibe_app.plugin_registry.base import BasePlugin
from vibe_app.state import GLOBAL_STATE


class PluginRegistry:
    """Register plugin instances and resolve them by name."""

    def __init__(self) -> None:
        self._instances: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> str:
        if not plugin.name:
            raise ValueError("plugin must define a name")
        self._instances[plugin.name] = plugin
        names = GLOBAL_STATE.setdefault("plugin_names", [])
        if plugin.name not in names:
            names.append(plugin.name)
        return plugin.name

    def get(self, name: str) -> BasePlugin | None:
        return self._instances.get(name)

    def list_plugins(self) -> list[str]:
        return sorted(self._instances)

    def run(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        plugin = self.get(name)
        if plugin is None:
            raise KeyError(name)
        if not plugin.enabled:
            raise RuntimeError(f"plugin {name!r} is disabled")
        return plugin.run(payload)

    def discover_classes(self) -> dict[str, type[BasePlugin]]:
        """Return plugin classes registered via PluginMeta."""
        return dict(GLOBAL_STATE.get("plugin_classes", {}))
