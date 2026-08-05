# sortedcontainers__sorted_list_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `11/31`

## Required API

- `featurelifted.SortedList` (class) `(iterable=None, key=None)`
- `featurelifted.SortedList._check` (method) `(self)`
- `featurelifted.SortedList._lists` (attribute)
- `featurelifted.SortedList._maxes` (attribute)
- `featurelifted.SortedList._reset` (method) `(self, load)`
- `featurelifted.SortedList.add` (method) `(self, value)`
- `featurelifted.SortedList.bisect` (method) `(self, value)`
- `featurelifted.SortedList.bisect_left` (method) `(self, value)`
- `featurelifted.SortedList.bisect_right` (method) `(self, value)`
- `featurelifted.SortedList.index` (method) `(self, value, start=None, stop=None)`
- `featurelifted.SortedList.irange` (method) `(self, minimum=None, maximum=None, inclusive=(True, True), reverse=False)`
- `featurelifted.SortedList.islice` (method) `(self, start=None, stop=None, reverse=False)`
- `featurelifted.SortedList.update` (method) `(self, iterable)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: maintain sorted order with add/update and duplicate values. Required observable cases include add and iteration; no sortedcontainers import surface.
- **B002**: The extracted feature must support this observable behavior: bisect_left/bisect_right and count/index on duplicate-heavy lists. Required observable cases include bisect and count; discard and remove; bisect with small load; index duplicate window.
- **B003**: The extracted feature must support this observable behavior: positional indexing and slice reads with small load factors. Required observable cases include bisect with small load.
- **B004**: The extracted feature must support this observable behavior: irange/islice inclusive bounds and reverse iteration. Required observable cases include add and iteration; irange inclusive bounds; islice reverse.
- **B005**: The extracted feature must support this observable behavior: sublist merge/delete invariants validated via _check after _reset. Required observable cases include delete random invariants; check invariants.
- **B006**: The package exposes the required task API paths `featurelifted.SortedList`, `featurelifted.SortedList._check`, `featurelifted.SortedList._lists`, `featurelifted.SortedList._maxes`, `featurelifted.SortedList._reset`, `featurelifted.SortedList.add`, `featurelifted.SortedList.bisect`, `featurelifted.SortedList.bisect_left`, `featurelifted.SortedList.bisect_right`, `featurelifted.SortedList.index`, `featurelifted.SortedList.irange`, `featurelifted.SortedList.islice`, and 1 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_add_and_iteration`

- mapping: `B001, B004`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L9: `list(slt) == [1, 2, 3]`

### `public_tests/test_public_api.py::test_bisect_and_count`

- mapping: `B002`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L14: `slt.bisect_left(2) == 1`
- A002 `assert` L15: `slt.bisect_right(2) == 3`
- A003 `assert` L16: `slt.count(2) == 2`

### `public_tests/test_public_api.py::test_discard_and_remove`

- mapping: `B002`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L22: `list(slt) == [1, 2, 3]`
- A002 `assert` L24: `list(slt) == [1, 3]`

### `hidden_tests/test_hidden_behavior.py::test_hidden_bisect_with_small_load`

- mapping: `B002, B003`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L15: `slt.bisect_left(50) == 100`
- A002 `assert` L16: `slt.bisect_right(10) == 22`
- A003 `assert` L17: `slt.bisect(200) == 200`

### `hidden_tests/test_hidden_behavior.py::test_hidden_irange_inclusive_bounds`

- mapping: `B004`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L23: `list(slt.irange(10, 20, (True, False))) == list(range(10, 20))`
- A002 `assert` L24: `list(slt.irange(10, 20, (False, True))) == list(range(11, 21))`
- A003 `assert` L25: `list(slt.irange(10, 20, (False, False))) == list(range(11, 20))`

### `hidden_tests/test_hidden_behavior.py::test_hidden_islice_reverse`

- mapping: `B004`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L34: `list(slt.islice(start, stop, reverse=True)) == values[start:stop][::-1]`

### `hidden_tests/test_hidden_behavior.py::test_hidden_delete_random_invariants`

- mapping: `B005`
- API: `featurelifted.SortedList`
- risk: `implicit_no_exception_assertion, time_or_randomness`
- assertion: implicit successful execution

### `hidden_tests/test_hidden_behavior.py::test_hidden_index_duplicate_window`

- mapping: `B002`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L53: `slt.index(0, -1000) == 0`
- A002 `assert` L52: `slt.index(0, start, stop + 1) == start`

### `hidden_tests/test_hidden_behavior.py::test_hidden_check_invariants`

- mapping: `B005`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L62: `len(slt._lists) > 1`
- A002 `assert` L63: `slt._maxes == [sub[-1] for sub in slt._lists]`

### `hidden_tests/test_hidden_behavior.py::test_no_sortedcontainers_import_surface`

- mapping: `B001, B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource, ordering_semantics`
- A001 `assert` L76: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.SortedList`
- risk: `none`
- A001 `assert` L9: `isinstance(SortedList, type)`
- A002 `assert` L10: `hasattr(SortedList, '_check')`
- A003 `assert` L11: `SortedList is not None`
- A004 `assert` L12: `SortedList is not None`
- A005 `assert` L13: `hasattr(SortedList, '_reset')`
- A006 `assert` L14: `hasattr(SortedList, 'add')`
- A007 `assert` L15: `hasattr(SortedList, 'bisect')`
- A008 `assert` L16: `hasattr(SortedList, 'bisect_left')`
- A009 `assert` L17: `hasattr(SortedList, 'bisect_right')`
- A010 `assert` L18: `hasattr(SortedList, 'index')`
- A011 `assert` L19: `hasattr(SortedList, 'irange')`
- A012 `assert` L20: `hasattr(SortedList, 'islice')`
- A013 `assert` L21: `hasattr(SortedList, 'update')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `sortedcontainers`
- source entrypoints: `sortedcontainers.SortedList, sortedcontainers.SortedList.add, sortedcontainers.SortedList.discard, sortedcontainers.SortedList.remove, sortedcontainers.SortedList.bisect_left, sortedcontainers.SortedList.bisect_right, sortedcontainers.SortedList.irange, sortedcontainers.SortedList.islice, sortedcontainers.SortedList._check, sortedcontainers.SortedList._reset`
- oracle source files: `sortedcontainers/sortedlist.py`
- runtime dependencies: `none`
- oracle notes: Oracle splits sortedlist.py into index/delete/invariant mixins plus SortedList core; excludes SortedKeyList, SortedDict, and SortedSet. Copy-all baseline includes the full sortedcontainers package.
