from __future__ import annotations

import featurelifted as fl


def test_declared_interface_is_provided() -> None:
    class ISource(fl.Interface):
        pass

    @fl.implementer(ISource)
    class Source:
        pass

    source = Source()
    assert ISource in fl.providedBy(source)
    assert ISource.providedBy(source)


def test_named_single_adapter_dispatch() -> None:
    class ISource(fl.Interface):
        pass

    class ITarget(fl.Interface):
        pass

    @fl.implementer(ISource)
    class Source:
        pass

    class Adapter:
        def __init__(self, context: Source) -> None:
            self.context = context

    registry = fl.AdapterRegistry()
    registry.register((ISource,), ITarget, "primary", Adapter)
    source = Source()
    adapted = registry.queryAdapter(source, ITarget, "primary")
    assert isinstance(adapted, Adapter)
    assert adapted.context is source
    assert registry.queryAdapter(source, ITarget) is None


def test_multi_adapter_dispatch() -> None:
    class ILeft(fl.Interface):
        pass

    class IRight(fl.Interface):
        pass

    class IResult(fl.Interface):
        pass

    @fl.implementer(ILeft)
    class Left:
        pass

    @fl.implementer(IRight)
    class Right:
        pass

    registry = fl.AdapterRegistry()
    registry.register((ILeft, IRight), IResult, "", lambda left, right: (left, right))
    left, right = Left(), Right()
    assert registry.queryMultiAdapter((left, right), IResult) == (left, right)
