"""Plugin registry with metaclass-based discovery."""

from vibe_app.plugin_registry.base import BasePlugin
from vibe_app.plugin_registry.metaclass import PluginMeta
from vibe_app.plugin_registry.registry import PluginRegistry

__all__ = ["BasePlugin", "PluginMeta", "PluginRegistry"]
