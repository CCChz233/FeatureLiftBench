from __future__ import annotations

from featurelifted import InvalidConfigError, load_config


def test_load_local_hook_config(tmp_path) -> None:
    path = tmp_path / ".pre-commit-config.yaml"
    path.write_text(
        "repos:\n"
        "  - repo: local\n"
        "    hooks:\n"
        "      - id: check\n"
        "        name: check\n"
        "        language: fail\n"
        "        entry: echo\n",
        encoding="utf-8",
    )
    loaded = load_config(str(path))
    hook = loaded["repos"][0]["hooks"][0]
    assert hook["id"] == "check"
    assert hook["language"] == "fail"
    assert hook["entry"] == "echo"
    assert hook["language_version"] == "default"
    assert hook["pass_filenames"] is True


def test_default_minimum_pre_commit_version(tmp_path) -> None:
    path = tmp_path / ".pre-commit-config.yaml"
    path.write_text("repos: []\n", encoding="utf-8")
    loaded = load_config(str(path))
    assert loaded["minimum_pre_commit_version"] == "0"


def test_invalid_schema_raises(tmp_path) -> None:
    path = tmp_path / ".pre-commit-config.yaml"
    path.write_text("hello: world\n", encoding="utf-8")
    try:
        load_config(str(path))
    except InvalidConfigError:
        return
    raise AssertionError("expected InvalidConfigError")


def test_local_hook_requires_string_entry(tmp_path) -> None:
    path = tmp_path / ".pre-commit-config.yaml"
    path.write_text(
        "repos:\n"
        "  - repo: local\n"
        "    hooks:\n"
        "      - id: check\n"
        "        name: check\n"
        "        language: fail\n"
        "        entry: true\n",
        encoding="utf-8",
    )
    try:
        load_config(str(path))
    except InvalidConfigError:
        return
    raise AssertionError("expected InvalidConfigError")
