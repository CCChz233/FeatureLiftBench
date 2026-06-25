from featurelifted import SessionRegistry
from featurelifted.state import GLOBAL_STATE
from featurelifted.state import reset_state


def test_revoke_removes_session() -> None:
    registry = SessionRegistry()
    token = registry.register("user-1")

    assert registry.resolve(token) is not None
    assert registry.revoke(token) is True
    assert registry.resolve(token) is None


def test_register_tracks_session_ids_in_global_state() -> None:
    reset_state()
    registry = SessionRegistry()

    token_a = registry.register("alice")
    token_b = registry.register("bob")

    sessions = GLOBAL_STATE["sessions"]
    assert len(sessions) == 2
    assert registry.resolve(token_a)["user_id"] == "alice"
    assert registry.resolve(token_b)["user_id"] == "bob"


def test_revoke_updates_global_state_session_list() -> None:
    reset_state()
    registry = SessionRegistry()
    token = registry.register("user-9")

    assert len(GLOBAL_STATE["sessions"]) == 1
    registry.revoke(token)
    assert GLOBAL_STATE["sessions"] == []
