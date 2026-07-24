"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    SessionRegistry,
    state,
)


def test_required_api_surface():
    assert isinstance(SessionRegistry, type)
    assert hasattr(SessionRegistry, 'register')
    assert hasattr(SessionRegistry, 'resolve')
    assert hasattr(SessionRegistry, 'revoke')
    assert state is not None
    assert getattr(state, 'GLOBAL_STATE') is not None
    assert callable(getattr(state, 'reset_state'))
