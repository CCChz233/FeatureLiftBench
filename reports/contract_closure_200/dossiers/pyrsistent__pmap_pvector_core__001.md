# pyrsistent__pmap_pvector_core__001

- release: `external50`
- lift: `Direct`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `8/12`

## Required API

- `featurelifted.pmap` (function) `(initial=None) -> PMap`
- `featurelifted.pvector` (function) `(initial=()) -> PVector`
- `featurelifted.PMap` (class)
- `featurelifted.PMap.set` (method)
- `featurelifted.PMap.get` (method)
- `featurelifted.PVector` (class)
- `featurelifted.PVector.append` (method)
- `featurelifted.PVector.extend` (method)
- `featurelifted.PVector.set` (method)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: pmap/PMap.set/get returns new maps without mutating originals. Required observable cases include pmap set get; pmap immutability.
- **B002**: The extracted feature must support this observable behavior: pvector/PVector.append returns new vectors. Required observable cases include pvector append; factory types.
- **B003**: The extracted feature must support this observable behavior: PVector.set/extend produce new vectors. Required observable cases include pvector set; pvector extend.
- **B004**: Original pmap/pvector instances remain unchanged after updates.
- **B005**: The package exposes pmap/pvector/PMap/PVector with the kinds listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: pyrsistent.

## Tests

### `public_tests/test_public_api.py::test_pmap_set_get`

- mapping: `B001`
- API: `featurelifted.pmap`
- risk: `none`
- A001 `assert` L9: `m2['a'] == 1 and m2.get('b') == 2`
- A002 `assert` L10: `m is not m2`

### `public_tests/test_public_api.py::test_pvector_append`

- mapping: `B002`
- API: `featurelifted.pvector`
- risk: `none`
- A001 `assert` L16: `list(v) == [1, 2] and list(v2) == [1, 2, 3]`
- A002 `assert` L17: `v is not v2`

### `public_tests/test_public_api.py::test_factory_types`

- mapping: `B003`
- API: `featurelifted.PMap, featurelifted.PVector, featurelifted.pmap, featurelifted.pvector`
- risk: `none`
- A001 `assert` L21: `isinstance(pmap(), PMap)`
- A002 `assert` L22: `isinstance(pvector(), PVector)`

### `hidden_tests/test_hidden_behavior.py::test_pmap_immutability`

- mapping: `B001, B004`
- API: `featurelifted.pmap`
- risk: `none`
- A001 `assert` L12: `'y' not in m and m2['y'] == 2`

### `hidden_tests/test_hidden_behavior.py::test_pvector_set`

- mapping: `B002`
- API: `featurelifted.pvector`
- risk: `none`
- A001 `assert` L18: `list(v) == [10, 20, 30] and list(v2) == [10, 99, 30]`

### `hidden_tests/test_hidden_behavior.py::test_pvector_extend`

- mapping: `B003`
- API: `featurelifted.pvector`
- risk: `none`
- A001 `assert` L24: `list(extended) == [1, 2, 3]`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L33: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.PMap, featurelifted.PVector, featurelifted.pmap, featurelifted.pvector`
- risk: `none`
- A001 `assert` L5: `callable(pmap) and callable(pvector)`
- A002 `assert` L6: `PMap is not None and PVector is not None`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `pyrsistent`
- source entrypoints: `none`
- oracle source files: `pyrsistent/_pmap.py, pyrsistent/_pvector.py, pyrsistent/__init__.py`
- runtime dependencies: `none`
- oracle notes: Direct pmap/pvector + PMap.set/get + PVector.append.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
