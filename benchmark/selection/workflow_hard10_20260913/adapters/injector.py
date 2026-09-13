from copy import deepcopy
from injector import Injector, Provider, InstanceProvider, singleton, NoScope, inject
from injector import UnsatisfiedRequirement, CircularDependency, CallError


def container_trace(bindings, operations):
    keys = {}
    counter = [0]
    scopes = {'main': Injector(auto_bind=False)}
    saved = {}
    def token(name):
        return keys.setdefault(name, type('Key_' + name, (), {}))
    def bind(container, row):
        key = token(row['key'])
        if row.get('kind', 'factory') == 'value':
            provider = InstanceProvider(deepcopy(row.get('value')))
        else:
            deps = list(row.get('deps', []))
            namespace = {'inject': inject, 'token': token}
            parameters = ', '.join('p' + str(i) + ': token(' + repr(name) + ')' for i, name in enumerate(deps))
            namespace['construct'] = lambda values: construct(row['key'], values, row.get('fail', False))
            expressions = ', '.join('p' + str(i) for i in range(len(deps)))
            exec('@inject\ndef factory(' + parameters + '):\n    return construct([' + expressions + '])', namespace)
            provider = namespace['factory']
        container.binder.bind(key, to=provider, scope=singleton if row.get('scope', 'transient') == 'singleton' else NoScope)
    def construct(name, values, fail):
        if fail:
            raise RuntimeError('provider failed')
        counter[0] += 1
        return {'key': name, 'serial': counter[0], 'deps': values}
    for row in bindings:
        bind(scopes['main'], row)
    trace = []
    for op in operations:
        try:
            container = scopes[op.get('container', 'main')]
            result = None
            if op['op'] == 'get':
                result = container.get(token(op['key']))
                if 'save' in op:
                    saved[op['save']] = result
            elif op['op'] == 'child':
                child = container.create_child_injector(auto_bind=False)
                for row in op.get('bindings', []):
                    bind(child, row)
                scopes[op['name']] = child
            elif op['op'] == 'same':
                result = saved[op['left']] is saved[op['right']]
            elif op['op'] == 'bind':
                bind(container, op['binding'])
            else:
                raise ValueError('unknown operation')
            trace.append({'result': deepcopy(result)})
        except UnsatisfiedRequirement:
            trace.append({'error': 'missing'})
        except CircularDependency:
            trace.append({'error': 'cycle'})
        except (CallError, RuntimeError):
            trace.append({'error': 'provider'})
    return trace
