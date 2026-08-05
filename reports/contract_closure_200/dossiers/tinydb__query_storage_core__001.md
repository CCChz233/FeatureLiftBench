# tinydb__query_storage_core__001

- release: `external50`
- lift: `Composite`
- coupling: `data_model_coupling`
- strict validation: `PASS`
- tests/assertions: `8/31`

## Required API

- `featurelifted.TinyDB` (class)
- `featurelifted.TinyDB.insert` (method) `(self, document: dict) -> int`
- `featurelifted.TinyDB.insert_multiple` (method) `(self, documents: list) -> list`
- `featurelifted.TinyDB.all` (method) `(self) -> list`
- `featurelifted.TinyDB.get` (method) `(self, cond=None, doc_id=None)`
- `featurelifted.TinyDB.search` (method) `(self, cond)`
- `featurelifted.TinyDB.update` (method) `(self, fields, cond=None, doc_ids=None)`
- `featurelifted.TinyDB.remove` (method) `(self, cond=None, doc_ids=None)`
- `featurelifted.TinyDB.truncate` (method) `(self) -> None`
- `featurelifted.TinyDB.close` (method) `(self) -> None`
- `featurelifted.Query` (class)
- `featurelifted.Query.__getattr__` (method)
- `featurelifted.Query.__getitem__` (method)
- `featurelifted.Query.exists` (method)
- `featurelifted.Query.matches` (method)
- `featurelifted.Query.test` (method)
- `featurelifted.JSONStorage` (class)
- `featurelifted.MemoryStorage` (class)

## Public Behaviors

- **B001**: The extracted feature must support this observable behavior: CRUD insert/search/update/remove/truncate. Required observable cases include insert and all; search equality; update and remove.
- **B002**: The extracted feature must support this observable behavior: Query operators == exists matches test and logical and/or. Required observable cases include exists matches test ops; logical and or.
- **B003**: The extracted feature must support this observable behavior: JSONStorage and MemoryStorage backends. Required observable cases include json storage roundtrip.
- **B004**: Default table behavior matches upstream TinyDB for the frozen CRUD paths.
- **B005**: The package exposes the required task API paths `featurelifted.TinyDB`, `featurelifted.Query`, `featurelifted.JSONStorage`, `featurelifted.MemoryStorage` and TinyDB CRUD methods with the kinds and callable signatures listed in this contract.
- **B006**: the submitted package does not import forbidden upstream packages: tinydb.

## Tests

### `public_tests/test_public_api.py::test_insert_and_all`

- mapping: `B001`
- API: `featurelifted.MemoryStorage, featurelifted.TinyDB`
- risk: `none`
- A001 `assert` L9: `isinstance(doc_id, int)`
- A002 `assert` L10: `db.all() == [{'name': 'alice', 'age': 30}]`

### `public_tests/test_public_api.py::test_search_equality`

- mapping: `B002`
- API: `featurelifted.MemoryStorage, featurelifted.Query, featurelifted.TinyDB`
- risk: `none`
- A001 `assert` L18: `db.search(q.name == 'b') == [{'name': 'b', 'age': 2}]`

### `public_tests/test_public_api.py::test_update_and_remove`

- mapping: `B003`
- API: `featurelifted.MemoryStorage, featurelifted.Query, featurelifted.TinyDB`
- risk: `state_mutation`
- A001 `assert` L27: `db.get(q.name == 'x')['age'] == 2`
- A002 `assert` L29: `db.all() == []`

### `hidden_tests/test_hidden_behavior.py::test_exists_matches_test_ops`

- mapping: `B001, B004`
- API: `featurelifted.MemoryStorage, featurelifted.Query, featurelifted.TinyDB`
- risk: `none`
- A001 `assert` L19: `len(db.search(q.tag.exists())) == 2`
- A002 `assert` L20: `db.search(q.tag.matches('^ok$')) == [{'name': 'ann', 'tag': 'ok'}]`
- A003 `assert` L21: `db.search(q.name.test(lambda v: v.startswith('c'))) == [{'name': 'cara', 'tag': 'ok-1'}]`

### `hidden_tests/test_hidden_behavior.py::test_logical_and_or`

- mapping: `B002`
- API: `featurelifted.MemoryStorage, featurelifted.Query, featurelifted.TinyDB`
- risk: `none`
- A001 `assert` L37: `db.search((q.age == 10) & (q.name == 'a')) == [{'name': 'a', 'age': 10}]`
- A002 `assert` L39: `names == {'a', 'b'}`

### `hidden_tests/test_hidden_behavior.py::test_json_storage_roundtrip`

- mapping: `B003`
- API: `featurelifted.JSONStorage, featurelifted.TinyDB`
- risk: `filesystem_resource`
- A001 `assert` L49: `db2.all() == [{'k': 1}]`
- A002 `assert` L51: `db2.all() == []`

### `hidden_tests/test_hidden_behavior.py::test_no_upstream_import_surface`

- mapping: `B006`
- API: `featurelifted.__file__`
- risk: `filesystem_resource`
- A001 `assert` L61: `not pattern.search(path.read_text(encoding='utf-8'))`

### `hidden_tests/test_required_api_surface.py::test_required_api_surface`

- mapping: `B005`
- API: `featurelifted.MemoryStorage, featurelifted.Query, featurelifted.Query.__getattr__, featurelifted.Query.__getitem__, featurelifted.Query.exists, featurelifted.Query.matches, featurelifted.Query.test, featurelifted.TinyDB`
- risk: `none`
- A001 `assert` L5: `hasattr(featurelifted, 'JSONStorage')`
- A002 `assert` L6: `hasattr(featurelifted, 'MemoryStorage')`
- A003 `assert` L7: `hasattr(featurelifted, 'Query')`
- A004 `assert` L8: `hasattr(featurelifted, 'TinyDB')`
- A005 `assert` L10: `callable(instance_0.insert)`
- A006 `assert` L11: `callable(instance_0.insert_multiple)`
- A007 `assert` L12: `callable(instance_0.all)`
- A008 `assert` L13: `callable(instance_0.get)`
- A009 `assert` L14: `callable(instance_0.search)`
- A010 `assert` L15: `callable(instance_0.update)`
- A011 `assert` L16: `callable(instance_0.remove)`
- A012 `assert` L17: `callable(instance_0.truncate)`
- A013 `assert` L18: `callable(instance_0.close)`
- A014 `assert` L19: `callable(featurelifted.Query.__getattr__)`
- A015 `assert` L20: `callable(featurelifted.Query.__getitem__)`
- A016 `assert` L21: `callable(featurelifted.Query.exists)`
- A017 `assert` L22: `callable(featurelifted.Query.matches)`
- A018 `assert` L23: `callable(featurelifted.Query.test)`

## Dependency / Oracle Evidence

- allowed dependencies: `none`
- forbidden imports: `tinydb`
- source entrypoints: `none`
- oracle source files: `tinydb/database.py, tinydb/queries.py, tinydb/storages.py, tinydb/table.py`
- runtime dependencies: `none`
- oracle notes: Composite DB + Query + Storage.
- behavior contract lacks a completed review_status
- behavior contract schema_version missing or unsupported
