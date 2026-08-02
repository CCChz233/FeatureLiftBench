from __future__ import annotations

from featurelifted import MemoryStorage, Query, TinyDB


def test_insert_and_all() -> None:
    db = TinyDB(storage=MemoryStorage)
    doc_id = db.insert({"name": "alice", "age": 30})
    assert isinstance(doc_id, int)
    assert db.all() == [{"name": "alice", "age": 30}]
    db.close()


def test_search_equality() -> None:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{"name": "a", "age": 1}, {"name": "b", "age": 2}])
    q = Query()
    assert db.search(q.name == "b") == [{"name": "b", "age": 2}]
    db.close()


def test_update_and_remove() -> None:
    db = TinyDB(storage=MemoryStorage)
    db.insert({"name": "x", "age": 1})
    q = Query()
    db.update({"age": 2}, q.name == "x")
    assert db.get(q.name == "x")["age"] == 2
    db.remove(q.name == "x")
    assert db.all() == []
    db.close()
