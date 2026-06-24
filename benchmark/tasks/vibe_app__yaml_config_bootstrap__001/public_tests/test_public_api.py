from __future__ import annotations

from featurelifted import bootstrap_config
from featurelifted import merge_config_layers


def test_merge_config_layers_deep_merges_nested_keys() -> None:
    base = {"app": {"name": "VibeShop", "debug": False}, "features": {"csv_import": True}}
    overlay = {"app": {"debug": True}, "features": {"legacy_reports": False}}

    merged = merge_config_layers(base, overlay)

    assert merged["app"] == {"name": "VibeShop", "debug": True}
    assert merged["features"] == {"csv_import": True, "legacy_reports": False}


def test_bootstrap_config_loads_repo_layers() -> None:
    import pathlib

    config_dir = pathlib.Path(__file__).resolve().parents[1] / "repo" / "config"
    cfg = bootstrap_config(config_dir)

    assert cfg["app"]["name"] == "VibeShop"
    assert cfg["app"]["debug"] is True
    assert cfg["pricing"]["categories"]["books"] == 0.95
    assert cfg["pricing"]["tiers"][1]["multiplier"] == 0.95
