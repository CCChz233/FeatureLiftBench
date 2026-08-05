# boltons__iterutils_core__001

- release: `frozen_python150`
- lift: `Adapted`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `15/28`

## Required API

- `featurelifted.chunked` (function) `(src, size, count=None, **kw)`
- `featurelifted.windowed` (function) `(src, size)`
- `featurelifted.pairwise` (function) `(src)`
- `featurelifted.unique` (function) `(src, key=None)`
- `featurelifted.bucketize` (function) `(src, key=<class 'bool'>, value_transform=None, key_filter=None)`
- `featurelifted.remap` (function) `(root, visit=<function default_visit>, enter=<function default_enter>, exit=<function default_exit>, **kwargs)`
- `featurelifted.get_path` (function) `(root, path, default=<object object>)`
- `featurelifted.partition` (function) `(src, key=<class 'bool'>)`
- `featurelifted.iterutils` (module)
- `featurelifted.iterutils.backoff` (function) `(start, stop, count=None, factor=2.0, jitter=False)`
- `featurelifted.iterutils.chunk_ranges` (function) `(input_size, chunk_size, input_offset=0, overlap_size=0, align=False)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: chunked and windowed iteration with size validation. Required observable cases include chunked basic; windowed and pairwise; chunked fill padding; chunked count limit; pairwise sliding window; windowed size three.
- **B002**: The extracted feature must support this observable behavior: pairwise adjacent pairs. Required observable cases include windowed and pairwise; pairwise sliding window.
- **B003**: The extracted feature must support this observable behavior: unique with optional key function. Required observable cases include unique and bucketize; unique key preserves first of length.
- **B004**: The extracted feature must support this observable behavior: bucketize grouping with key_filter and value_transform. Required observable cases include unique and bucketize; bucketize value transform.
- **B005**: The extracted feature must support this observable behavior: remap tree walk with visit/enter/exit hooks. Required observable cases include windowed size three.
- **B006**: The extracted feature must support this observable behavior: get_path nested dict/list access. Required observable cases include get path missing raises.
- **B007**: The package exposes the required task API paths `featurelifted.chunked`, `featurelifted.windowed`, `featurelifted.pairwise`, `featurelifted.unique`, `featurelifted.bucketize`, `featurelifted.remap`, `featurelifted.get_path`, `featurelifted.partition`, `featurelifted.iterutils`, `featurelifted.iterutils.backoff`, `featurelifted.iterutils.chunk_ranges` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_chunked_basic`

- mapping: `B001`
- API: `featurelifted.chunked`
- risk: `none`
- A001 `assert` L7: `chunked(range(7), 3) == [[0, 1, 2], [3, 4, 5], [6]]`

### `public_tests/test_public_api.py::test_windowed_and_pairwise`

- mapping: `B001, B002`
- API: `featurelifted.pairwise, featurelifted.windowed`
- risk: `none`
- A001 `assert` L11: `windowed([1, 2, 3, 4], 3) == [(1, 2, 3), (2, 3, 4)]`
- A002 `assert` L12: `pairwise([1, 2, 3]) == [(1, 2), (2, 3)]`

### `public_tests/test_public_api.py::test_unique_and_bucketize`

- mapping: `B003, B004`
- API: `featurelifted.bucketize, featurelifted.unique`
- risk: `none`
- A001 `assert` L16: `unique([1, 2, 1, 3, 2]) == [1, 2, 3]`
- A002 `assert` L17: `bucketize(['aa', 'b', 'ccc'], key=len) == {2: ['aa'], 1: ['b'], 3: ['ccc']}`

### `hidden_tests/test_hidden_behavior.py::test_chunked_fill_padding`

- mapping: `B001`
- API: `featurelifted.chunked, featurelifted.iterutils`
- risk: `none`
- A001 `assert` L13: `chunked(range(10), 3, fill=None) == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, None, None]]`

### `hidden_tests/test_hidden_behavior.py::test_chunked_count_limit`

- mapping: `B001`
- API: `featurelifted.chunked, featurelifted.iterutils`
- risk: `none`
- A001 `assert` L22: `chunked(range(10), 3, count=2) == [[0, 1, 2], [3, 4, 5]]`

