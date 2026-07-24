"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    MultiDict,
    CIMultiDict,
    MultiDictProxy,
    CIMultiDictProxy,
)


def test_required_api_surface():
    assert isinstance(MultiDict, type)
    assert hasattr(MultiDict, 'add')
    assert hasattr(MultiDict, 'popall')
    assert hasattr(MultiDict, 'popone')
    assert isinstance(CIMultiDict, type)
    assert hasattr(CIMultiDict, 'add')
    assert hasattr(CIMultiDict, 'getall')
    assert isinstance(MultiDictProxy, type)
    assert isinstance(CIMultiDictProxy, type)
    assert hasattr(CIMultiDictProxy, 'add')
