# typer__command_parser_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/9`

## Required API

- `featurelifted.testing` (module)
- `featurelifted.testing.CliRunner` (class) `(charset: str = 'utf-8', env: Optional[Mapping[str, Optional[str]]] = None, echo_stdin: bool = False, mix_stderr: bool = True) -> None`
- `featurelifted.testing.CliRunner.invoke` (method) `(self, app: Typer, args: Union[Sequence[str], str, NoneType] = None, input: Union[str, bytes, IO[Any], NoneType] = None, env: Optional[Mapping[str, Optional[str]]] = None, catch_exceptions: bool = True, color: bool = False, **extra: Any) -> Result`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: build commands from type-annotated functions. Required observable cases include subcommands and optional path.
- **B002**: The extracted feature must support this observable behavior: parse options, arguments, defaults, and choices. Required observable cases include typed options and arguments; subcommands and optional path.
- **B003**: The extracted feature must support this observable behavior: invoke Typer apps through CliRunner. Required observable cases include typed options and arguments; subcommands and optional path; choice validation.
- **B004**: The extracted feature must support this observable behavior: nested subcommands and context passing. Required observable cases include subcommands and optional path.
- **B005**: The extracted feature must support this observable behavior: usage errors for invalid parameters. Required observable cases include subcommands and optional path.
- **B006**: The package exposes the required task API paths `featurelifted.testing`, `featurelifted.testing.CliRunner`, `featurelifted.testing.CliRunner.invoke` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_typed_options_and_arguments`

- mapping: `B002, B003`
- API: `featurelifted.testing`
- risk: `none`
- A001 `assert` L17: `result.exit_code == 0`
- A002 `assert` L18: `result.output.strip() == 'Greetings Ada Greetings Ada'`

### `hidden_tests/test_hidden_behavior.py::test_subcommands_and_optional_path`

- mapping: `B001, B002, B003, B004, B005`
- API: `featurelifted.testing`
- risk: `filesystem_resource`
- A001 `assert` L20: `ok.exit_code == 0`
- A002 `assert` L21: `ok.output.strip() == 'create:Ada:a@example.com'`
- A003 `assert` L24: `bad.exit_code != 0`

### `hidden_tests/test_hidden_behavior.py::test_choice_validation`

- mapping: `B003`
- API: `featurelifted.testing`
- risk: `none`
- A001 `assert` L36: `bad.exit_code != 0`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.testing`
- risk: `none`
- A001 `assert` L9: `testing is not None`
- A002 `assert` L10: `isinstance(getattr(testing, 'CliRunner'), type)`
- A003 `assert` L11: `hasattr(getattr(testing, 'CliRunner'), 'invoke')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `typer, click`
- source entrypoints: `typer.Typer, typer.run, typer.testing.CliRunner, typer.Argument, typer.Option`
- oracle source files: `none`
- runtime dependencies: `none`
