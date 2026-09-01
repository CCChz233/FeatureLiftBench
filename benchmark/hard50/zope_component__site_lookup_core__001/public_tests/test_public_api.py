from __future__ import annotations

from featurelifted import (
    ComponentLookupError,
    Interface,
    getUtility,
    implementer,
    provideUtility,
    queryUtility,
)


class IGreeting(Interface):
    pass


class IUnused(Interface):
    pass


@implementer(IGreeting)
class Greeting:
    def __init__(self, text: str) -> None:
        self.text = text


def test_provide_then_get_utility() -> None:
    greeting = Greeting("hello")
    provideUtility(greeting)
    assert getUtility(IGreeting) is greeting


def test_query_utility_returns_default_when_missing() -> None:
    assert queryUtility(IUnused, default="absent") == "absent"
    assert queryUtility(IUnused) is None


def test_get_utility_raises_when_unregistered() -> None:
    try:
        getUtility(IUnused)
    except ComponentLookupError:
        return
    raise AssertionError("expected ComponentLookupError")


def test_named_utility_lookup() -> None:
    first = Greeting("one")
    second = Greeting("two")
    provideUtility(first, name="first")
    provideUtility(second, name="second")
    assert getUtility(IGreeting, name="first") is first
    assert getUtility(IGreeting, name="second") is second
