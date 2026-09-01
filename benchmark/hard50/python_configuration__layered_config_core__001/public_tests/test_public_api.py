from __future__ import annotations

from featurelifted import ConfigurationSet, config_from_dict, config_from_env, config_from_path


def test_nested_dict_item_and_attribute_access() -> None:
    cfg = config_from_dict({"db": {"host": "h1", "port": 5432}, "name": "app"})
    assert cfg["name"] == "app"
    assert cfg["db"]["host"] == "h1"
    assert cfg.db.host == "h1"
    assert cfg.db.port == 5432


def test_first_layer_wins_on_overlap() -> None:
    first = config_from_dict({"k": "first", "only_a": 1})
    second = config_from_dict({"k": "second", "only_b": 2})
    merged = ConfigurationSet(first, second)
    assert merged["k"] == "first"
    assert merged["only_a"] == 1
    assert merged["only_b"] == 2


def test_env_prefix_and_separator(monkeypatch) -> None:
    monkeypatch.setenv("FLBAPP__HOST", "envhost")
    monkeypatch.setenv("FLBAPP__DB__PORT", "9")
    monkeypatch.setenv("OTHER__HOST", "ignored")
    cfg = config_from_env("FLBAPP")
    assert cfg["HOST"] == "envhost"
    assert cfg["DB.PORT"] == "9"


def test_path_directory_file_contents(tmp_path) -> None:
    nested = tmp_path / "db"
    nested.mkdir()
    (nested / "host").write_text("localhost", encoding="utf-8")
    cfg = config_from_path(str(tmp_path))
    assert cfg["host"] == "localhost"
