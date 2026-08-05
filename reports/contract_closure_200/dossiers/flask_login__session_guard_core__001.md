# flask_login__session_guard_core__001

- release: `external50`
- lift: `Composite`
- coupling: `framework_coupling`
- strict validation: `PASS`
- tests/assertions: `6/16`

## Required API

- `featurelifted.LoginManager` (class)
- `featurelifted.LoginManager.init_app` (method)
- `featurelifted.LoginManager.user_loader` (method)
- `featurelifted.LoginManager.login_view` (attribute)
- `featurelifted.UserMixin` (class)
- `featurelifted.login_user` (function)
- `featurelifted.logout_user` (function)
- `featurelifted.login_required` (function)
- `featurelifted.current_user` (attribute)
- `featurelifted.current_user.get_id` (method)
- `featurelifted.current_user.is_authenticated` (attribute)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: login/logout/current_user with UserMixin. Required observable cases include login logout current user; user mixin anonymous.
- **B002**: The extracted feature must support this observable behavior: login_required guards anonymous users. Required observable cases include login required redirects anonymous.
- **B003**: The extracted feature must support this observable behavior: remember flag on login_user. Required observable cases include remember flag.
- **B004**: Tests use Flask test_request_context/test_client only; Flask is an allowed dependency.
- **B005**: The package exposes LoginManager/UserMixin/login_user/logout_user/login_required/current_user with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: flask_login.

## Tests

### `public_tests/test_public_api.py::test_login_logout_current_user`

- mapping: `B001`
- API: `featurelifted.LoginManager, featurelifted.current_user, featurelifted.login_user, featurelifted.logout_user`
- risk: `none`
- A001 `assert` L25: `login_user(user) is True`
- A002 `assert` L27: `user_proxy.is_authenticated`
- A003 `assert` L28: `user_proxy.get_id() == '1'`
- A004 `assert` L31: `not user_proxy.is_authenticated`

### `public_tests/test_public_api.py::test_user_mixin_anonymous`

- mapping: `B002`
- API: `none detected`
- risk: `none`
- A001 `assert` L36: `u.is_authenticated and (not u.is_anonymous)`

### `hidden_tests/test_hidden_behavior.py::test_login_required_redirects_anonymous`

- mapping: `B001, B003, B004`
- API: `featurelifted.LoginManager, featurelifted.login_required`
- risk: `none`
- A001 `assert` L38: `resp.status_code in {302, 401}`

### `hidden_tests/test_hidden_behavior.py::test_remember_flag`

- mapping: `B002`
- API: `featurelifted.LoginManager, featurelifted.login_user`
- risk: `none`
- A001 `assert` L52: `login_user(User('2'), remember=True) is True`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L61: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.LoginManager, featurelifted.LoginManager.init_app, featurelifted.LoginManager.user_loader`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'LoginManager')`
- A002 `assert` L6: `hasattr(featurelifted, 'UserMixin')`
- A003 `assert` L7: `hasattr(featurelifted, 'current_user')`
- A004 `assert` L8: `hasattr(featurelifted, 'login_required')`
- A005 `assert` L9: `hasattr(featurelifted, 'login_user')`
- A006 `assert` L10: `hasattr(featurelifted, 'logout_user')`
- A007 `assert` L11: `callable(featurelifted.LoginManager.init_app)`
- A008 `assert` L12: `callable(featurelifted.LoginManager.user_loader)`

## Dependency / Oracle Evidence

- allowed dependencies: `blinker, click, flask, itsdangerous, jinja2, markupsafe, werkzeug`
- forbidden imports: `flask_login`
- source entrypoints: `none`
- oracle source files: `src/flask_login/login_manager.py, src/flask_login/utils.py, src/flask_login/mixins.py`
- runtime dependencies: `blinker, click, flask, itsdangerous, jinja2, markupsafe, werkzeug`
- oracle notes: Flask test_request_context only; flask allowed, flask_login forbidden.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
