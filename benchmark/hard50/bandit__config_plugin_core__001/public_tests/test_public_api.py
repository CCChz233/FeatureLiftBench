from __future__ import annotations

from featurelifted import BanditConfig, BanditTestSet, ConfigError


def test_config_loads_skip_and_include_lists(tmp_path) -> None:
    path = tmp_path / "bandit.yaml"
    path.write_text("skips: [B101]\ntests: [B201]\n", encoding="utf-8")
    config = BanditConfig(str(path))
    assert config.get_option("skips") == ["B101"]
    assert config.get_option("tests") == ["B201"]


def test_include_filter_keeps_only_listed_ids() -> None:
    selected = BanditTestSet._get_filter(
        BanditConfig(), {"include": ["B201"], "exclude": []}
    )
    assert selected == {"B201"}


def test_exclude_filter_removes_listed_ids() -> None:
    selected = BanditTestSet._get_filter(
        BanditConfig(), {"include": ["B101", "B201"], "exclude": ["B101"]}
    )
    assert "B101" not in selected
    assert "B201" in selected


def test_invalid_yaml_raises_config_error(tmp_path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("- [ unterminated", encoding="utf-8")
    try:
        BanditConfig(str(path))
    except ConfigError:
        return
    raise AssertionError("expected ConfigError")
