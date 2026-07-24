"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    DataClassJsonMixin,
    LetterCase,
    Exclude,
    Undefined,
    dataclass_json,
    config,
    global_config,
    undefined,
)


def test_required_api_surface():
    assert isinstance(DataClassJsonMixin, type)
    assert isinstance(LetterCase, type)
    assert isinstance(Exclude, type)
    assert isinstance(Undefined, type)
    assert Undefined is not None
    assert callable(dataclass_json)
    assert callable(config)
    assert global_config is not None
    assert undefined is not None
    assert issubclass(getattr(undefined, 'UndefinedParameterError'), BaseException)
