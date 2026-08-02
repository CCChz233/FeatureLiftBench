import json
from featurelifted import load


def definition():
    return json.dumps({"name": "Order", "states": {"draft": {"initial": True, "transitions": [{"event": "submit", "target": "sent"}]}, "sent": {"final": True}}})


def test_load_inline_json_returns_machine_class():
    cls = load(definition(), format="json")
    machine = cls()
    assert [state.id for state in machine.configuration] == ["draft"]


def test_declared_event_moves_to_target():
    machine = load(definition(), format="json")()
    machine.send("submit")
    assert [state.id for state in machine.configuration] == ["sent"]
