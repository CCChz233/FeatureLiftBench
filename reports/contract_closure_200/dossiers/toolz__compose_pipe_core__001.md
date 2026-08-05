# toolz__compose_pipe_core__001

- release: `external50`
- lift: `Direct`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `8/15`

## Required API

- `featurelifted.compose` (function) `(*funcs)`
- `featurelifted.pipe` (function) `(data, *funcs)`
- `featurelifted.curry` (class)
- `featurelifted.identity` (function) `(x)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: compose right-to-left callable pipelines. Required observable cases include compose and pipe.
- **B002**: The extracted feature must support this observable behavior: pipe left-to-right value pipelines. Required observable cases include pipe left to right.
- **B003**: The extracted feature must support this observable behavior: curry partial application. Required observable cases include curry partial; curry kwargs.
- **B004**: identity returns its argument unchanged.
- **B005**: The package exposes compose/pipe/curry/identity with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: toolz.

## Tests

### `public_tests/test_public_api.py::test_compose_and_pipe`

- mapping: `B001`
- API: `featurelifted.compose, featurelifted.pipe`
- risk: `none`
- A001 `assert` L8: `f(3) == 7`
- A002 `assert` L9: `pipe(3, lambda x: x * 2, lambda x: x + 1) == 7`

### `public_tests/test_public_api.py::test_curry_partial`

- mapping: `B002`
- API: `featurelifted.curry`
- risk: `none`
- A001 `assert` L14: `add(1)(2) == 3`
- A002 `assert` L15: `add(1, 2) == 3`

### `public_tests/test_public_api.py::test_identity`

- mapping: `B003`
- API: `featurelifted.compose, featurelifted.identity`
- risk: `none`
- A001 `assert` L19: `identity(42) == 42`
- A002 `assert` L20: `compose(identity, identity)(5) == 5`

### `hidden_tests/test_hidden_behavior.py::test_compose_right_to_left`

- mapping: `B001, B004`
- API: `featurelifted.compose`
- risk: `none`
- A001 `assert` L20: `compose(a, b)(3) == 7`
- A002 `assert` L21: `order == ['b', 'a']`

### `hidden_tests/test_hidden_behavior.py::test_pipe_left_to_right`

- mapping: `B002`
- API: `featurelifted.pipe`
- risk: `none`
- A001 `assert` L35: `pipe(3, a, b) == 8`
- A002 `assert` L36: `order == ['a', 'b']`

### `hidden_tests/test_hidden_behavior.py::test_curry_kwargs`

- mapping: `B003`
- API: `featurelifted.curry`
- risk: `none`
- A001 `assert` L44: `cf(1)(2) == 3`
- A002 `assert` L45: `cf(1, c=4)(2) == 7`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L54: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.compose, featurelifted.curry, featurelifted.identity, featurelifted.pipe`
- risk: `none`
- A001 `assert` L5: `callable(compose) and callable(pipe) and callable(identity)`
- A002 `assert` L6: `curry is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `toolz`
- source entrypoints: `none`
- oracle source files: `toolz/functoolz.py, toolz/__init__.py`
- runtime dependencies: `none`
- oracle notes: Direct extract of compose/pipe/curry/identity.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
