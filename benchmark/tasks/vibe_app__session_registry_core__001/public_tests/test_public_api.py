from featurelifted import SessionRegistry


def test_register_and_resolve_session() -> None:
    registry = SessionRegistry()

    token = registry.register("user-42", metadata={"role": "admin"})
    session = registry.resolve(token)

    assert session is not None
    assert session["user_id"] == "user-42"
    assert session["metadata"]["role"] == "admin"


def test_resolve_normalizes_token_case() -> None:
    registry = SessionRegistry()
    token = registry.register("user-7")

    session = registry.resolve(f"  {token.upper()}  ")

    assert session is not None
    assert session["user_id"] == "user-7"
