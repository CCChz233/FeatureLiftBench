from __future__ import annotations

from featurelifted import PyLinter, UnrecognizedOptionError, find_default_config_files


def test_finds_pylintrc_in_cwd(tmp_path, monkeypatch) -> None:
    rcfile = tmp_path / "pylintrc"
    rcfile.write_text("[MAIN]\ndisable=unused-import\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    found = list(find_default_config_files())
    assert rcfile in found or any(path.name == "pylintrc" for path in found)


def test_command_line_disable_turns_message_off() -> None:
    linter = PyLinter()
    linter.load_default_plugins()
    assert linter.is_message_enabled("unused-import") is True
    linter._parse_command_line_configuration(["--disable=unused-import"])
    assert linter.is_message_enabled("unused-import") is False


def test_configuration_file_disable_turns_message_off() -> None:
    linter = PyLinter()
    linter.load_default_plugins()
    linter._parse_configuration_file(["--disable=unused-import"])
    assert linter.is_message_enabled("unused-import") is False


def test_unknown_option_raises() -> None:
    linter = PyLinter()
    linter.load_default_plugins()
    try:
        linter._parse_configuration_file(["--not-a-real-pylint-option"])
    except UnrecognizedOptionError as exc:
        assert "not-a-real-pylint-option" in exc.options
        return
    raise AssertionError("expected UnrecognizedOptionError")
