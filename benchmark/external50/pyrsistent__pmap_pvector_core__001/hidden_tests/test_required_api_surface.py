from featurelifted import PMap, PVector, pmap, pvector


def test_required_api_surface() -> None:
    assert callable(pmap) and callable(pvector)
    assert PMap is not None and PVector is not None
