# Design card: tinydb__query_storage_core__001

**status:** `validated_staging`  
**wave:** W3  
**package:** `tinydb`  
**repository_url:** https://github.com/msiemens/tinydb  
**planned_lift_type:** Composite  
**final_lift_type:** Composite  
**reclassification_reason:** None  
**feature_family:** algorithm_data_structure  
**entanglement:** data_model_coupling  
**feature_one_liner:** TinyDB + Query + Storage middleware  
**lift_review_flag:** none  
**skim_status:** `pass` (2026-07-31)

> Filled for design_card phase. `feasibility.commit` still unresolved until pin.  
> Spec authority: `docs/TASK_DESIGN_RULES.md`. Workflow: `docs/archive/plans/PLAN_EXTERNAL50_EXPANSION.md`.

## target_api

```yaml
module: featurelifted
signatures:
  - "featurelifted.TinyDB(storage: Storage | str | None = None) -> TinyDB"
  - "featurelifted.TinyDB.insert(document: dict) -> int"
  - "featurelifted.TinyDB.insert_multiple(documents: list[dict]) -> list[int]"
  - "featurelifted.TinyDB.all() -> list[dict]"
  - "featurelifted.TinyDB.get(cond: Query | None = None, doc_id: int | None = None) -> dict | None"
  - "featurelifted.TinyDB.search(cond: Query) -> list[dict]"
  - "featurelifted.TinyDB.update(fields, cond: Query | None = None, doc_ids: list[int] | None = None) -> list[int]"
  - "featurelifted.TinyDB.remove(cond: Query | None = None, doc_ids: list[int] | None = None) -> list[int]"
  - "featurelifted.TinyDB.truncate() -> None"
  - "featurelifted.TinyDB.close() -> None"
  - "featurelifted.Query() -> Query"
  - "featurelifted.JSONStorage(path: str)"
  - "featurelifted.MemoryStorage()"
query_operators_subset:
  - "field equality: Query().field == value"
  - "Query().field.exists()"
  - "Query().field.matches(regex: str)"
  - "Query().field.test(func)"
  - "logical and/or via & and | on Query objects"
returns:
  - "insert returns doc id (int); insert_multiple returns list[int]"
  - "search/all return list[dict]; get returns dict|None"
  - "update/remove return list of affected doc ids"
exceptions:
  - "ValueError/RuntimeError on closed DB ops as upstream"
defaults:
  - "default table name '_default'"
  - "TinyDB() with no path uses MemoryStorage when constructed with MemoryStorage explicitly in tests"
state_effects:
  - "mutates storage; MemoryStorage in-memory only; JSONStorage persists to path"
```

## upstream_mapping

```yaml
primary_symbols:
  - "tinydb.TinyDB"
  - "tinydb.queries.Query"
supporting_components:
  - "tinydb.storages.JSONStorage"
  - "tinydb.storages.MemoryStorage"
  - "tinydb.table.Table"
semantic_delta:
  - "Target API requires DB + Query + Storage together as one contract"
  - "Query operator subset frozen above; no other Query methods required"
```

## oracle_basis

```yaml
basis: upstream
notes: |
  Composite of DB, query DSL, and storage backends.
```

## scope

```yaml
included:
  - "CRUD paths: insert, insert_multiple, all, get, search, update, remove, truncate, close"
  - "Query operators: ==, exists, matches, test, & , |"
  - "JSONStorage and MemoryStorage backends"
excluded:
  - "middleware caching"
  - "SQL storage"
  - "concurrent multi-process locking guarantees"
  - "Query operators beyond the frozen subset (e.g. one_of, search, frag unless listed)"
```

## feasibility

```yaml
commit: "10644a0e07ad180c5b756aba272ee6b0dbd12df8"  # tag v4.8.2
license: "MIT"
python_versions:
  - "3.10"
  - "3.11"
  - "3.12"
native_or_heavy_dependencies: "none"
offline_resources: "MemoryStorage or temp JSON file"
```

## acceptance

```yaml
closure_review: pass
reference_pass: pass
isolation_pass: pass
no_original_import: pass
overlap_check: pass
```

## agent_notes

- Staging path: `benchmark/staging/tinydb__query_storage_core__001/`
- Skim passed; Query subset frozen; pin commit before materialize.
- Do not promote to `benchmark/tasks/` in pilot wave.
