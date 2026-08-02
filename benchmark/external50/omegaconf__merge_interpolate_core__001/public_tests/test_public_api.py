from __future__ import annotations

from featurelifted import OmegaConf


def test_create_merge_resolve() -> None:
    a = OmegaConf.create({"x": 1, "y": "${x}"})
    b = OmegaConf.create({"z": 2})
    m = OmegaConf.merge(a, b)
    assert OmegaConf.to_container(m, resolve=True) == {"x": 1, "y": 1, "z": 2}


def test_select() -> None:
    cfg = OmegaConf.create({"a": {"b": 3}})
    assert OmegaConf.select(cfg, "a.b") == 3
    assert OmegaConf.select(cfg, "a.c", default=9) == 9


def test_is_helpers() -> None:
    cfg = OmegaConf.create({"m": "???", "n": None, "o": 1})
    assert OmegaConf.is_missing(cfg, "m")
    assert OmegaConf.select(cfg, "n") is None
    assert OmegaConf.is_config(cfg)
