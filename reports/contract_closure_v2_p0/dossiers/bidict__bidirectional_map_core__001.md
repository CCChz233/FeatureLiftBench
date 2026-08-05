# Contract V2 P0: bidict__bidirectional_map_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `11/30`

## Required API

- `featurelifted.bidict` (class) `(arg=(), /, *, on_dup=ON_DUP_DEFAULT, **items) -> bidict`
- `featurelifted.bidict.inverse` (attribute)
- `featurelifted.bidict.__getitem__` (method) `(self, key) -> value`
- `featurelifted.bidict.__setitem__` (method) `(self, key, value) -> None`
- `featurelifted.bidict.keys` (method) `(self) -> KeysView`
- `featurelifted.frozenbidict` (class) `(arg=(), /, **items) -> frozenbidict`
- `featurelifted.frozenbidict.inverse` (attribute)
- `featurelifted.frozenbidict.__getitem__` (method) `(self, key) -> value`
- `featurelifted.frozenbidict.__hash__` (method) `(self) -> int`
- `featurelifted.OrderedBidict` (class) `(arg: 'MapOrItems[KT, VT]' = (), /, **kw: 'VT') -> 'None'`
- `featurelifted.OrderedBidict.keys` (method) `(self) -> 'KeysView[KT]'`
- `featurelifted.OrderedBidict.move_to_end` (method) `(self, key: 'KT', last: 'bool' = True) -> 'None'`
- `featurelifted.ON_DUP_RAISE` (constant)
- `featurelifted.ValueDuplicationError` (exception)
- `featurelifted.KeyAndValueDuplicationError` (exception)
- `featurelifted.inverted` (function) `(arg: 'MapOrItems[KT, VT]') -> 'ItemsIter[VT, KT]'`

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: forward and inverse lookups on bidict and frozenbidict. Required observable cases include bidict forward and inverse lookup; frozenbidict is immutable; frozenbidict hash stable.
- **B002**: The extracted feature must support this observable behavior: inverse view reflects live updates on mutable bidicts. Required observable cases include bidict inverse reflects updates; ordered move to end.
- **B003**: The extracted feature must support this observable behavior: ON_DUP_RAISE duplicate value/key policies with typed errors. Required observable cases include on dup raise value collision; key and value duplication error.
- **B004**: The extracted feature must support this observable behavior: OrderedBidict preserves insertion order and move_to_end. Required observable cases include ordered move to end.
- **B005**: The extracted feature must support this observable behavior: inverted() iterator helper for value-key pairs. Required observable cases include inverted iterator.
- **B006**: The package exposes the required task API paths `featurelifted.bidict`, `featurelifted.bidict.inverse`, `featurelifted.bidict.__getitem__`, `featurelifted.bidict.__setitem__`, `featurelifted.bidict.keys`, `featurelifted.frozenbidict`, `featurelifted.frozenbidict.inverse`, `featurelifted.frozenbidict.__getitem__`, `featurelifted.frozenbidict.__hash__`, `featurelifted.OrderedBidict`, `featurelifted.OrderedBidict.keys`, `featurelifted.OrderedBidict.move_to_end`, and 4 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_api.py::test_bidict_forward_and_inverse_lookup`

- mapping: `B001`
- API: `featurelifted.bidict`
- risk: `none`
- A001 `assert` L8: `mapping['H'] == 'hydrogen'`
- A002 `assert` L9: `mapping.inverse['hydrogen'] == 'H'`

### `public_tests/test_public_api.py::test_bidict_inverse_reflects_updates`

- mapping: `B002`
- API: `featurelifted.bidict`
- risk: `state_mutation`
- A001 `assert` L15: `mapping.inverse[2] == 'b'`
- A002 `assert` L16: `set(mapping.inverse.keys()) == {1, 2}`

### `public_tests/test_public_api.py::test_frozenbidict_is_immutable`

- mapping: `B001`
- API: `featurelifted.frozenbidict`
- risk: `none`
- A001 `assert` L21: `mapping['x'] == 10`
- A002 `assert` L22: `mapping.inverse[10] == 'x'`

### `hidden_tests/test_hidden_behavior.py::test_on_dup_raise_value_collision`

- mapping: `B003`
- API: `featurelifted.ON_DUP_RAISE, featurelifted.ValueDuplicationError, featurelifted.bidict`
- risk: `exception_semantics`
- A001 `raises` L21: `pytest.raises(ValueDuplicationError)`

### `hidden_tests/test_hidden_behavior.py::test_key_and_value_duplication_error`

- mapping: `B003`
- API: `featurelifted.KeyAndValueDuplicationError, featurelifted.ON_DUP_RAISE, featurelifted.bidict`
- risk: `exception_semantics`
- A001 `raises` L27: `pytest.raises(KeyAndValueDuplicationError)`

### `hidden_tests/test_hidden_behavior.py::test_ordered_move_to_end`

- mapping: `B002, B004`
- API: `featurelifted.OrderedBidict`
- risk: `ordering_semantics`
- A001 `assert` L34: `list(ordered.keys()) == ['a', 'b', 'c']`
- A002 `assert` L36: `list(ordered.keys()) == ['a', 'c', 'b']`

### `hidden_tests/test_hidden_behavior.py::test_frozenbidict_hash_stable`

- mapping: `B001`
- API: `featurelifted.frozenbidict`
- risk: `none`
- A001 `assert` L42: `hash(left) == hash(right)`

### `hidden_tests/test_hidden_behavior.py::test_frozenbidict_rejects_mutation`

- mapping: `B001`
- API: `featurelifted.frozenbidict`
- risk: `exception_semantics, state_mutation`
- A001 `raises` L47: `pytest.raises(TypeError)`

### `hidden_tests/test_hidden_behavior.py::test_inverted_iterator`

- mapping: `B005`
- API: `featurelifted.bidict, featurelifted.inverted`
- risk: `none`
- A001 `assert` L53: `list(inverted(mapping)) == [(1, 'a'), (2, 'b')]`

### `hidden_tests/test_hidden_behavior.py::test_no_bidict_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L63: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.KeyAndValueDuplicationError, featurelifted.ON_DUP_RAISE, featurelifted.OrderedBidict, featurelifted.ValueDuplicationError, featurelifted.bidict, featurelifted.frozenbidict, featurelifted.inverted`
- risk: `none`
- A001 `assert` L15: `isinstance(bidict, type)`
- A002 `assert` L16: `bidict is not None`
- A003 `assert` L17: `hasattr(bidict, '__getitem__')`
- A004 `assert` L18: `hasattr(bidict, '__setitem__')`
- A005 `assert` L19: `hasattr(bidict, 'keys')`
- A006 `assert` L20: `isinstance(frozenbidict, type)`
- A007 `assert` L21: `frozenbidict is not None`
- A008 `assert` L22: `hasattr(frozenbidict, '__getitem__')`
- A009 `assert` L23: `hasattr(frozenbidict, '__hash__')`
- A010 `assert` L24: `isinstance(OrderedBidict, type)`
- A011 `assert` L25: `hasattr(OrderedBidict, 'keys')`
- A012 `assert` L26: `hasattr(OrderedBidict, 'move_to_end')`
- A013 `assert` L27: `ON_DUP_RAISE is not None`
- A014 `assert` L28: `issubclass(ValueDuplicationError, BaseException)`
- A015 `assert` L29: `issubclass(KeyAndValueDuplicationError, BaseException)`
- A016 `assert` L30: `callable(inverted)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `bidict`
- source entrypoints: `bidict.bidict, bidict.frozenbidict, bidict.OrderedBidict, bidict.ON_DUP_RAISE, bidict.ValueDuplicationError, bidict.inverted`
- oracle source files: `bidict/__init__.py, bidict/_abc.py, bidict/_base.py, bidict/_bidict.py, bidict/_dup.py, bidict/_exc.py, bidict/_frozen.py, bidict/_iter.py, bidict/_orderedbase.py, bidict/_orderedbidict.py, bidict/_typing.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies the bidict runtime package; excludes upstream tests and docs.
