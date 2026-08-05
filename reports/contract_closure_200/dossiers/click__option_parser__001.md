# click__option_parser__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `4/19`

## Required API

- `featurelifted.testing` (module)
- `featurelifted.testing.CliRunner` (class) `(charset: str = 'utf-8', env: Optional[Mapping[str, Optional[str]]] = None, echo_stdin: bool = False, mix_stderr: bool = True) -> None`
- `featurelifted.testing.CliRunner.invoke` (method) `(self, cli: 'BaseCommand', args: Union[Sequence[str], str, NoneType] = None, input: Union[str, bytes, IO[Any], NoneType] = None, env: Optional[Mapping[str, Optional[str]]] = None, catch_exceptions: bool = True, color: bool = False, **extra: Any) -> Result`
- `featurelifted.testing.CliRunner.isolated_filesystem` (method) `(self, temp_dir: Union[str, ForwardRef('os.PathLike[str]'), NoneType] = None) -> Iterator[str]`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: decorate functions as commands and groups. Required observable cases include usage errors prompts and isolated filesystem.
- **B002**: The extracted feature must support this observable behavior: parse options, flags, choices, defaults, integer ranges, and positional arguments. Required observable cases include command options arguments and choice errors; group context flags range and defaults.
- **B003**: The extracted feature must support this observable behavior: invoke commands through CliRunner and capture output, exit code, and exceptions. Required observable cases include usage errors prompts and isolated filesystem.
- **B004**: The extracted feature must support this observable behavior: support nested groups and context object passing. Required observable cases include usage errors prompts and isolated filesystem.
- **B005**: The extracted feature must support this observable behavior: render useful usage/error output for invalid options and bad values. Required observable cases include usage errors prompts and isolated filesystem.
- **B006**: The package exposes the required task API paths `featurelifted.testing`, `featurelifted.testing.CliRunner`, `featurelifted.testing.CliRunner.invoke`, `featurelifted.testing.CliRunner.isolated_filesystem` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_command_options_arguments_and_choice_errors`

- mapping: `B002`
- API: `featurelifted.testing`
- risk: `none`
- A001 `assert` L17: `result.exit_code == 0`
- A002 `assert` L18: `result.output.strip() == 'Ada:slow:3'`
- A003 `assert` L21: `bad.exit_code == 2`
- A004 `assert` L22: `"Invalid value for '--mode'" in bad.output`

### `hidden_tests/test_hidden_behavior.py::test_group_context_flags_range_and_defaults`

- mapping: `B002`
- API: `featurelifted.testing`
- risk: `none`
- A001 `assert` L23: `ok.exit_code == 0`
- A002 `assert` L24: `ok.output.strip() == 'Ada:4:True'`
- A003 `assert` L27: `defaulted.exit_code == 0`
- A004 `assert` L28: `defaulted.output.strip() == 'world:2:False'`
- A005 `assert` L31: `bad.exit_code == 2`
- A006 `assert` L32: `'9 is not in the range 1<=x<=5' in bad.output`

### `hidden_tests/test_hidden_behavior.py::test_usage_errors_prompts_and_isolated_filesystem`

- mapping: `B001, B003, B004, B005`
- API: `featurelifted.testing`
- risk: `filesystem_resource`
- A001 `assert` L43: `prompted.exit_code == 0`
- A002 `assert` L44: `'Name: Ada' in prompted.output`
- A003 `assert` L45: `'hello Ada' in prompted.output`
- A004 `assert` L57: `read_result.exit_code == 0`
- A005 `assert` L58: `read_result.output.strip() == 'ok'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.testing`
- risk: `none`
- A001 `assert` L9: `testing is not None`
- A002 `assert` L10: `isinstance(getattr(testing, 'CliRunner'), type)`
- A003 `assert` L11: `hasattr(getattr(testing, 'CliRunner'), 'invoke')`
- A004 `assert` L12: `hasattr(getattr(testing, 'CliRunner'), 'isolated_filesystem')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `click`
- source entrypoints: `click.command, click.group, click.option, click.argument, click.Choice, click.IntRange, click.echo, click.UsageError, click.testing.CliRunner`
- oracle source files: `none`
- runtime dependencies: `none`
