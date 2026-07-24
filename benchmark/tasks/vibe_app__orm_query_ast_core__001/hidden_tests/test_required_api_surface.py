"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    Query,
    compile_query,
    state,
)


def test_required_api_surface():
    assert isinstance(Query, type)
    assert hasattr(Query, 'build_ast')
    assert callable(compile_query)
    assert state is not None
    assert getattr(state, 'GLOBAL_STATE') is not None
    assert callable(getattr(state, 'reset_state'))
