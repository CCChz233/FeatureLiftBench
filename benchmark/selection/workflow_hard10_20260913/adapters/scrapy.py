from copy import deepcopy
from scrapy.settings import BaseSettings


def settings_trace(layers, operations):
    stores = {'main': BaseSettings()}
    for layer in layers:
        stores['main'].update(deepcopy(layer['values']), layer.get('priority', 'project'))
    trace = []
    for operation in operations:
        op = deepcopy(operation)
        store = stores[op.get('store', 'main')]
        try:
            name = op['op']
            result = None
            if name == 'set':
                store.set(op['key'], op['value'], op.get('priority', 'project'))
            elif name == 'update':
                store.update(op['values'], op.get('priority', 'project'))
            elif name == 'delete':
                store.delete(op['key'], op.get('priority', 'project'))
            elif name == 'setdefault':
                result = store.setdefault(op['key'], op['value'], op.get('priority', 'project'))
            elif name == 'get':
                kind = op.get('kind', 'value')
                defaults = {'value': None, 'bool': False, 'int': 0, 'float': 0.0, 'list': None, 'dict': None}
                method = store.get if kind == 'value' else getattr(store, 'get' + kind)
                result = method(op['key'], op.get('default', defaults[kind]))
            elif name == 'priority':
                result = store.getpriority(op['key'])
            elif name == 'withbase':
                value = store.getwithbase(op['key'])
                result = {'values': value.copy_to_dict(), 'priorities': {k: value.getpriority(k) for k in value}}
            elif name == 'nested':
                nested = BaseSettings()
                for layer in op['layers']:
                    nested.update(layer['values'], layer.get('priority', 'project'))
                store.set(op['key'], nested, op.get('priority', 'project'))
            elif name == 'copy':
                stores[op['target']] = store.frozencopy() if op.get('frozen', False) else store.copy()
            elif name == 'freeze':
                store.freeze()
            elif name == 'add':
                store.add_to_list(op['key'], op['value'])
            elif name == 'remove':
                store.remove_from_list(op['key'], op['value'])
            elif name == 'snapshot':
                result = {'values': store.copy_to_dict(), 'priorities': {k: store.getpriority(k) for k in store}, 'frozen': store.frozen}
            else:
                raise ValueError('unknown operation')
            trace.append({'result': deepcopy(result)})
        except (KeyError, ValueError, TypeError) as exc:
            trace.append({'error': type(exc).__name__})
    return trace
