from __future__ import annotations

import re
from pathlib import Path

import pytest
from featurelifted import OmegaConf
from featurelifted.errors import ConfigKeyError, InterpolationResolutionError


def test_resolve_inplace() -> None:
    cfg = OmegaConf.create({"a": 1, "b": "${a}"})
    OmegaConf.resolve(cfg)
    assert cfg.b == 1


def test_interpolation_error() -> None:
    cfg = OmegaConf.create({"b": "${missing}"})
    with pytest.raises(InterpolationResolutionError):
        OmegaConf.to_container(cfg, resolve=True)


def test_struct_mode_key_error() -> None:
    cfg = OmegaConf.create({"a": 1})
    OmegaConf.set_struct(cfg, True)
    with pytest.raises((ConfigKeyError, KeyError, Exception)):
        cfg.missing = 2  # type: ignore[attr-defined]


def test_list_config_merge() -> None:
    a = OmegaConf.create({"items": [1, 2]})
    b = OmegaConf.create({"items": [3]})
    m = OmegaConf.merge(a, b)
    assert OmegaConf.to_container(m)["items"] == [3]


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from omegaconf\b|import omegaconf\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
