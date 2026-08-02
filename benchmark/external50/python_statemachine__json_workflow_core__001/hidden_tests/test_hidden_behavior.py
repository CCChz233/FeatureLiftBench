import json
import pytest
from featurelifted import InvalidDefinition, load


def test_instances_have_independent_configuration():
    doc = json.dumps({"states": {"idle": {"initial": True, "transitions": [{"event": "go", "target": "done"}]}, "done": {"final": True}}})
    cls = load(doc, format="json")
    first, second = cls(), cls(); first.send("go")
    assert [state.id for state in first.configuration] == ["done"]
    assert [state.id for state in second.configuration] == ["idle"]


def test_invalid_definition_is_rejected():
    with pytest.raises(InvalidDefinition):
        load(json.dumps({"states": {}}), format="json")


def test_required_api_surface():
    from featurelifted import InvalidDefinition, StateChart, load
    assert callable(load)
    assert isinstance(StateChart, type)
    assert callable(StateChart.send)
    assert issubclass(InvalidDefinition, Exception)


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from statemachine|import statemachine)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
