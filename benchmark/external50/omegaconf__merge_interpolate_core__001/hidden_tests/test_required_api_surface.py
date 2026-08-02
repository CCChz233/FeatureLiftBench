from featurelifted import OmegaConf
from featurelifted.errors import ConfigKeyError, InterpolationResolutionError


def test_required_api_surface() -> None:
    assert hasattr(OmegaConf, "create")
    assert hasattr(OmegaConf, "merge")
    assert hasattr(OmegaConf, "to_container")
    assert hasattr(OmegaConf, "select")
    assert hasattr(OmegaConf, "resolve")
    assert hasattr(OmegaConf, "is_missing")
    assert hasattr(OmegaConf, "is_config")
    assert hasattr(OmegaConf, "set_struct")
    assert InterpolationResolutionError is not None and ConfigKeyError is not None
