"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    bootstrap_config,
    merge_config_layers,
    config_loader,
    state,
)


def test_required_api_surface():
    assert callable(bootstrap_config)
    assert callable(merge_config_layers)
    assert config_loader is not None
    assert callable(getattr(config_loader, 'load_yaml_config'))
    assert state is not None
    assert getattr(state, 'GLOBAL_STATE') is not None
    assert callable(getattr(state, 'reset_state'))
