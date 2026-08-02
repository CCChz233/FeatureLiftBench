from __future__ import annotations

import datetime
import re
from pathlib import Path

from featurelifted import HOTP, TOTP, random_base32


SECRET = "JBSWY3DPEHPK3PXP"


def test_totp_verify_rejects_wrong() -> None:
    totp = TOTP(SECRET)
    when = datetime.datetime.fromtimestamp(1234567890)
    assert totp.verify("000000", when) is False


def test_hotp_counter_increments() -> None:
    hotp = HOTP(SECRET)
    assert hotp.at(0) != hotp.at(1)


def test_random_base32_length_guard() -> None:
    try:
        random_base32(length=16)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_no_upstream_import_surface() -> None:
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(r"^\s*(?:from pyotp\b|import pyotp\b)", re.MULTILINE)
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
