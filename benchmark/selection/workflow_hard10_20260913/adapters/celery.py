from copy import deepcopy
import json
from celery import Celery
from celery.canvas import Signature, chain, group, chord, StampingVisitor


def canvas_trace(spec, operations):
    app = Celery('offline_canvas', set_as_current=False, fixups=[])
    def build(row):
        kind = row.get('kind', 'task')
        options = deepcopy(row.get('options', {}))
        if kind == 'task':
            result = Signature(row['task'], args=deepcopy(row.get('args', [])),
                               kwargs=deepcopy(row.get('kwargs', {})), options=options,
                               immutable=row.get('immutable', False), app=app)
        elif kind == 'chain':
            result = chain([build(t) for t in row['tasks']], app=app, **options)
        elif kind == 'group':
            result = group([build(t) for t in row['tasks']], app=app, **options)
        elif kind == 'chord':
            result = chord([build(t) for t in row['header']], build(row['body']), app=app, **options)
        else:
            raise ValueError('unknown canvas kind')
        for item in row.get('links', []):
            result.link(build(item))
        for item in row.get('errbacks', []):
            result.link_error(build(item))
        return result
    def canonical(value):
        if isinstance(value, dict):
            return {k: sorted(v) if k == 'stamped_headers' else canonical(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [canonical(v) for v in value]
        return value
    def snapshot(value):
        return canonical(json.loads(json.dumps(dict(value))))
    class Visitor(StampingVisitor):
        def __init__(self, rules):
            self.rules = rules
        def on_signature(self, sig, **headers):
            return deepcopy(self.rules.get('tasks', {}).get(sig.task, {}))
        def on_group_start(self, sig, **headers):
            return deepcopy(self.rules.get('group', {}))
        def on_chain_start(self, sig, **headers):
            return deepcopy(self.rules.get('chain', {}))
        def on_chord_header_start(self, sig, **headers):
            return deepcopy(self.rules.get('chord_header', {}))
        def on_chord_body(self, sig, **headers):
            return deepcopy(self.rules.get('chord_body', {}))
    stores = {'main': build(spec)}
    trace = []
    for op in operations:
        sig = stores[op.get('store', 'main')]
        kind = op['op']
        if kind == 'stamp':
            sig.stamp(Visitor(op.get('visitor', {})), append_stamps=op.get('append', False), **deepcopy(op.get('headers', {})))
        elif kind == 'clone':
            stores[op['target']] = sig.clone(args=deepcopy(op.get('args', [])), kwargs=deepcopy(op.get('kwargs', {})), **deepcopy(op.get('options', {})))
        elif kind == 'set':
            sig.set(**deepcopy(op['options']))
        elif kind == 'immutable':
            sig.set_immutable(op['value'])
        elif kind == 'link':
            sig.link(build(op['signature']))
        elif kind == 'errback':
            sig.link_error(build(op['signature']))
        elif kind != 'snapshot':
            raise ValueError('unknown operation')
        trace.append({name: snapshot(value) for name, value in sorted(stores.items())})
    return trace
