# Contract V2 P0: multidict__multidict_mutation_core__hard3_001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/32`

## Required API

- `featurelifted.MultiDict` (class) `(*args, **kwargs) -> 'None'`
- `featurelifted.MultiDict.add` (method) `(self, key: 'str', value: 'object') -> 'None'`
- `featurelifted.MultiDict.popall` (method) `(self, key: 'str') -> 'list[object]'`
- `featurelifted.MultiDict.popone` (method) `(self, key: 'str', default=Ellipsis)`
- `featurelifted.MultiDict.getall` (method)
- `featurelifted.MultiDict.__getitem__` (method) `(self, key: str) -> object`
- `featurelifted.MultiDict.__setitem__` (method) `(self, key: str, value: object) -> None`
- `featurelifted.MultiDict.__eq__` (method) `(self, other: object) -> bool`
- `featurelifted.CIMultiDict` (class) `(*args, **kwargs) -> 'None'`
- `featurelifted.CIMultiDict.add` (method) `(self, key: 'str', value: 'object') -> 'None'`
- `featurelifted.CIMultiDict.getall` (method) `(self, key: 'str') -> 'list[object]'`
- `featurelifted.CIMultiDict.__getitem__` (method) `(self, key: str) -> object`
- `featurelifted.CIMultiDict.__setitem__` (method) `(self, key: str, value: object) -> None`
- `featurelifted.CIMultiDict.__eq__` (method) `(self, other: object) -> bool`
- `featurelifted.MultiDictProxy` (class) `(base: 'MultiDict') -> 'None'`
- `featurelifted.MultiDictProxy.__getitem__` (method) `(self, key: str) -> object`
- `featurelifted.MultiDictProxy.getall` (method) `(self, key: str) -> list[object]`
- `featurelifted.CIMultiDictProxy` (class) `(base: 'CIMultiDict') -> 'None'`
- `featurelifted.CIMultiDictProxy.__getitem__` (method) `(self, key: str) -> object`
- `featurelifted.CIMultiDictProxy.getall` (method) `(self, key: str) -> list[object]`

## Public Behaviors

- **B001**: MultiDict preserves repeated values and insertion order while CIMultiDict applies the same mutations using case-insensitive string keys.
- **B002**: getall and getone retrieve repeated values, while popone removes the most recent matching value and popall removes every matching value.
- **B003**: MultiDictProxy and CIMultiDictProxy are read-only live views: mutations applied to their base mappings are reflected immediately, while assignment, deletion, and add through a proxy are rejected.
- **B004**: CIMultiDict folds keys case-insensitively for lookup, replacement, deletion, and repeated-value operations.
- **B005**: The package exposes the required task API paths `featurelifted.MultiDict`, `featurelifted.MultiDict.add`, `featurelifted.MultiDict.popall`, `featurelifted.MultiDict.popone`, `featurelifted.MultiDict.getall`, `featurelifted.MultiDict.__getitem__`, `featurelifted.MultiDict.__setitem__`, `featurelifted.MultiDict.__eq__`, `featurelifted.CIMultiDict`, `featurelifted.CIMultiDict.add`, `featurelifted.CIMultiDict.getall`, `featurelifted.CIMultiDict.__getitem__`, and 8 listed members with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_multidict_duplicate_keys_and_getall`

- mapping: `B001, B002`
- API: `featurelifted.MultiDict`
- risk: `none`
- A001 `assert` L10: `md['a'] == 2`
- A002 `assert` L11: `md.getall('a') == [1, 2]`

### `public_tests/test_public_contract.py::test_proxy_reflects_base_mutations`

- mapping: `B001, B003`
- API: `featurelifted.MultiDict, featurelifted.MultiDictProxy`
- risk: `exception_semantics, state_mutation`
- A001 `assert` L18: `proxy['x'] == 9`
- A002 `raises` L19: `pytest.raises(TypeError)`

### `hidden_tests/test_hidden_contract.py::test_popone_and_popall_semantics`

- mapping: `B001, B002`
- API: `featurelifted.MultiDict`
- risk: `exception_semantics`
- A001 `assert` L10: `md.popone('k') == 2`
- A002 `assert` L11: `md['k'] == 1`
- A003 `assert` L12: `md.popall('k') == [1]`
- A004 `raises` L13: `pytest.raises(KeyError)`

### `hidden_tests/test_hidden_contract.py::test_cimultidict_case_insensitive_lookup_and_equality`

- mapping: `B004`
- API: `featurelifted.CIMultiDict`
- risk: `none`
- A001 `assert` L20: `md['header'] == 'v1'`
- A002 `assert` L22: `md == other`

### `hidden_tests/test_hidden_contract.py::test_cimultidict_proxy_reflects_base`

- mapping: `B003, B004`
- API: `featurelifted.CIMultiDict, featurelifted.CIMultiDictProxy`
- risk: `exception_semantics`
- A001 `assert` L29: `proxy.getall('a') == [1]`
- A002 `raises` L30: `pytest.raises(TypeError)`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.CIMultiDict, featurelifted.CIMultiDictProxy, featurelifted.MultiDict, featurelifted.MultiDictProxy`
- risk: `none`
- A001 `assert` L12: `isinstance(MultiDict, type)`
- A002 `assert` L13: `hasattr(MultiDict, 'add')`
- A003 `assert` L14: `hasattr(MultiDict, 'popall')`
- A004 `assert` L15: `hasattr(MultiDict, 'popone')`
- A005 `assert` L16: `hasattr(MultiDict, 'getall')`
- A006 `assert` L17: `hasattr(MultiDict, '__getitem__')`
- A007 `assert` L18: `hasattr(MultiDict, '__setitem__')`
- A008 `assert` L19: `hasattr(MultiDict, '__eq__')`
- A009 `assert` L20: `isinstance(CIMultiDict, type)`
- A010 `assert` L21: `hasattr(CIMultiDict, 'add')`
- A011 `assert` L22: `hasattr(CIMultiDict, 'getall')`
- A012 `assert` L23: `hasattr(CIMultiDict, '__getitem__')`
- A013 `assert` L24: `hasattr(CIMultiDict, '__setitem__')`
- A014 `assert` L25: `hasattr(CIMultiDict, '__eq__')`
- A015 `assert` L26: `isinstance(MultiDictProxy, type)`
- A016 `assert` L27: `hasattr(MultiDictProxy, '__getitem__')`
- A017 `assert` L28: `hasattr(MultiDictProxy, 'getall')`
- A018 `assert` L29: `isinstance(CIMultiDictProxy, type)`
- A019 `assert` L30: `hasattr(CIMultiDictProxy, '__getitem__')`
- A020 `assert` L31: `hasattr(CIMultiDictProxy, 'getall')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `multidict`
- source entrypoints: `multidict.MultiDict, multidict.CIMultiDict, multidict.MultiDictProxy`
- oracle source files: `repo/multidict/__init__.py, repo/multidict/_abc.py, repo/multidict/_compat.py, repo/multidict/_multidict_py.py`
- runtime dependencies: `none`
- oracle notes: Pure-Python multidict subset with upstream-compatible read-only live proxy views. C extension and typing-only modules are excluded.
