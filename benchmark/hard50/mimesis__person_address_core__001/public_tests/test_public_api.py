from __future__ import annotations

from featurelifted import Address, Locale, Person


def test_person_name_is_nonempty_string() -> None:
    person = Person(locale=Locale("en"), seed=7)
    name = person.name()
    assert isinstance(name, str) and name
    assert Person(locale=Locale("en"), seed=7).name() == name


def test_address_city_is_nonempty_string() -> None:
    address = Address(locale=Locale("en"), seed=7)
    city = address.city()
    assert isinstance(city, str) and city
