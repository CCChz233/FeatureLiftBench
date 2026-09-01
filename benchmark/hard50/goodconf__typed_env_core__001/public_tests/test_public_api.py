from __future__ import annotations

import json

from featurelifted import Field, GoodConf


class App(GoodConf):
    host: str = Field(default="localhost")
    port: int = Field(default=8000)


def test_env_uppercase_field_names(monkeypatch) -> None:
    monkeypatch.setenv("HOST", "envhost")
    monkeypatch.setenv("PORT", "9000")
    settings = App()
    settings.load()
    assert settings.host == "envhost"
    assert settings.port == 9000


def test_json_file_overlay(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    path = tmp_path / "app.json"
    path.write_text(json.dumps({"host": "filehost", "port": 7000}), encoding="utf-8")
    settings = App()
    settings.load(str(path))
    assert settings.host == "filehost"
    assert settings.port == 7000


def test_generate_json_contains_initial_fields() -> None:
    payload = json.loads(App.generate_json())
    assert payload["host"] == "localhost"
    assert payload["port"] == 8000
