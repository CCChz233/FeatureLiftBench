# FeatureLift Task: TinyDB query and storage

Extract a task-scoped subset of `tinydb` into a standalone `featurelifted` package.

The submitted implementation must not import the upstream package or read from `repo/` at runtime, must not use the network, and must not depend on external services. Use only the standard library unless the task lockfile allows otherwise.

## Target API

```python
from featurelifted import (
    JSONStorage,
    MemoryStorage,
    Query,
    TinyDB,
)
```

## Required API Details

- `TinyDB` class must be importable
  - `TinyDB.insert(self, document: dict) -> int`
  - `TinyDB.insert_multiple(self, documents: list) -> list`
  - `TinyDB.all(self) -> list`
  - `TinyDB.get(self, cond=None, doc_id=None)`
  - `TinyDB.search(self, cond)`
  - `TinyDB.update(self, fields, cond=None, doc_ids=None)`
  - `TinyDB.remove(self, cond=None, doc_ids=None)`
  - `TinyDB.truncate(self) -> None`
  - `TinyDB.close(self) -> None`
- `Query` class must be importable
  - `Query.__getattr__(self, name)`
  - `Query.__getitem__(self, item)`
  - `Query.exists(self)`
  - `Query.matches(self, regex, flags=0)`
  - `Query.test(self, func, *args)`
- `JSONStorage` class must be importable
- `MemoryStorage` class must be importable

## Required Behavior

- TinyDB insert and insert_multiple persist dictionary documents, all returns them, update changes matching documents, get retrieves a match, remove deletes matches, and truncate empties the default table.
- Query field paths support equality, exists(), matches(), and test() predicates, and predicate expressions compose with & and | to filter TinyDB.search results.
- MemoryStorage retains documents for an in-memory database lifetime, while JSONStorage persists inserted documents across close and reopen at the same filesystem path.
- Default table behavior matches upstream TinyDB for the frozen CRUD paths.
- The package exposes the required task API paths `featurelifted.TinyDB`, `featurelifted.Query`, `featurelifted.JSONStorage`, `featurelifted.MemoryStorage` and TinyDB CRUD methods with the kinds and callable signatures listed in this contract.
- the submitted package does not import forbidden upstream packages: tinydb.

## Constraints

- Forbidden imports: `tinydb`.
- Do not implement middleware caching.
- Do not implement SQL storage.
- Do not implement multi-process locking guarantees.
- Do not implement original tinydb import at runtime.

<!-- featureliftbench:behavior-clauses:start -->
## Public Behavior Contract

The stable clause IDs below define the public behavior contract. Hidden tests may exercise these clauses but do not introduce additional requirements.

- **B001** — TinyDB insert and insert_multiple persist dictionary documents, all returns them, update changes matching documents, get retrieves a match, remove deletes matches, and truncate empties the default table.
- **B002** — Query field paths support equality, exists(), matches(), and test() predicates, and predicate expressions compose with & and | to filter TinyDB.search results.
- **B003** — MemoryStorage retains documents for an in-memory database lifetime, while JSONStorage persists inserted documents across close and reopen at the same filesystem path.
- **B004** — Default table behavior matches upstream TinyDB for the frozen CRUD paths.
- **B005** — The package exposes the required task API paths `featurelifted.TinyDB`, `featurelifted.Query`, `featurelifted.JSONStorage`, `featurelifted.MemoryStorage` and TinyDB CRUD methods with the kinds and callable signatures listed in this contract.
- **B006** — the submitted package does not import forbidden upstream packages: tinydb.
<!-- featureliftbench:behavior-clauses:end -->
