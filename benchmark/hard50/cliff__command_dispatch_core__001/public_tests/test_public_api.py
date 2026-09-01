from __future__ import annotations

import argparse
import io
import featurelifted as fl


class Greet(fl.Command):
    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument("name")
        parser.add_argument("--loud", action="store_true")
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> int:
        text = f"hello {parsed_args.name}"
        self.app.stdout.write(text.upper() if parsed_args.loud else text)
        return 7


def test_registered_name_is_matched_literally() -> None:
    manager = fl.CommandManager(convert_underscores=False)
    manager.add_command("image_list", Greet)
    factory, name, remainder = manager.find_command(["image_list", "Ada"])
    assert factory is Greet
    assert name == "image_list"
    assert remainder == ["Ada"]


def test_find_longest_named_command() -> None:
    manager = fl.CommandManager()
    manager.add_command("server", Greet)
    manager.add_command("server start", Greet)
    factory, name, remainder = manager.find_command(
        ["server", "start", "Ada", "--loud"]
    )
    assert factory is Greet
    assert name == "server start"
    assert remainder == ["Ada", "--loud"]


def test_app_parses_and_dispatches_take_action() -> None:
    output = io.StringIO()
    manager = fl.CommandManager()
    manager.add_command("greet", Greet)
    app = fl.App("demo", "1.0", manager, stdout=output, stderr=io.StringIO())
    assert app.run(["greet", "Ada", "--loud"]) == 7
    assert output.getvalue() == "HELLO ADA"


def test_command_false_result_becomes_success() -> None:
    class NoResult(fl.Command):
        def take_action(self, parsed_args: argparse.Namespace):
            return None

    manager = fl.CommandManager()
    app = fl.App("demo", "1.0", manager, stdout=io.StringIO(), stderr=io.StringIO())
    command = NoResult(app=app, app_args=argparse.Namespace())
    assert command.run(argparse.Namespace()) == 0
