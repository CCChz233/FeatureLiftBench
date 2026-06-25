from featurelifted import BasePlugin
from featurelifted import PluginRegistry


class EchoPlugin(BasePlugin):
    name = "echo"

    def run(self, payload: dict) -> dict:
        return {"echo": payload.get("message", "")}


def test_register_and_run_plugin() -> None:
    registry = PluginRegistry()
    plugin = EchoPlugin()

    registry.register(plugin)
    result = registry.run("echo", {"message": "hello"})

    assert result == {"echo": "hello"}


def test_list_plugins_returns_registered_names() -> None:
    registry = PluginRegistry()
    registry.register(EchoPlugin())

    assert registry.list_plugins() == ["echo"]
