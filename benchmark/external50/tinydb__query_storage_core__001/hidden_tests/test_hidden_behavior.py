from __future__ import annotations

import re
from pathlib import Path

from featurelifted import JSONStorage, MemoryStorage, Query, TinyDB


def test_exists_matches_test_ops() -> None:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(
        [
            {"name": "ann", "tag": "ok"},
            {"name": "bob"},
            {"name": "cara", "tag": "ok-1"},
        ]
    )
    q = Query()
    assert len(db.search(q.tag.exists())) == 2
    assert db.search(q.tag.matches(r"^ok$")) == [{"name": "ann", "tag": "ok"}]
    assert db.search(q.name.test(lambda v: v.startswith("c"))) == [
        {"name": "cara", "tag": "ok-1"}
    ]
    db.close()


def test_logical_and_or() -> None:
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(
        [
            {"name": "a", "age": 10},
            {"name": "b", "age": 20},
            {"name": "c", "age": 10},
        ]
    )
    q = Query()
    assert db.search((q.age == 10) & (q.name == "a")) == [{"name": "a", "age": 10}]
    names = {d["name"] for d in db.search((q.name == "a") | (q.name == "b"))}
    assert names == {"a", "b"}
    db.close()


def test_json_storage_roundtrip(tmp_path) -> None:
    path = tmp_path / "db.json"
    db = TinyDB(path, storage=JSONStorage)
    db.insert({"k": 1})
    db.close()
    db2 = TinyDB(path, storage=JSONStorage)
    assert db2.all() == [{"k": 1}]
    db2.truncate()
    assert db2.all() == []
    db2.close()


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from tinydb|import tinydb)\b", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
