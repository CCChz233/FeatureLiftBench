from copy import deepcopy
from types import SimpleNamespace
from transitions.extensions.nesting import HierarchicalMachine
from transitions.core import MachineError


def hierarchy_trace(states, transitions, operations, *, initial, context=None, callbacks=None, queued=False):
    values = deepcopy(context or {})
    actions = deepcopy(callbacks or {})
    log = []
    model = SimpleNamespace()
    def callback(name):
        def invoke(data):
            log.append({'kind': 'callback', 'name': name, 'event': data.event.name,
                        'state': deepcopy(model.state)})
            for action in actions[name]:
                if action['op'] == 'set':
                    values[action['key']] = deepcopy(action['value'])
                elif action['op'] == 'emit':
                    model.trigger(action['event'], **deepcopy(action.get('kwargs', {})))
                elif action['op'] == 'raise':
                    raise RuntimeError('callback failed')
        return invoke
    def guard(name):
        def invoke(data):
            value = bool(values.get(name, False))
            log.append({'kind': 'guard', 'name': name, 'value': value, 'state': deepcopy(model.state)})
            return value
        return invoke
    for name in actions:
        setattr(model, name, callback(name))
    for row in transitions:
        for key in ('conditions', 'unless'):
            names = row.get(key, [])
            for name in [names] if isinstance(names, str) else names:
                setattr(model, name, guard(name))
    machine = HierarchicalMachine(model, states=deepcopy(states), transitions=deepcopy(transitions),
                                  initial=deepcopy(initial), auto_transitions=False,
                                  send_event=True, queued=queued)
    trace = []
    for op in operations:
        log.clear()
        error, result = None, None
        try:
            if op['op'] == 'event':
                result = model.trigger(op['event'], **deepcopy(op.get('kwargs', {})))
            elif op['op'] == 'set':
                values.update(deepcopy(op['values']))
            elif op['op'] != 'snapshot':
                raise ValueError('unknown operation')
        except MachineError:
            error = 'transition'
        except (AttributeError, ValueError):
            error = 'event'
        except RuntimeError:
            error = 'callback'
        trace.append({'result': result, 'error': error, 'state': deepcopy(model.state),
                      'context': deepcopy(values), 'log': deepcopy(log)})
    return trace
