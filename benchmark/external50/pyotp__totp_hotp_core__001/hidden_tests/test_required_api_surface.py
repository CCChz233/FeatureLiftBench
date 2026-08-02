from featurelifted import HOTP, TOTP, random_base32


def test_required_api_surface() -> None:
    assert TOTP is not None and HOTP is not None
    assert callable(random_base32)
