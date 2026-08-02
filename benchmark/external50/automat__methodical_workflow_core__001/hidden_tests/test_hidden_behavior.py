from featurelifted import MethodicalMachine, NoTransition


def test_serializer_roundtrip():
    class Switch:
        machine = MethodicalMachine()
        @machine.state(initial=True, serialized="off")
        def off(self): pass
        @machine.state(serialized="on")
        def on(self): pass
        @machine.input()
        def flip(self): pass
        off.upon(flip, enter=on, outputs=[]); on.upon(flip, enter=off, outputs=[])
        @machine.serializer()
        def save(self, state): return state
        @machine.unserializer()
        def restore(self, state): return state
    first = Switch(); first.flip(); state = first.save()
    second = Switch(); second.restore(state)
    assert second.save() == "on"


def test_undeclared_transition_raises():
    class OneWay:
        machine = MethodicalMachine()
        @machine.state(initial=True)
        def start(self): pass
        @machine.state()
        def end(self): pass
        @machine.input()
        def go(self): pass
        start.upon(go, enter=end, outputs=[])
    obj = OneWay(); obj.go()
    try: obj.go()
    except NoTransition: pass
    else: raise AssertionError("NoTransition not raised")


def test_required_api_surface():
    from featurelifted import MethodicalMachine, NoTransition
    assert isinstance(MethodicalMachine, type)
    assert issubclass(NoTransition, Exception)


def test_no_upstream_import_surface():
    import re
    from pathlib import Path
    import featurelifted
    pattern = re.compile(r"^\s*(?:from automat|import automat)\b", re.MULTILINE)
    for path in Path(featurelifted.__file__).parent.rglob("*.py"):
        assert not pattern.search(path.read_text(encoding="utf-8"))
