"""Constitution API-surface coverage generated from public_spec."""

from featurelifted import (
    Registry,
    Resource,
    exceptions,
    jsonschema,
)


def test_required_api_surface():
    assert isinstance(Registry, type)
    assert hasattr(Registry, 'resolver')
    assert isinstance(Resource, type)
    assert hasattr(Resource, 'from_contents')
    assert exceptions is not None
    assert issubclass(getattr(exceptions, 'NoSuchAnchor'), BaseException)
    assert issubclass(getattr(exceptions, 'Unresolvable'), BaseException)
    assert jsonschema is not None
    assert getattr(jsonschema, 'DRAFT202012') is not None
    assert issubclass(getattr(jsonschema, 'UnknownDialect'), BaseException)
