from __future__ import annotations

import os
from pathlib import Path

from featurelifted import bootstrap_config
from featurelifted import merge_config_layers


def test_env_placeholder_expansion(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("VIBE_SHOP_CURRENCY", "EUR")
    cfg_file = tmp_path / "overlay.yaml"
    cfg_file.write_text(
        "app:\n  currency: ${VIBE_SHOP_CURRENCY:-USD}\n",
        encoding="utf-8",
    )
    from featurelifted.config_loader import load_yaml_config

    loaded = load_yaml_config(cfg_file)

    assert loaded["app"]["currency"] == "EUR"


def test_bootstrap_records_side_effects() -> None:
    from featurelifted.state import GLOBAL_STATE, reset_state

    reset_state()
    config_dir = Path(__file__).resolve().parents[1] / "repo" / "config"
    bootstrap_config(config_dir)

    assert GLOBAL_STATE["bootstrapped"] is True
    assert GLOBAL_STATE["load_count"] == 4
    assert len(GLOBAL_STATE["config_paths"]) == 4
    assert GLOBAL_STATE["feature_flags"]["pricing_v2"] is True


def test_merge_does_not_mutate_inputs() -> None:
    left = {"nested": {"keep": 1}}
    right = {"nested": {"add": 2}}

    merged = merge_config_layers(left, right)

    assert merged == {"nested": {"keep": 1, "add": 2}}
    assert left == {"nested": {"keep": 1}}
