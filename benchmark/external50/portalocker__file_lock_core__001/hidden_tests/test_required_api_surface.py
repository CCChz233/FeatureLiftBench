from featurelifted import LOCK_EX, Lock, lock, unlock


def test_required_api_surface() -> None:
    assert Lock is not None and callable(lock) and callable(unlock)
    assert LOCK_EX is not None
