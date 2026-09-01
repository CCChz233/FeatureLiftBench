from __future__ import annotations

from featurelifted import APISpec, BasePlugin


class TagPlugin(BasePlugin):
    def init_spec(self, spec: APISpec) -> None:
        self.spec = spec

    def path_helper(self, path=None, operations=None, parameters=None, **kwargs):
        if operations is not None:
            operations.setdefault(
                "get",
                {"responses": {"200": {"description": "ok"}}},
            )
        return path


def test_path_is_recorded_in_spec() -> None:
    spec = APISpec(title="Pets", version="1.0.0", openapi_version="3.0.2")
    spec.path(
        path="/pets",
        operations={"get": {"responses": {"200": {"description": "list"}}}},
    )
    assert "/pets" in spec.to_dict()["paths"]


def test_component_schema_is_named() -> None:
    spec = APISpec(title="Pets", version="1.0.0", openapi_version="3.0.2")
    spec.components.schema(
        "Pet",
        {"type": "object", "properties": {"id": {"type": "integer"}}},
    )
    schemas = spec.to_dict()["components"]["schemas"]
    assert "Pet" in schemas
    assert schemas["Pet"]["type"] == "object"


def test_plugin_init_spec_runs_on_construction() -> None:
    plugin = TagPlugin()
    spec = APISpec(
        title="Pets",
        version="1.0.0",
        openapi_version="3.0.2",
        plugins=[plugin],
    )
    assert plugin.spec is spec


def test_plugin_path_helper_can_fill_operations() -> None:
    spec = APISpec(
        title="Pets",
        version="1.0.0",
        openapi_version="3.0.2",
        plugins=[TagPlugin()],
    )
    spec.path(path="/health")
    assert "get" in spec.to_dict()["paths"]["/health"]
