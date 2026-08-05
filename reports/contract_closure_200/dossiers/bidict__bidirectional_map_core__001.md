# bidict__bidirectional_map_core__001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `10/22`

## Required API

- `featurelifted.bidict` (function) `(arg: 'MapOrItems[KT, VT]' = (), /, **kw: 'VT') -> 'None'`
- `featurelifted.frozenbidict` (function) `(arg: 'MapOrItems[KT, VT]' = (), /, **kw: 'VT') -> 'None'`
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
- **B006**: The package exposes the required task API paths `featurelifted.bidict`, `featurelifted.frozenbidict`, `featurelifted.OrderedBidict`, `featurelifted.OrderedBidict.keys`, `featurelifted.OrderedBidict.move_to_end`, `featurelifted.ON_DUP_RAISE`, `featurelifted.ValueDuplicationError`, `featurelifted.KeyAndValueDuplicationError`, `featurelifted.inverted` with the kinds and callable signatures listed in this contract.

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

### `hidden_tests/test_hidden_behavior.py::test_inverted_iterator`

- mapping: `B005`
- API: `featurelifted.bidict, featurelifted.inverted`
- risk: `none`
- A001 `assert` L47: `list(inverted(mapping)) == [(1, 'a'), (2, 'b')]`

### `hidden_tests/test_hidden_behavior.py::test_no_bidict_import_surface`

- mapping: `B007`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L57: `not import_pattern.search(text)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B006`
- API: `featurelifted.KeyAndValueDuplicationError, featurelifted.ON_DUP_RAISE, featurelifted.OrderedBidict, featurelifted.ValueDuplicationError, featurelifted.bidict, featurelifted.frozenbidict, featurelifted.inverted`
- risk: `none`
- A001 `assert` L15: `callable(bidict)`
- A002 `assert` L16: `callable(frozenbidict)`
- A003 `assert` L17: `isinstance(OrderedBidict, type)`
- A004 `assert` L18: `hasattr(OrderedBidict, 'keys')`
- A005 `assert` L19: `hasattr(OrderedBidict, 'move_to_end')`
- A006 `assert` L20: `ON_DUP_RAISE is not None`
- A007 `assert` L21: `issubclass(ValueDuplicationError, BaseException)`
- A008 `assert` L22: `issubclass(KeyAndValueDuplicationError, BaseException)`
- A009 `assert` L23: `callable(inverted)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `bidict`
- source entrypoints: `bidict.bidict, bidict.frozenbidict, bidict.OrderedBidict, bidict.ON_DUP_RAISE, bidict.ValueDuplicationError, bidict.inverted`
- oracle source files: `bidict/__init__.py, bidict/_abc.py, bidict/_base.py, bidict/_bidict.py, bidict/_dup.py, bidict/_exc.py, bidict/_frozen.py, bidict/_iter.py, bidict/_orderedbase.py, bidict/_orderedbidict.py, bidict/_typing.py`
- runtime dependencies: `none`
- oracle notes: Oracle copies the bidict runtime package; excludes upstream tests and docs.
