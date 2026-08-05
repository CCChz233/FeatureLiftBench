# intervaltree__interval_tree_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `12/30`

## Required API

- `featurelifted.Interval` (class) `(begin, end, data=None)`
- `featurelifted.IntervalTree` (class) `(intervals=None)`
- `featurelifted.IntervalTree.at` (method) `(self, p)`
- `featurelifted.IntervalTree.chop` (method) `(self, begin, end, datafunc=None)`
- `featurelifted.IntervalTree.envelop` (method) `(self, begin, end=None)`
- `featurelifted.IntervalTree.overlap` (method) `(self, begin, end=None)`
- `featurelifted.IntervalTree.remove_envelop` (method) `(self, begin, end)`
- `featurelifted.IntervalTree.remove_overlap` (method) `(self, begin, end=None)`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: add/remove/discard intervals with set semantics and distinct data fields. Required observable cases include add and point query; remove interval; remove overlap multiple; distinct data same range; remove envelop.
- **B002**: The extracted feature must support this observable behavior: point and range overlap queries via at/overlap/overlaps. Required observable cases include add and point query; overlap range; complex point query.
- **B003**: The extracted feature must support this observable behavior: remove_overlap and remove_envelop bulk deletion. Required observable cases include remove interval; remove overlap multiple; envelop vs overlap; remove envelop.
- **B004**: The extracted feature must support this observable behavior: chop trims overhanging intervals and optional datafunc relabeling. Required observable cases include chop splits intervals; chop datafunc.
- **B005**: The extracted feature must support this observable behavior: self-balancing tree queries through Node search helpers. Required observable cases include remove overlap multiple.
- **B006**: The package exposes the required task API paths `featurelifted.Interval`, `featurelifted.IntervalTree`, `featurelifted.IntervalTree.at`, `featurelifted.IntervalTree.chop`, `featurelifted.IntervalTree.envelop`, `featurelifted.IntervalTree.overlap`, `featurelifted.IntervalTree.remove_envelop`, `featurelifted.IntervalTree.remove_overlap` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_add_and_point_query`

- mapping: `B001, B002`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L10: `len(tree) == 2`
- A002 `assert` L11: `tree[5] == {Interval(0, 10, 'base')}`
- A003 `assert` L12: `tree.overlaps(15)`

### `public_tests/test_public_api.py::test_remove_interval`

- mapping: `B001, B003`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L18: `Interval(-10, 10) not in tree`
- A002 `assert` L19: `tree.overlaps(15)`

### `public_tests/test_public_api.py::test_overlap_range`

- mapping: `B002`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L25: `Interval(4, 7) in hits`
- A002 `assert` L26: `tree.overlaps(4, 6)`

### `hidden_tests/test_hidden_behavior.py::test_chop_splits_intervals`

- mapping: `B004`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L14: `len(tree) == 2`
- A002 `assert` L15: `sorted(tree) == [Interval(0, 3), Interval(7, 10)]`

### `hidden_tests/test_hidden_behavior.py::test_chop_datafunc`

- mapping: `B004`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L25: `sorted(tree) == [Interval(0, 3, 'oldlimit: 10, islower: True'), Interval(7, 10, 'oldlimit: 0, islower: False')]`

### `hidden_tests/test_hidden_behavior.py::test_remove_overlap_multiple`

- mapping: `B001, B003, B005`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L36: `set(tree) == {Interval(0.5, 1.7)}`

### `hidden_tests/test_hidden_behavior.py::test_envelop_vs_overlap`

- mapping: `B003`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L41: `tree.envelop(6, 10) == {Interval(6, 10)}`
- A002 `assert` L43: `Interval(4, 7) in overlap_hits`
- A003 `assert` L44: `Interval(5, 9) in overlap_hits`
- A004 `assert` L45: `Interval(6, 10) in overlap_hits`

### `hidden_tests/test_hidden_behavior.py::test_distinct_data_same_range`

- mapping: `B001`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L52: `len(tree) == 2`
- A002 `assert` L53: `Interval(-10, 10) in tree`
- A003 `assert` L54: `Interval(-10, 10, 'tag') in tree`

### `hidden_tests/test_hidden_behavior.py::test_remove_envelop`

- mapping: `B001, B003`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L62: `set(tree) == {Interval(-1.1, 1.1), Interval(0.5, 1.7)}`

### `hidden_tests/test_hidden_behavior.py::test_complex_point_query`

- mapping: `B002`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L70: `at_nine == {Interval(6, 10), Interval(8, 15)}`
- A002 `assert` L71: `tree[9] == at_nine`

### `hidden_tests/test_hidden_behavior.py::test_no_intervaltree_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L83: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.Interval, featurelifted.IntervalTree`
- risk: `none`
- A001 `assert` L10: `isinstance(Interval, type)`
- A002 `assert` L11: `isinstance(IntervalTree, type)`
- A003 `assert` L12: `hasattr(IntervalTree, 'at')`
- A004 `assert` L13: `hasattr(IntervalTree, 'chop')`
- A005 `assert` L14: `hasattr(IntervalTree, 'envelop')`
- A006 `assert` L15: `hasattr(IntervalTree, 'overlap')`
- A007 `assert` L16: `hasattr(IntervalTree, 'remove_envelop')`
- A008 `assert` L17: `hasattr(IntervalTree, 'remove_overlap')`

## Dependency / Oracle Evidence

- allowed dependencies: `sortedcontainers`
- forbidden imports: `intervaltree`
- source entrypoints: `intervaltree.Interval, intervaltree.IntervalTree, intervaltree.IntervalTree.add, intervaltree.IntervalTree.remove, intervaltree.IntervalTree.discard, intervaltree.IntervalTree.remove_overlap, intervaltree.IntervalTree.remove_envelop, intervaltree.IntervalTree.chop, intervaltree.IntervalTree.overlap, intervaltree.IntervalTree.overlaps, intervaltree.IntervalTree.at, intervaltree.IntervalTree.envelop, intervaltree.node.Node`
- oracle source files: `intervaltree/interval.py, intervaltree/intervaltree.py, intervaltree/node.py`
- runtime dependencies: `sortedcontainers`
- oracle notes: Oracle copies the three runtime modules; SortedDict comes from allowed sortedcontainers dependency.
