from featurelifted import CollectionCheckStrategy, TypeCheckError, check_type


def test_required_api_surface() -> None:
    assert callable(check_type)
    assert TypeCheckError is not None
    assert CollectionCheckStrategy["ALL_ITEMS"] is not None
