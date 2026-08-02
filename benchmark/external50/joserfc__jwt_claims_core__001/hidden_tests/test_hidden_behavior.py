from __future__ import annotations

import time

from featurelifted import jwt
from featurelifted.errors import ExpiredTokenError
from featurelifted.jwk import OctKey


def test_exp_claim() -> None:
    from featurelifted.jwt import JWTClaimsRegistry

    key = OctKey.import_key("secretsecretsecret")
    now = int(time.time())
    token = jwt.encode({"alg": "HS256"}, {"sub": "u", "exp": now + 3600}, key)
    decoded = jwt.decode(token, key)
    assert decoded.claims["sub"] == "u"
    expired = jwt.encode({"alg": "HS256"}, {"sub": "u", "exp": now - 10}, key)
    tok = jwt.decode(expired, key)
    try:
        JWTClaimsRegistry().validate(tok.claims)
        assert False, "expected ExpiredTokenError"
    except ExpiredTokenError:
        pass


def test_no_upstream_import_surface() -> None:
    import re
    from pathlib import Path
    import featurelifted

    pkg_root = Path(featurelifted.__file__).parent
    pattern = re.compile(
        rf"^\s*(?:from joserfc\b|import joserfc\b)",
        re.MULTILINE,
    )
    for path in pkg_root.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8")), path
