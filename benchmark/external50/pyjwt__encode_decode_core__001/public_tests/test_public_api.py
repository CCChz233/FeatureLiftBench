from __future__ import annotations

import time

from featurelifted import decode, encode
from featurelifted.exceptions import ExpiredSignatureError, InvalidSignatureError


def test_encode_decode_hs256() -> None:
    token = encode({"sub": "user1"}, "secret", algorithm="HS256")
    payload = decode(token, "secret", algorithms=["HS256"])
    assert payload["sub"] == "user1"


def test_wrong_secret() -> None:
    token = encode({"a": 1}, "k", algorithm="HS256")
    try:
        decode(token, "wrong", algorithms=["HS256"])
        assert False, "expected InvalidSignatureError"
    except InvalidSignatureError:
        pass


def test_expired_token() -> None:
    token = encode({"exp": int(time.time()) - 10}, "k", algorithm="HS256")
    try:
        decode(token, "k", algorithms=["HS256"])
        assert False, "expected ExpiredSignatureError"
    except ExpiredSignatureError:
        pass
