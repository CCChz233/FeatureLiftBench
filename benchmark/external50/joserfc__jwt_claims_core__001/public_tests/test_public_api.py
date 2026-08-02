from __future__ import annotations

from featurelifted import jwt
from featurelifted.jwk import OctKey


def test_encode_decode_hs256() -> None:
    key = OctKey.import_key("secret")
    token = jwt.encode({"alg": "HS256"}, {"sub": "user-1"}, key)
    decoded = jwt.decode(token, key)
    assert decoded.claims["sub"] == "user-1"


def test_generate_key() -> None:
    key = OctKey.generate_key(256)
    token = jwt.encode({"alg": "HS256"}, {"iss": "test"}, key)
    decoded = jwt.decode(token, key)
    assert decoded.claims["iss"] == "test"
