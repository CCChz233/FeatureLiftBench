# keyring__backend_select_core__hard3_001

- release: `frozen_python150`
- lift: `Composite`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `9/25`

## Required API

- `featurelifted.ChainerBackend` (class) `(backends: 'list[Backend] | tuple[Backend, ...]') -> 'None'`
- `featurelifted.ChainerBackend.get_password` (method) `(self, service: 'str', username: 'str') -> 'str | None'`
- `featurelifted.ChainerBackend.set_password` (method) `(self, service: 'str', username: 'str', password: 'str') -> 'None'`
- `featurelifted.MemoryBackend` (class) `(label: 'str', priority: 'float' = 1.0, data: 'dict[tuple[str, str], str]' = <factory>) -> None`
- `featurelifted.MemoryBackend.get_credential` (method) `(self, service: 'str', username: 'str | None' = None) -> 'Credential | None'`
- `featurelifted.MemoryBackend.get_password` (method) `(self, service: 'str', username: 'str') -> 'str | None'`
- `featurelifted.MemoryBackend.set_password` (method) `(self, service: 'str', username: 'str', password: 'str') -> 'None'`
- `featurelifted.select_backend` (function) `(backends: 'list[Any] | tuple[Any, ...]', env: 'dict[str, str] | None' = None) -> 'Backend'`
- `featurelifted.Backend` (class) `()`
- `featurelifted.BackendNotFound` (exception)
- `featurelifted.Credential` (class) `(username: 'str', password: 'str') -> None`
- `featurelifted.ErrorBackend` (class) `(label: 'str' = 'error', priority: 'float' = 1.0, error: 'Exception' = <factory>) -> None`
- `featurelifted.FailBackend` (class) `()`
- `featurelifted.PasswordDeleteError` (exception)
- `featurelifted.PasswordSetError` (exception)

## Public Behaviors

