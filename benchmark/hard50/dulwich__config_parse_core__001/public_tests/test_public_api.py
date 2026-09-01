from __future__ import annotations

from io import BytesIO

from featurelifted import ConfigFile


SAMPLE = b"""[core]
\tfilemode = true
[remote "origin"]
\turl = git@example.com:lift.git
"""


def test_core_filemode_from_file() -> None:
    cfg = ConfigFile.from_file(BytesIO(SAMPLE), expand_includes=False)
    assert cfg.get((b"core",), b"filemode") == b"true"


def test_subsection_remote_url() -> None:
    cfg = ConfigFile.from_file(BytesIO(SAMPLE), expand_includes=False)
    assert cfg.get((b"remote", b"origin"), b"url") == b"git@example.com:lift.git"
