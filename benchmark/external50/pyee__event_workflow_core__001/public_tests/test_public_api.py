from featurelifted import EventEmitter


def test_emit_preserves_registration_order():
    emitter = EventEmitter(); seen = []
    emitter.on("data", lambda value: seen.append(("a", value)))
    emitter.on("data", lambda value: seen.append(("b", value)))
    assert emitter.emit("data", 3) is True
    assert seen == [("a", 3), ("b", 3)]


def test_once_listener_runs_once():
    emitter = EventEmitter(); seen = []
    emitter.once("tick", lambda: seen.append(1))
    emitter.emit("tick"); emitter.emit("tick")
    assert seen == [1]
