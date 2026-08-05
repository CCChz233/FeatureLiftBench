# python_decouple__config_repository_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `5/17`

## Required API

- `featurelifted.Choices` (class) `(choices, cast=<class 'str'>)`
- `featurelifted.Config` (class) `(repository, environ=None)`
- `featurelifted.Csv` (class) `(cast=<class 'str'>, delimiter=',', strip=' ')`
- `featurelifted.RepositoryDict` (class) `(data)`
- `featurelifted.RepositoryEnv` (class) `(source)`
- `featurelifted.UndefinedValueError` (exception)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: environment variables override repository values. Required observable cases include precedence defaults and casts; csv cast; env file quotes comments and empty; choices and float.
- **B002**: The extracted feature must support this observable behavior: .env quoted-value and comment parsing. Required observable cases include precedence defaults and casts; csv cast; env file quotes comments and empty; choices and float.
- **B003**: The extracted feature must support this observable behavior: required and default value behavior. Required observable cases include precedence defaults and casts; csv cast; env file quotes comments and empty; choices and float.
- **B004**: The extracted feature must support this observable behavior: bool, int, float, Csv, and Choices casting. Required observable cases include precedence defaults and casts; csv cast; env file quotes comments and empty; choices and float.
- **B005**: The package exposes the required task API paths `featurelifted.Choices`, `featurelifted.Config`, `featurelifted.Csv`, `featurelifted.RepositoryDict`, `featurelifted.RepositoryEnv`, `featurelifted.UndefinedValueError` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_precedence_defaults_and_casts`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.Config, featurelifted.RepositoryDict, featurelifted.UndefinedValueError`
- risk: `exception_semantics`
- A001 `assert` L6: `config('PORT', cast=int) == 9000`
- A002 `assert` L7: `config('DEBUG', cast=bool) is False`
- A003 `assert` L8: `config('MISSING', default='x') == 'x'`
- A004 `raises` L9: `pytest.raises(UndefinedValueError)`

### `public_tests/test_public_contract.py::test_csv_cast`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.Config, featurelifted.Csv, featurelifted.RepositoryDict`
- risk: `none`
- A001 `assert` L13: `config('HOSTS', cast=Csv()) == ['a', 'b', 'c']`

### `hidden_tests/test_hidden_contract.py::test_env_file_quotes_comments_and_empty`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.Config, featurelifted.RepositoryEnv`
- risk: `filesystem_resource`
- A001 `assert` L8: `config('NAME') == 'Ada Lovelace'`
- A002 `assert` L9: `config('EMPTY') == ''`
- A003 `assert` L10: `config('FLAG', cast=bool) is True`

### `hidden_tests/test_hidden_contract.py::test_choices_and_float`

- mapping: `B001, B002, B003, B004`
- API: `featurelifted.Choices, featurelifted.Config`
- risk: `exception_semantics`
- A001 `assert` L14: `config('MODE', cast=Choices(['dev', 'prod'])) == 'prod'`
- A002 `assert` L15: `config('RATE', cast=float) == 1.25`
- A003 `raises` L16: `pytest.raises(ValueError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.Choices, featurelifted.Config, featurelifted.Csv, featurelifted.RepositoryDict, featurelifted.RepositoryEnv, featurelifted.UndefinedValueError`
- risk: `none`
- A001 `assert` L14: `isinstance(Choices, type)`
- A002 `assert` L15: `isinstance(Config, type)`
- A003 `assert` L16: `isinstance(Csv, type)`
- A004 `assert` L17: `isinstance(RepositoryDict, type)`
- A005 `assert` L18: `isinstance(RepositoryEnv, type)`
- A006 `assert` L19: `issubclass(UndefinedValueError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `python_decouple`
- source entrypoints: `decouple.Config, decouple.RepositoryEnv, decouple.RepositoryEmpty, decouple.Csv, decouple.Choices`
- oracle source files: `decouple.Config, decouple.RepositoryEnv, decouple.RepositoryEmpty, decouple.Csv, decouple.Choices`
- runtime dependencies: `none`
- oracle notes: Entrypoints are maintainer-private provenance and are never Agent-visible in Main.
- behavior contract lacks a completed review_status
