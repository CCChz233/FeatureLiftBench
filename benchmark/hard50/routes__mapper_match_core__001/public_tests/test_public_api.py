from __future__ import annotations

from featurelifted import Mapper


def _mapper() -> Mapper:
    mapper = Mapper(controller_scan=["main", "user"])
    mapper.connect("home", "/home", controller="main", action="index")
    mapper.connect("user", "/user/{id}", controller="user", action="show")
    return mapper


def test_literal_path_matches_controller() -> None:
    result = _mapper().match("/home")
    assert result is not None
    assert result["controller"] == "main"
    assert result["action"] == "index"


def test_template_path_captures_id() -> None:
    result = _mapper().match("/user/7")
    assert result is not None
    assert result["controller"] == "user"
    assert result["id"] == "7"


def test_unknown_path_returns_none() -> None:
    assert _mapper().match("/missing") is None


def test_generate_rebuilds_connected_urls() -> None:
    mapper = _mapper()
    assert mapper.generate(controller="main", action="index") == "/home"
    assert mapper.generate(controller="user", action="show", id="7") == "/user/7"
