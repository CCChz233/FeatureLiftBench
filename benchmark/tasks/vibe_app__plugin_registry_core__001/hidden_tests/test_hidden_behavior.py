from featurelifted import BasePlugin
from featurelifted import PluginRegistry
from featurelifted.state import GLOBAL_STATE
from featurelifted.state import reset_state


class UpperPlugin(BasePlugin):
    name = "upper"

    def run(self, payload: dict) -> dict:
        return {"text": str(payload.get("text", "")).upper()}


def test_metaclass_registers_plugin_classes() -> None:
    reset_state()

    class AutoPlugin(BasePlugin):
        name = "auto"

        def run(self, payload: dict) -> dict:
            return payload

    registry = PluginRegistry()
    classes = registry.discover_classes()

    assert "auto" in classes
    assert classes["auto"] is AutoPlugin


def test_register_tracks_names_in_global_state() -> None:
    reset_state()
    registry = PluginRegistry()
    registry.register(UpperPlugin())

    assert GLOBAL_STATE["plugin_names"] == ["upper"]


def test_run_raises_for_disabled_plugin() -> None:
    registry = PluginRegistry()
    plugin = UpperPlugin()
    plugin.enabled = False
    registry.register(plugin)

    try:
        registry.run("upper", {"text": "x"})
        raised = False
    except RuntimeError as exc:
        raised = True
        assert "disabled" in str(exc)

    assert raised
