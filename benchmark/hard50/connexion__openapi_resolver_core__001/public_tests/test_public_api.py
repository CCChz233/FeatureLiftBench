from __future__ import annotations

from types import SimpleNamespace

from featurelifted import Resolution, Resolver, RestyResolver


def _op(spec: dict, path: str, method: str):
    node = spec["paths"][path][method]
    return SimpleNamespace(
        operation_id=node.get("operationId"),
        router_controller=node.get("x-openapi-router-controller"),
        path=path,
        method=method,
    )


SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Demo", "version": "1.0.0"},
    "paths": {
        "/ping": {
            "get": {"operationId": "builtins.len"},
        },
        "/pets": {
            "get": {},
            "post": {},
        },
    },
}


def test_resolver_maps_operation_id_from_spec_dict() -> None:
    resolver = Resolver()
    result = resolver.resolve(_op(SPEC, "/ping", "get"))
    assert isinstance(result, Resolution)
    assert result.function is len
    assert result.operation_id == "builtins.len"


def test_resty_resolver_uses_path_semantics_when_operation_id_missing() -> None:
    resolver = RestyResolver("api")
    operation_id = resolver.resolve_operation_id(_op(SPEC, "/pets", "get"))
    assert operation_id == "api.pets.search"


def test_resty_resolver_keeps_explicit_operation_id() -> None:
    resolver = RestyResolver("api")
    operation_id = resolver.resolve_operation_id(_op(SPEC, "/ping", "get"))
    assert operation_id == "builtins.len"


def test_custom_function_resolver() -> None:
    def ping():
        return "pong"

    resolver = Resolver(function_resolver=lambda operation_id: ping)
    result = resolver.resolve(_op(SPEC, "/ping", "get"))
    assert result.function is ping
