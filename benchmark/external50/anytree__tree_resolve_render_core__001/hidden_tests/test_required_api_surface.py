import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "ChildResolverError")
    assert hasattr(featurelifted, "Node")
    assert hasattr(featurelifted, "PreOrderIter")
    assert hasattr(featurelifted, "RenderTree")
    assert hasattr(featurelifted, "Resolver")
    assert hasattr(featurelifted, "ResolverError")
    assert hasattr(featurelifted, "findall")
    assert callable(featurelifted.Resolver.get)
    assert callable(featurelifted.RenderTree.__iter__)
