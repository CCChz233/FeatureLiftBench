# more_itertools__recipes_core__001

- release: `external50`
- lift: `Direct`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `9/11`

## Required API

- `featurelifted.chunked` (function) `(iterable, n, strict=False)`
- `featurelifted.first` (function) `(iterable, default=...)`
- `featurelifted.unique_everseen` (function) `(iterable, key=None)`
- `featurelifted.consume` (function) `(iterator, n=None)`
- `featurelifted.windowed` (function) `(seq, n, fillvalue=None, step=1)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: chunked splits iterables and first returns the first element. Required observable cases include chunked and first.
- **B002**: The extracted feature must support this observable behavior: unique_everseen deduplicates preserving order. Required observable cases include unique everseen; unique everseen key.
- **B003**: The extracted feature must support this observable behavior: consume advances iterators and windowed yields sliding tuples. Required observable cases include consume and windowed; windowed fillvalue; consume all.
- **B004**: chunked strict=True raises ValueError when the iterable length is not divisible by n.
- **B005**: The package exposes chunked/first/unique_everseen/consume/windowed with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: more_itertools.

## Tests

### `public_tests/test_public_api.py::test_chunked_and_first`

- mapping: `B001`
- API: `featurelifted.chunked, featurelifted.first`
- risk: `none`
- A001 `assert` L7: `list(chunked(range(5), 2)) == [[0, 1], [2, 3], [4]]`
- A002 `assert` L8: `first((x for x in [0, 1, 2])) == 0`

### `public_tests/test_public_api.py::test_unique_everseen`

- mapping: `B002`
- API: `featurelifted.unique_everseen`
- risk: `none`
- A001 `assert` L12: `list(unique_everseen([1, 2, 1, 3, 2])) == [1, 2, 3]`

### `public_tests/test_public_api.py::test_consume_and_windowed`

- mapping: `B003`
- API: `featurelifted.consume, featurelifted.windowed`
- risk: `none`
- A001 `assert` L18: `next(it) == 2`
- A002 `assert` L19: `list(windowed([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]`

### `hidden_tests/test_hidden_behavior.py::test_chunked_strict`

- mapping: `B001`
- API: `featurelifted.chunked`
- risk: `none`
- A001 `assert` L12: `False`

### `hidden_tests/test_hidden_behavior.py::test_unique_everseen_key`

- mapping: `B002`
- API: `featurelifted.unique_everseen`
- risk: `none`
- A001 `assert` L19: `list(unique_everseen(data, key=str.lower)) == ['A', 'B']`

### `hidden_tests/test_hidden_behavior.py::test_windowed_fillvalue`

- mapping: `B003`
- API: `featurelifted.windowed`
- risk: `none`
- A001 `assert` L23: `list(windowed([1, 2], 3, fillvalue=0)) == [(1, 2, 0)]`

### `hidden_tests/test_hidden_behavior.py::test_consume_all`

- mapping: `B004`
- API: `featurelifted.consume`
- risk: `none`
- A001 `assert` L29: `list(it) == []`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L38: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.chunked, featurelifted.consume, featurelifted.first, featurelifted.unique_everseen, featurelifted.windowed`
- risk: `none`
- A001 `assert` L5: `all((callable(x) for x in (chunked, consume, first, unique_everseen, windowed)))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `more_itertools`
- source entrypoints: `none`
- oracle source files: `more_itertools/recipes.py, more_itertools/more.py, more_itertools/__init__.py`
- runtime dependencies: `none`
- oracle notes: Direct extract of chunked/first/unique_everseen/consume/windowed helpers.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
