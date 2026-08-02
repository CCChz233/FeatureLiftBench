from operator import itemgetter
from featurelifted import MethodicalMachine


def make_switch():
    class Switch:
        machine = MethodicalMachine()
        @machine.state(initial=True, serialized="off")
        def off(self): pass
        @machine.state(serialized="on")
        def on(self): pass
        @machine.input()
        def flip(self): pass
        off.upon(flip, enter=on, outputs=[])
        on.upon(flip, enter=off, outputs=[])
        @machine.input()
        def query(self): pass
        @machine.output()
        def yes(self): return True
        @machine.output()
        def no(self): return False
        off.upon(query, enter=off, outputs=[no], collector=itemgetter(0))
        on.upon(query, enter=on, outputs=[yes], collector=itemgetter(0))
    return Switch


def test_transition_and_collected_output():
    switch = make_switch()()
    assert switch.query() is False
    switch.flip()
    assert switch.query() is True


def test_instances_keep_independent_state():
    Switch = make_switch(); left = Switch(); right = Switch()
    left.flip()
    assert left.query() is True and right.query() is False
