from __future__ import annotations

from featurelifted import ConfigOpts, Opt, OptGroup


def test_registered_default() -> None:
    conf = ConfigOpts()
    conf.register_opt(Opt("host", default="localhost"))
    conf(args=[])
    assert conf.host == "localhost"


def test_grouped_option() -> None:
    conf = ConfigOpts()
    group = OptGroup("database")
    conf.register_group(group)
    conf.register_opt(Opt("port", default="5432"), group=group)
    conf(args=[])
    assert conf.database.port == "5432"


def test_file_overlay(tmp_path) -> None:
    path = tmp_path / "app.conf"
    path.write_text("[DEFAULT]\nhost = file-host\n", encoding="utf-8")
    conf = ConfigOpts()
    conf.register_opt(Opt("host", default="localhost"))
    conf(args=["--config-file", str(path)])
    assert conf.host == "file-host"


def test_cli_overrides_file(tmp_path) -> None:
    path = tmp_path / "app.conf"
    path.write_text("[DEFAULT]\nhost = file-host\n", encoding="utf-8")
    conf = ConfigOpts()
    conf.register_opt(Opt("host", default="localhost"), cli=True)
    conf(args=["--config-file", str(path), "--host", "cli-host"])
    assert conf.host == "cli-host"
