# FeatureLift Task: Command registration, argv parsing, and dispatch

Extract a deterministic in-process slice of Cliff command registration and application dispatch into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    App,
    Command,
    CommandManager,
)
```

## Required API Details

- `Command(app: App, app_args: argparse.Namespace | None, cmd_name: str | None = None)` class constructor
  - `Command.get_parser(self, prog_name: str) -> argparse.ArgumentParser`
  - `Command.take_action(self, parsed_args: argparse.Namespace)`
  - `Command.run(self, parsed_args: argparse.Namespace) -> int`
- `CommandManager(namespace: str | None = None, convert_underscores: bool = True, *, ignored_modules: Iterable[str] | None = None)` class constructor
  - `CommandManager.add_command(self, name: str, command_class: type[Command]) -> None`
  - `CommandManager.find_command(self, argv: list[str]) -> tuple[type[Command], str, list[str]]`
  - `CommandManager.get_command_names(self, group: str | None = None) -> list[str]`
- `App(description: str | None, version: str | None, command_manager: CommandManager, stdin=None, stdout=None, stderr=None, interactive_app_factory=None, deferred_help: bool = False)` class constructor
  - `App.run(self, argv: list[str]) -> int`
  - `App.run_subcommand(self, argv: list[str]) -> int`

## Required Behavior

- After command classes are registered by name, `find_command` chooses the longest matching multi-word command, leaves subsequent option and operand tokens untouched, and raises `ValueError` when no command matches.
- `add_command` stores and matches the command name as given. `find_command` looks up that stored name; `convert_underscores=False` still requires the literal registered name. Underscore-to-space rewriting of plugin entry-point names is out of scope.
- A `Command` subclass can extend its `argparse` parser in `get_parser`; `App.run` parses global arguments separately, parses the remaining command arguments with that parser, and invokes `take_action` with the resulting namespace.
- `Command.run` returns the value from `take_action`, except that a false or `None` result becomes exit status 0.
- `App.run` returns exit status 2 for an unknown command and exit status 1 when command execution raises an ordinary exception. The `--debug` flag does not change those exit statuses for unknown commands.
- The command instance receives the invoking `App`, parsed global application arguments (including `verbose_level`, which `-v`/`--verbose` raises from the default of 1 to 2), and the matched command name, so `take_action` can observe both application state and command operands.

## Constraints

- Forbidden imports: `cliff`.
- Do not implement entry-point and stevedore discovery.
- Do not implement interactive cmd2 mode, shell completion, help plugins, and formatter plugins.
- Do not implement logging configuration, fuzzy suggestions, and terminal paging behavior.
- Do not implement runtime import of `cliff`.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — After command classes are registered by name, `find_command` chooses the longest matching multi-word command, leaves subsequent option and operand tokens untouched, and raises `ValueError` when no command matches.
- **B002** — `add_command` stores and matches the command name as given. `find_command` looks up that stored name; `convert_underscores=False` still requires the literal registered name. Underscore-to-space rewriting of plugin entry-point names is out of scope.
- **B003** — A `Command` subclass can extend its `argparse` parser in `get_parser`; `App.run` parses global arguments separately, parses the remaining command arguments with that parser, and invokes `take_action` with the resulting namespace.
- **B004** — `Command.run` returns the value from `take_action`, except that a false or `None` result becomes exit status 0.
- **B005** — `App.run` returns exit status 2 for an unknown command and exit status 1 when command execution raises an ordinary exception. The `--debug` flag does not change those exit statuses for unknown commands.
- **B006** — The command instance receives the invoking `App`, parsed global application arguments (including `verbose_level`, which `-v`/`--verbose` raises from the default of 1 to 2), and the matched command name, so `take_action` can observe both application state and command operands.
<!-- featureliftbench:behavior-clauses:end -->
