from __future__ import annotations

from featurelifted import App, Controller, ex


class HelloController(Controller):
    class Meta:
        label = "base"

    @ex(help="say hello")
    def hello(self):
        return "hello-ok"


class DemoApp(App):
    class Meta:
        label = "demo"
        handlers = [HelloController]
        argv = ["hello"]
        catch_signals = None
        exit_on_close = False
        core_system_config_files = []
        core_user_config_files = []
        config_files = []
        core_system_config_dirs = []
        core_user_config_dirs = []
        config_dirs = []
        core_system_template_dirs = []
        core_user_template_dirs = []
        core_system_plugin_dirs = []
        core_user_plugin_dirs = []
        plugin_dirs = []
        extensions = []


def test_controller_command_runs() -> None:
    with DemoApp() as app:
        assert app.run() == "hello-ok"


def test_post_setup_hook_runs() -> None:
    seen: list[str] = []

    def mark(app):
        seen.append(app._meta.label)

    class Hooked(DemoApp):
        class Meta:
            hooks = [("post_setup", mark)]

    with Hooked() as app:
        app.run()
    assert seen == ["demo"]


def test_setup_installs_controller() -> None:
    with DemoApp() as app:
        assert app.controller is not None
        assert app.run() == "hello-ok"
