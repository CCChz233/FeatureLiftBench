from __future__ import annotations

import datetime

from featurelifted import HOTP, TOTP, random_base32


SECRET = "JBSWY3DPEHPK3PXP"


def test_totp_at_verify() -> None:
    totp = TOTP(SECRET)
    when = datetime.datetime.fromtimestamp(1234567890)
    code = totp.at(when)
    assert code == "742275"
    assert totp.verify(code, when) is True


def test_hotp_at_verify() -> None:
    hotp = HOTP(SECRET)
    code = hotp.at(0)
    assert code == "282760"
    assert hotp.verify(code, 0) is True


def test_random_base32() -> None:
    secret = random_base32()
    assert len(secret) == 32
    assert set(secret) <= set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