### `hidden_tests/test_hidden_behavior.py::test_unique_key_preserves_first_of_length`

- mapping: `B003`
- API: `featurelifted.iterutils, featurelifted.unique`
- risk: `none`
- A001 `assert` L27: `unique(words, key=lambda x: len(x)) == ['hi', 'hello', 'bye']`

### `hidden_tests/test_hidden_behavior.py::test_bucketize_value_transform`

- mapping: `B004`
- API: `featurelifted.bucketize, featurelifted.iterutils`
- risk: `none`
- A001 `assert` L33: `out == {2: ['AA'], 3: ['BBB'], 1: ['C']}`

### `hidden_tests/test_hidden_behavior.py::test_partition_truthiness`

- mapping: `B007`
- API: `featurelifted.iterutils, featurelifted.partition`
- risk: `none`
- A001 `assert` L39: `partition([0, 1, 2, 3]) == ([1, 2, 3], [0])`

### `hidden_tests/test_hidden_behavior.py::test_get_path_missing_raises`

- mapping: `B006`
- API: `featurelifted.get_path, featurelifted.iterutils`
- risk: `exception_semantics, filesystem_resource`
- A001 `assert` L44: `get_path(root, ('users', 0, 'name')) == 'ada'`
- A002 `raises` L45: `pytest.raises(KeyError)`

### `hidden_tests/test_hidden_behavior.py::test_pairwise_sliding_window`

- mapping: `B001, B002`
- API: `featurelifted.iterutils, featurelifted.pairwise`
- risk: `none`
- A001 `assert` L50: `list(pairwise(range(4))) == [(0, 1), (1, 2), (2, 3)]`

### `hidden_tests/test_hidden_behavior.py::test_windowed_size_three`

- mapping: `B001, B005`
- API: `featurelifted.iterutils, featurelifted.windowed`
- risk: `none`
- A001 `assert` L54: `list(windowed(range(5), 3)) == [(0, 1, 2), (1, 2, 3), (2, 3, 4)]`

### `hidden_tests/test_hidden_behavior.py::test_chunk_ranges_with_overlap`

- mapping: `B007`
- API: `featurelifted.iterutils`
- risk: `none`
- A001 `assert` L58: `list(chunk_ranges(10, 4, overlap_size=1)) == [(0, 4), (3, 7), (6, 10)]`

### `hidden_tests/test_hidden_behavior.py::test_backoff_exponential_growth`

- mapping: `B007`
- API: `featurelifted.iterutils`
- risk: `none`
- A001 `assert` L62: `list(backoff(1, 100, count=4)) == [1.0, 2.0, 4.0, 8.0]`

### `hidden_tests/test_hidden_behavior.py::test_no_boltons_import_surface`

- mapping: `B008`
- API: `featurelifted.__file__, featurelifted.iterutils`
- risk: `filesystem_resource`
- A001 `assert` L72: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B007`
- API: `featurelifted.bucketize, featurelifted.chunked, featurelifted.get_path, featurelifted.iterutils, featurelifted.pairwise, featurelifted.partition, featurelifted.remap, featurelifted.unique, featurelifted.windowed`
- risk: `none`
- A001 `assert` L17: `callable(chunked)`
- A002 `assert` L18: `callable(windowed)`
- A003 `assert` L19: `callable(pairwise)`
- A004 `assert` L20: `callable(unique)`
- A005 `assert` L21: `callable(bucketize)`
- A006 `assert` L22: `callable(remap)`
- A007 `assert` L23: `callable(get_path)`
- A008 `assert` L24: `callable(partition)`
- A009 `assert` L25: `iterutils is not None`
- A010 `assert` L26: `callable(getattr(iterutils, 'backoff'))`
- A011 `assert` L27: `callable(getattr(iterutils, 'chunk_ranges'))`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `boltons`
- source entrypoints: `boltons.iterutils.chunked, boltons.iterutils.windowed, boltons.iterutils.pairwise, boltons.iterutils.unique, boltons.iterutils.bucketize, boltons.iterutils.remap, boltons.iterutils.get_path`
- oracle source files: `boltons/iterutils.py`
- runtime dependencies: `none`
- oracle notes: Oracle is iterutils.py only; curated repo includes sibling boltons modules for copy-all penalty.
