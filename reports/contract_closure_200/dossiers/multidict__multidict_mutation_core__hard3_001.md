# multidict__multidict_mutation_core__hard3_001

- release: `frozen_python150`
- lift: `Direct`
- coupling: `unknown`
- strict validation: `PASS`
- tests/assertions: `6/20`

## Required API

- `featurelifted.MultiDict` (class) `(*args, **kwargs) -> 'None'`
- `featurelifted.MultiDict.add` (method) `(self, key: 'str', value: 'object') -> 'None'`
- `featurelifted.MultiDict.popall` (method) `(self, key: 'str') -> 'list[object]'`
- `featurelifted.MultiDict.popone` (method) `(self, key: 'str', default=Ellipsis)`
- `featurelifted.CIMultiDict` (class) `(*args, **kwargs) -> 'None'`
- `featurelifted.CIMultiDict.add` (method) `(self, key: 'str', value: 'object') -> 'None'`
- `featurelifted.CIMultiDict.getall` (method) `(self, key: 'str') -> 'list[object]'`
- `featurelifted.MultiDictProxy` (class) `(base: 'MultiDict') -> 'None'`
- `featurelifted.CIMultiDictProxy` (class) `(base: 'CIMultiDict') -> 'None'`
- `featurelifted.CIMultiDictProxy.add` (method) `(self, key: 'str', value: 'object') -> 'None'`

## Public Behaviors

- **B001**: MultiDict preserves repeated values and insertion order while CIMultiDict applies the same mutations using case-insensitive string keys.
- **B002**: getall and getone retrieve repeated values, while popone removes the most recent matching value and popall removes every matching value.
- **B003**: MultiDictProxy and CIMultiDictProxy reflect subsequent mutations of their underlying mappings without exposing independent copied state.
- **B004**: CIMultiDict folds keys case-insensitively for lookup, replacement, deletion, and repeated-value operations.
- **B005**: The package exposes the required task API paths `featurelifted.MultiDict`, `featurelifted.MultiDict.add`, `featurelifted.MultiDict.popall`, `featurelifted.MultiDict.popone`, `featurelifted.CIMultiDict`, `featurelifted.CIMultiDict.add`, `featurelifted.CIMultiDict.getall`, `featurelifted.MultiDictProxy`, `featurelifted.CIMultiDictProxy`, `featurelifted.CIMultiDictProxy.add` with the kinds and callable signatures listed in this contract.

## Tests

### `public_tests/test_public_contract.py::test_multidict_duplicate_keys_and_getall`

- mapping: `B001, B002`
- API: `featurelifted.MultiDict`
- risk: `none`
- A001 `assert` L9: `md['a'] == 2`
- A002 `assert` L10: `md.getall('a') == [1, 2]`

### `public_tests/test_public_contract.py::test_proxy_reflects_base_mutations`

- mapping: `B001, B003`
- API: `featurelifted.MultiDict, featurelifted.MultiDictProxy`
- risk: `state_mutation`
- A001 `assert` L17: `base['x'] == 9`

### `hidden_tests/test_hidden_contract.py::test_popone_and_popall_semantics`

- mapping: `B002, B003`
- API: `featurelifted.MultiDict`
- risk: `exception_semantics`
- A001 `assert` L11: `md.popone('k') == 2`
- A002 `assert` L12: `md['k'] == 1`
- A003 `assert` L13: `md.popall('k') == [1]`
- A004 `raises` L14: `pytest.raises(KeyError)`

### `hidden_tests/test_hidden_contract.py::test_cimultidict_case_insensitive_lookup_and_equality`

- mapping: `B004`
- API: `featurelifted.CIMultiDict`
- risk: `none`
- A001 `assert` L21: `md['header'] == 'v1'`
- A002 `assert` L23: `md == other`

### `hidden_tests/test_hidden_contract.py::test_cimultidict_proxy_reflects_base`

- mapping: `B001, B004`
- API: `featurelifted.CIMultiDict, featurelifted.CIMultiDictProxy`
- risk: `none`
- A001 `assert` L30: `base.getall('a') == [1]`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.CIMultiDict, featurelifted.CIMultiDictProxy, featurelifted.MultiDict, featurelifted.MultiDictProxy`
- risk: `none`
- A001 `assert` L12: `isinstance(MultiDict, type)`
- A002 `assert` L13: `hasattr(MultiDict, 'add')`
- A003 `assert` L14: `hasattr(MultiDict, 'popall')`
- A004 `assert` L15: `hasattr(MultiDict, 'popone')`
- A005 `assert` L16: `isinstance(CIMultiDict, type)`
- A006 `assert` L17: `hasattr(CIMultiDict, 'add')`
- A007 `assert` L18: `hasattr(CIMultiDict, 'getall')`
- A008 `assert` L19: `isinstance(MultiDictProxy, type)`
- A009 `assert` L20: `isinstance(CIMultiDictProxy, type)`
- A010 `assert` L21: `hasattr(CIMultiDictProxy, 'add')`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `multidict`
- source entrypoints: `multidict.MultiDict, multidict.CIMultiDict, multidict.MultiDictProxy`
- oracle source files: `repo/multidict/__init__.py, repo/multidict/_abc.py, repo/multidict/_compat.py, repo/multidict/_multidict_py.py`
- runtime dependencies: `none`
- oracle notes: Pure-Python multidict subset. C extension and typing-only modules excluded.
