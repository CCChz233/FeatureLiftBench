from copy import deepcopy
from traitlets import HasTraits, Int, Float, Unicode, Bool, List, TraitError, validate


def model_trace(schema, operations, *, initial=None, rules=()):
    attributes = {}
    for name, field in schema.items():
        kind = field['type']
        opts = {k: deepcopy(field[k]) for k in ('min', 'max', 'allow_none') if k in field}
        if 'default' in field:
            opts['default_value'] = deepcopy(field['default'])
        if kind == 'list_int':
            trait = List(Int(), **opts)
        else:
            trait = {'int': Int, 'float': Float, 'text': Unicode, 'bool': Bool}[kind](**opts)
        attributes[name] = trait
    for name in schema:
        relevant = [r for r in rules if r['field'] == name]
        if relevant:
            def validator(self, proposal, relevant=relevant):
                value = proposal['value']
                for rule in relevant:
                    other = getattr(self, rule['other'])
                    valid = value <= other if rule.get('op', 'le') == 'le' else value >= other
                    if not valid:
                        raise TraitError('cross-field invariant')
                return value
            attributes['_validate_' + name] = validate(name)(validator)
    cls = type('RecordModel', (HasTraits,), attributes)
    model = cls(**deepcopy(initial or {}))
    for name in schema:
        getattr(model, name)
    changes = []
    def snapshot():
        return {name: deepcopy(getattr(model, name)) for name in schema}
    def observe(change):
        changes.append({'name': change.name, 'old': deepcopy(change.old), 'new': deepcopy(change.new), 'values': snapshot()})
    model.observe(observe, names=list(schema))
    trace = []
    for op in operations:
        changes.clear()
        error = None
        try:
            if op['op'] == 'set':
                setattr(model, op['field'], deepcopy(op['value']))
            elif op['op'] == 'batch':
                with model.hold_trait_notifications():
                    for update in op['updates']:
                        setattr(model, update['field'], deepcopy(update['value']))
            elif op['op'] == 'append':
                getattr(model, op['field']).append(deepcopy(op['value']))
            elif op['op'] == 'watch':
                model.observe(observe, names=op['fields'])
            elif op['op'] == 'unwatch':
                model.unobserve(observe, names=op['fields'])
            elif op['op'] != 'snapshot':
                raise ValueError('unknown operation')
        except TraitError:
            error = 'TraitError'
        trace.append({'error': error, 'values': snapshot(), 'changes': deepcopy(changes)})
    return trace
