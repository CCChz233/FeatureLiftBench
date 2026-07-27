"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    BasePlugin,
    PluginMeta,
    PluginRegistry,
    state,
)


def test_required_api_surface():
    assert isinstance(BasePlugin, type)
    assert isinstance(PluginMeta, type)
    assert isinstance(PluginRegistry, type)
    assert hasattr(PluginRegistry, 'register')
    assert hasattr(PluginRegistry, 'discover_classes')
    assert hasattr(PluginRegistry, 'run')
    assert state is not None
    assert getattr(state, 'GLOBAL_STATE') is not None
    assert callable(getattr(state, 'reset_state'))
