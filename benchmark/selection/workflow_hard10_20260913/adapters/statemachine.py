from copy import deepcopy
from statemachine import State, StateMachine
from statemachine.exceptions import TransitionNotAllowed


def events_trace(states, transitions, operations, *, initial, context=None, callbacks=None, rtc=True, allow_empty=False):
    values = deepcopy(context or {})
    actions = deepcopy(callbacks or {})
    log = []
    attrs = {}
    for row in states:
        row = {'name': row} if isinstance(row, str) else row
        attrs[row['name']] = State(row['name'], initial=row['name'] == initial, final=row.get('final', False),
                                  enter=row.get('enter'), exit=row.get('exit'))
    def callback(name):
        def invoke(self, event, **kwargs):
            current = self.current_state_value
            log.append({'kind': 'callback', 'name': name, 'event': str(event), 'state': current})
            for action in actions[name]:
                if action['op'] == 'set':
                    values[action['key']] = deepcopy(action['value'])
                elif action['op'] == 'emit':
                    self.send(action['event'], **deepcopy(action.get('kwargs', {})))
                elif action['op'] == 'raise':
                    raise RuntimeError('callback failed')
        return invoke
    def guard(name):
        def invoke(self, **kwargs):
            value = bool(values.get(name, False))
            log.append({'kind': 'guard', 'name': name, 'value': value, 'state': self.current_state_value})
            return value
        return invoke
    for name in actions:
        attrs[name] = callback(name)
    for row in transitions:
        for field in ('cond', 'unless'):
            names = row.get(field, [])
            for name in [names] if isinstance(names, str) else names:
                attrs[name] = guard(name)
    for row in transitions:
        opts = {k: deepcopy(row[k]) for k in ('cond', 'unless', 'before', 'after', 'on', 'internal') if k in row}
        edge = attrs[row['source']].to(attrs[row['target']], **opts)
        name = row['event']
        attrs[name] = attrs[name] | edge if name in attrs else edge
    cls = type('RecordStateMachine', (StateMachine,), attrs)
    machine = cls(rtc=rtc, allow_event_without_transition=allow_empty)
    # Initial activation is part of the returned construction record.
    trace = [{'error': None, 'state': machine.current_state_value, 'context': deepcopy(values), 'log': deepcopy(log)}]
    for op in operations:
        log.clear()
        error = None
        try:
            if op['op'] == 'event':
                machine.send(op['event'], **deepcopy(op.get('kwargs', {})))
            elif op['op'] == 'set':
                values.update(deepcopy(op['values']))
            elif op['op'] != 'snapshot':
                raise ValueError('unknown operation')
        except TransitionNotAllowed:
            error = 'transition'
        except RuntimeError:
            error = 'callback'
        trace.append({'error': error, 'state': machine.current_state_value, 'context': deepcopy(values), 'log': deepcopy(log)})
    return trace