- **B001**: Backend implementations expose priority and the declared password and credential operations used by selection and chaining.
- **B002**: MemoryBackend stores deterministic credentials and can discover a stored username when get_credential is called without one.
- **B003**: When no viable backend exists, selection returns FailBackend and its password operations fail through the declared error API.
- **B004**: ErrorBackend raises its configured failure so ChainerBackend fallback paths can be observed.
- **B005**: ChainerBackend sorts viable backends by descending priority, skips backend failures, and returns the first successful password result.
- **B006**: select_backend chooses the highest-priority non-negative viable backend and falls back to FailBackend when none qualifies.
- **B007**: When PYTHON_KEYRING_BACKEND is provided, select_backend matches the requested backend name or class and raises BackendNotFound if it is unavailable.
- **B008**: Credential values and password set/delete failures use the declared Credential, PasswordSetError, and PasswordDeleteError types.
- **B009**: The package exposes the required task API paths `featurelifted.ChainerBackend`, `featurelifted.ChainerBackend.get_password`, `featurelifted.ChainerBackend.set_password`, `featurelifted.MemoryBackend`, `featurelifted.MemoryBackend.get_credential`, `featurelifted.MemoryBackend.get_password`, `featurelifted.MemoryBackend.set_password`, `featurelifted.select_backend`, `featurelifted.Backend`, `featurelifted.BackendNotFound`, `featurelifted.Credential`, `featurelifted.ErrorBackend`, and 3 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_select_highest_priority_backend`

- mapping: `B006`
- API: `featurelifted.select_backend`
- risk: `ordering_semantics`
- A001 `assert` L21: `isinstance(select_backend([Low, High]), High)`

### `public_tests/test_public_contract.py::test_env_override_selects_named_backend`

- mapping: `B006, B007`
- API: `featurelifted.select_backend`
- risk: `none`
- A001 `assert` L27: `isinstance(selected, Low)`

### `public_tests/test_public_contract.py::test_chainer_get_password_uses_first_backend_with_value`

- mapping: `B006, B008`
- API: `featurelifted.ChainerBackend, featurelifted.MemoryBackend`
- risk: `none`
- A001 `assert` L37: `backend.get_password('svc', 'user') == 'secret'`

### `hidden_tests/test_hidden_contract.py::test_negative_priority_is_excluded_and_fail_backend_is_default`

- mapping: `B001, B002, B003, B005, B006, B007`
- API: `featurelifted.BackendNotFound, featurelifted.FailBackend, featurelifted.select_backend`
- risk: `exception_semantics, ordering_semantics`
- A001 `assert` L32: `isinstance(select_backend([Negative]), FailBackend)`
- A002 `raises` L34: `pytest.raises(BackendNotFound)`

### `hidden_tests/test_hidden_contract.py::test_chainer_skips_backend_errors_on_get_password`

- mapping: `B008`
- API: `featurelifted.ChainerBackend, featurelifted.ErrorBackend, featurelifted.MemoryBackend`
- risk: `none`
- A001 `assert` L45: `backend.get_password('svc', 'u') == 'secret'`

### `hidden_tests/test_hidden_contract.py::test_chainer_set_password_falls_back_after_failure`

- mapping: `B004, B008`
- API: `featurelifted.ChainerBackend, featurelifted.ErrorBackend, featurelifted.MemoryBackend`
- risk: `none`
- A001 `assert` L55: `working.get_password('svc', 'u') == 'secret'`

### `hidden_tests/test_hidden_contract.py::test_chainer_set_password_raises_when_all_backends_fail`

- mapping: `B008`
- API: `featurelifted.ChainerBackend, featurelifted.ErrorBackend, featurelifted.PasswordSetError`
- risk: `exception_semantics`
- A001 `raises` L61: `pytest.raises(PasswordSetError)`

### `hidden_tests/test_hidden_contract.py::test_get_credential_can_discover_username`

- mapping: `B008`
- API: `featurelifted.MemoryBackend`
- risk: `none`
- A001 `assert` L71: `credential.username == 'stored-user'`
- A002 `assert` L72: `credential.password == 'secret'`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B009`
- API: `featurelifted.Backend, featurelifted.BackendNotFound, featurelifted.ChainerBackend, featurelifted.Credential, featurelifted.ErrorBackend, featurelifted.FailBackend, featurelifted.MemoryBackend, featurelifted.PasswordDeleteError, featurelifted.PasswordSetError, featurelifted.select_backend`
- risk: `none`
- A001 `assert` L18: `isinstance(ChainerBackend, type)`
- A002 `assert` L19: `hasattr(ChainerBackend, 'get_password')`
- A003 `assert` L20: `hasattr(ChainerBackend, 'set_password')`
- A004 `assert` L21: `isinstance(MemoryBackend, type)`
- A005 `assert` L22: `hasattr(MemoryBackend, 'get_credential')`
- A006 `assert` L23: `hasattr(MemoryBackend, 'get_password')`
- A007 `assert` L24: `hasattr(MemoryBackend, 'set_password')`
- A008 `assert` L25: `callable(select_backend)`
- A009 `assert` L26: `isinstance(Backend, type)`
- A010 `assert` L27: `issubclass(BackendNotFound, BaseException)`
- A011 `assert` L28: `isinstance(Credential, type)`
- A012 `assert` L29: `isinstance(ErrorBackend, type)`
- A013 `assert` L30: `isinstance(FailBackend, type)`
- A014 `assert` L31: `issubclass(PasswordDeleteError, BaseException)`
- A015 `assert` L32: `issubclass(PasswordSetError, BaseException)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `keyring`
- source entrypoints: `keyring.backend.KeyringBackend, keyring.core.get_keyring, keyring.core.load_env, keyring.core._detect_backend, keyring.backends.chainer.ChainerBackend, keyring.backends.fail.Keyring`
- oracle source files: `repo/keyring/backend.py, repo/keyring/core.py, repo/keyring/backends/chainer.py, repo/keyring/backends/fail.py, repo/keyring/backends/null.py, repo/keyring/errors.py, repo/pyproject.toml`
- runtime dependencies: `none`
- oracle notes: Task-scoped backend discovery and failover selection. OS keychains, CLI, config writes, SecretService, KWallet, and Windows/macOS integrations are intentionally excluded. Upstream declares MIT in pyproject.toml; no standalone LICENSE file exists at the pinned commit.
