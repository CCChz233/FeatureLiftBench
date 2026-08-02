from __future__ import annotations

from io import StringIO

from featurelifted import ConfigUpdater


INI = """[app]
# keep this comment
name = old
enabled = true
"""


def test_read_modify_write_stringio() -> None:
    cu = ConfigUpdater()
    cu.read_string(INI)
    assert cu["app"]["name"].value == "old"
    cu["app"]["name"].value = "new"
    buf = StringIO()
    cu.write(buf)
    out = buf.getvalue()
    assert "# keep this comment" in out
    assert "name = new" in out


def test_section_option_access() -> None:
    cu = ConfigUpdater()
    cu.read_string("[s]\nkey = v\n")
    assert "s" in cu
    assert cu["s"]["key"].value == "v"


def test_add_option() -> None:
    cu = ConfigUpdater()
    cu.read_string("[s]\na = 1\n")
    cu["s"]["b"] = "2"
    buf = StringIO()
    cu.write(buf)
    assert "b = 2" in buf.getvalue()
