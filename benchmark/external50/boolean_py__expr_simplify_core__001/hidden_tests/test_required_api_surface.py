import featurelifted


def test_required_api_surface() -> None:
    assert hasattr(featurelifted, "BooleanAlgebra")
    assert hasattr(featurelifted, "Expression")
    assert hasattr(featurelifted, "ParseError")
    assert hasattr(featurelifted, "Symbol")
    instance_0 = featurelifted.BooleanAlgebra()
    assert callable(instance_0.parse)
    assert hasattr(instance_0, "Symbol")
    assert hasattr(instance_0, "TRUE")
    assert hasattr(instance_0, "FALSE")
    assert callable(instance_0.parse)
    assert callable(featurelifted.Expression.simplify)
    assert callable(featurelifted.Expression.subs)
