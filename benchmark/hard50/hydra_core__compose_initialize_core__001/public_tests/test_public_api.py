from __future__ import annotations

from pathlib import Path

from featurelifted import GlobalHydra, compose, initialize
from omegaconf import DictConfig


CONFIG_DIR = Path(__file__).parent / "fixtures_public_configs"


def _write_configs() -> None:
    assert (CONFIG_DIR / "config.yaml").is_file()


def test_initialize_compose_and_context_cleanup() -> None:
    _write_configs()
    GlobalHydra.instance().clear()
    with initialize(config_path="fixtures_public_configs", job_name="public"):
        assert GlobalHydra.instance().is_initialized()
        cfg = compose(config_name="config")
        assert isinstance(cfg, DictConfig)
        assert cfg.service.host == "localhost"
        assert cfg.service.port == 8000
    assert not GlobalHydra.instance().is_initialized()


def test_dotted_override() -> None:
    _write_configs()
    GlobalHydra.instance().clear()
    with initialize(config_path="fixtures_public_configs"):
        cfg = compose(
            config_name="config",
            overrides=["service.port=9000", "+service.secure=true"],
        )
        assert cfg.service.port == 9000
        assert cfg.service.secure is True
