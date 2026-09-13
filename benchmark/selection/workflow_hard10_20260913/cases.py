"""Authored scenarios; expectations are captured separately from pinned sources.

Behavior IDs refer to definitions.py. None of this enters an agent workspace.
"""
from copy import deepcopy

CASES = {k: [] for k in ['resolvelib', 'django', 'apscheduler', 'doit', 'scrapy', 'traitlets', 'injector', 'celery', 'transitions', 'statemachine']}
def add(source, name, args, ids, *, public=False, error=None):
    CASES[source].append(dict(name=name, args=deepcopy(args), behavior_ids=ids,
                              tier='public' if public else 'hidden', error=error))

def release(name, version, *dependencies):
    return dict(name=name, version=str(version), dependencies=list(dependencies))

# Backtracking, marker contexts, constraints and extras interact in a single solve.
index = [release('app', 2, 'core>=2', 'plugin'), release('app', 1, 'core<2', 'plugin'),
         release('core', 2), release('core', 1), release('plugin', 1, 'core<2')]
add('resolvelib', 'backtrack-parent', dict(index=index, requirements=['app']), ['B001', 'B002'], public=True)
add('resolvelib', 'empty-roots', dict(index=index, requirements=[]), ['B001'], public=True)
add('resolvelib', 'conflicting-roots', dict(index=index, requirements=['core>=2', 'plugin']), ['B002'], error='ValueError', public=True)
add('resolvelib', 'backtrack-with-constraint', dict(index=index, requirements=['app'], constraints=['app<2', 'unused==1']), ['B002', 'B003'])
add('resolvelib', 'constraint-alone-not-root', dict(index=index, requirements=[], constraints=['missing>=99']), ['B003'])
add('resolvelib', 'missing-transitive', dict(index=[release('a', 1, 'missing')], requirements=['a']), ['B002'], error='ValueError')
add('resolvelib', 'canonical-name', dict(index=[release('Some_Pkg', 1)], requirements=['some.pkg>=1']), ['B001'])
add('resolvelib', 'same-package-two-roots', dict(index=[release('a', 1), release('a', 2), release('a', 3)], requirements=['a>=2', 'a<3']), ['B002'])
extra_index = [release('a', 1, 'x; extra == "fast"', 'y; extra == "safe"'), release('x', 1, 'z<2'), release('y', 1, 'z>=1'), release('z', 1), release('z', 2)]
add('resolvelib', 'extras-union', dict(index=extra_index, requirements=['a[fast]', 'a[safe]']), ['B004', 'B002'])
add('resolvelib', 'extras-late-discovery', dict(index=extra_index + [release('b', 1, 'a[safe]')], requirements=['a[fast]', 'b']), ['B004', 'B002'])
add('resolvelib', 'base-dependency-with-extra', dict(index=[release('a', 1, 'x; extra != "fast"'), release('x', 1)], requirements=['a[fast]']), ['B004'])
add('resolvelib', 'environment-dependency', dict(index=[release('a', 1, 'x; sys_platform == "win32"'), release('x', 1)], requirements=['a'], environment={'sys_platform': 'win32'}), ['B005'])
add('resolvelib', 'false-root-marker', dict(index=[], requirements=['absent; python_version < "3.10"']), ['B005'])
add('resolvelib', 'false-constraint-marker', dict(index=[release('a', 1)], requirements=['a'], constraints=['a>5; sys_platform == "win32"']), ['B003', 'B005'])
add('resolvelib', 'prerelease-disabled', dict(index=[release('a', '2.0rc1'), release('a', '1.0')], requirements=['a']), ['B006'])
add('resolvelib', 'prerelease-enabled', dict(index=[release('a', '2.0rc1'), release('a', '1.0')], requirements=['a'], prereleases=True), ['B006'])
add('resolvelib', 'satisfiable-cycle', dict(index=[release('a', 1, 'b'), release('b', 1, 'a')], requirements=['a']), ['B002'])
add('resolvelib', 'duplicate-release', dict(index=[release('a', '1'), release('A', '1.0')], requirements=['a']), ['B001'], error='ValueError')

def migration(app, name, deps=(), before=()):
    return dict(app=app, name=name, dependencies=list(deps), run_before=list(before))
migrations = [migration('a', '1'), migration('a', '2', [('a', '1')]), migration('b', '1', [('a', '1')]),
              migration('b', '2', [('b', '1'), ('a', '2')]), migration('a', '3', [('a', '2')])]
add('django', 'forward-join', dict(migrations=migrations, applied=[], targets=[['b', '2']]), ['B001', 'B002'], public=True)
add('django', 'rollback-to-applied', dict(migrations=migrations, applied=[['a', '1'], ['a', '2'], ['a', '3'], ['b', '1'], ['b', '2']], targets=[['a', '1']]), ['B003', 'B004'], public=True)
add('django', 'empty-targets', dict(migrations=migrations, applied=[], targets=[]), ['B001'], public=True)
for app in ['a', 'b', 'absent']:
    add('django', 'unapply-' + app, dict(migrations=migrations, applied=[['a', '1'], ['a', '2'], ['b', '1'], ['b', '2']], targets=[[app, None]]), ['B003', 'B004'])
add('django', 'target-does-not-rollback-cross-app-child', dict(migrations=migrations, applied=[['a', '1'], ['b', '1']], targets=[['a', '1']]), ['B003', 'B004'])
add('django', 'mixed-target-order', dict(migrations=migrations, applied=[['a', '1'], ['a', '2']], targets=[['b', '2'], ['a', '1']]), ['B002', 'B003', 'B005'])
add('django', 'duplicate-targets', dict(migrations=migrations, applied=[], targets=[['a', '3'], ['a', '3'], ['b', '2']]), ['B002', 'B005'])
add('django', 'clean-start', dict(migrations=migrations, applied=[['a', '1'], ['a', '2']], targets=[['a', '2']], clean_start=True), ['B006'])
add('django', 'run-before', dict(migrations=[migration('z', '1', before=[('a', '1')]), migration('a', '1')], applied=[], targets=[['a', '1']]), ['B002', 'B004'])
add('django', 'no-implicit-number-edge', dict(migrations=[migration('a', '1'), migration('a', '2')], applied=[], targets=[['a', '2']]), ['B001', 'B002'])
for name, rows, applied, targets in [
    ('missing-parent', [migration('a', '1', [('x', '1')])], [], [['a', '1']]),
    ('cycle', [migration('a', '1', [('a', '2')]), migration('a', '2', [('a', '1')])], [], [['a', '1']]),
    ('unknown-applied', migrations, [['z', '0']], []), ('unknown-target', migrations, [], [['a', 'missing']]),
    ('duplicate-node', [migration('a', '1'), migration('a', '1')], [], [])]:
    add('django', name, dict(migrations=rows, applied=applied, targets=targets), ['B007'], error='ValueError')

START = '2025-01-01T00:00:00+00:00'
def job(name='j', **opts):
    return dict(id=name, trigger=dict(type='interval', seconds=10, start_date=START), **opts)
def poll(seconds):
    return dict(op='poll', now='2025-01-01T00:00:%02d+00:00' % seconds)
add('apscheduler', 'coalesce-before-grace', dict(jobs=[job()], operations=[poll(25), poll(30)], start=START), ['B001', 'B002', 'B003'], public=True)
add('apscheduler', 'all-due-with-grace', dict(jobs=[job(coalesce=False, grace=5)], operations=[poll(25), poll(30)], start=START), ['B002', 'B003'], public=True)
add('apscheduler', 'nothing-due', dict(jobs=[job()], operations=[], start=START), ['B001'], public=True)
add('apscheduler', 'grace-inclusive', dict(jobs=[job(coalesce=False, grace=5)], operations=[poll(5)], start=START), ['B003'])
add('apscheduler', 'unlimited-grace', dict(jobs=[job(coalesce=False, grace=None)], operations=[poll(35), poll(35)], start=START), ['B002', 'B003'])
add('apscheduler', 'pause-resume-skip', dict(jobs=[job(grace=None)], operations=[poll(0), {'op': 'pause', 'id': 'j'}, poll(25), {'op': 'resume', 'id': 'j', 'now': '2025-01-01T00:00:25+00:00'}, poll(30)], start=START), ['B004'])
add('apscheduler', 'date-exhaustion', dict(jobs=[dict(id='once', trigger={'type': 'date', 'run_date': START}, grace=None)], operations=[poll(20), poll(30)], start=START), ['B001', 'B003', 'B005'])
add('apscheduler', 'interval-end-inclusive', dict(jobs=[dict(id='j', trigger={'type': 'interval', 'seconds': 10, 'start_date': START, 'end_date': '2025-01-01T00:00:20+00:00'}, coalesce=False, grace=None)], operations=[poll(20), poll(30)], start=START), ['B005'])
add('apscheduler', 'zero-interval-upstream-one-second', dict(jobs=[dict(id='j', trigger={'type': 'interval', 'seconds': 0}, coalesce=False, grace=None)], operations=[poll(3)], start=START), ['B001', 'B002'])
add('apscheduler', 'tie-job-order', dict(jobs=[job('z', grace=None), job('a', grace=None)], operations=[poll(10)], start=START), ['B002'])
add('apscheduler', 'replace-paused', dict(jobs=[job(paused=True)], operations=[{'op': 'replace', 'job': job(grace=None), 'now': '2025-01-01T00:00:25+00:00'}, poll(30)], start=START), ['B004', 'B006'])
add('apscheduler', 'remove', dict(jobs=[job()], operations=[{'op': 'remove', 'id': 'j'}, poll(30)], start=START), ['B006'])
for kind in ['or']:
    trigger = {'type': kind, 'triggers': [{'type': 'cron', 'second': '*/10'}, {'type': 'cron', 'second': '*/15'}]}
    add('apscheduler', kind + '-cron-combination', dict(jobs=[dict(id='j', trigger=trigger, coalesce=False, grace=None)], operations=[poll(31)], start=START), ['B005', 'B002'])
add('apscheduler', 'timezone-cron', dict(jobs=[dict(id='j', trigger={'type': 'cron', 'timezone': 'Asia/Shanghai', 'hour': 8, 'minute': 0, 'second': '0,30'}, coalesce=False, grace=None)], operations=[poll(31)], start=START), ['B005'])

def task(name, **kwargs):
    return dict(name=name, **kwargs)
add('doit', 'dependency-diamond', dict(tasks=[task('a'), task('b', task_dep=['a']), task('c', task_dep=['a']), task('d', task_dep=['b', 'c'])], selected=['d']), ['B001', 'B002'], public=True)
add('doit', 'file-target-producer', dict(tasks=[task('compile', targets=['x.o']), task('link', file_dep=['x.o'])], selected=['link']), ['B003'], public=True)
add('doit', 'empty-selection', dict(tasks=[task('a')], selected=[]), ['B001'], public=True)
add('doit', 'wildcard-dependencies', dict(tasks=[task('test:a'), task('test:b'), task('all', task_dep=['test:*'])], selected=['all']), ['B002'])
add('doit', 'select-by-target', dict(tasks=[task('compile', targets=['x.o'])], selected=['x.o']), ['B003'])
add('doit', 'select-wildcard', dict(tasks=[task('test:a'), task('test:b'), task('other')], selected=['test:*']), ['B002'])
for status in ['done', 'up-to-date', 'ignore', 'failure']:
    add('doit', 'setup-' + status, dict(tasks=[task('setup'), task('build', setup=['setup'])], selected=['build'], outcomes={'build': {'status': status}}), ['B004', 'B005'])
for status in ['ignore', 'failure']:
    add('doit', 'propagate-' + status, dict(tasks=[task('a'), task('b', task_dep=['a']), task('c', task_dep=['b'])], selected=['c'], outcomes={'a': {'status': status}}), ['B005'])
add('doit', 'calculated-task-dependency', dict(tasks=[task('discover'), task('compile'), task('link', calc_dep=['discover'])], selected=['link'], outcomes={'discover': {'values': {'task_dep': ['compile']}}}), ['B006'])
add('doit', 'calculated-file-dependency', dict(tasks=[task('discover'), task('compile', targets=['x.o']), task('link', calc_dep=['discover'])], selected=['link'], outcomes={'discover': {'values': {'file_dep': ['x.o']}}}), ['B006', 'B003'])
add('doit', 'calculated-recursive-dependency', dict(tasks=[task('first'), task('second'), task('last'), task('build', calc_dep=['first'])], selected=['build'], outcomes={'first': {'values': {'calc_dep': ['second']}}, 'second': {'values': {'task_dep': ['last']}}}), ['B006'])
for name, rows, selected in [('cycle', [task('a', task_dep=['b']), task('b', task_dep=['a'])], ['a']), ('unknown-dependency', [task('a', task_dep=['b'])], ['a']), ('duplicate-target', [task('a', targets=['x']), task('b', targets=['x'])], ['a']), ('unknown-selection', [task('a')], ['bad'])]:
    add('doit', name, dict(tasks=rows, selected=selected), ['B007'], error='ValueError')

LAYERS = [{'values': {'N': 1, 'BOOL': 'false', 'LIST': ['a']}, 'priority': 'default'}, {'values': {'N': 2}, 'priority': 'project'}]
add('scrapy', 'priority-overwrite', dict(layers=LAYERS, operations=[{'op': 'set', 'key': 'N', 'value': 9, 'priority': 'command'}, {'op': 'get', 'key': 'N'}, {'op': 'priority', 'key': 'N'}]), ['B001', 'B002'], public=True)
add('scrapy', 'typed-bool', dict(layers=LAYERS, operations=[{'op': 'get', 'key': 'BOOL', 'kind': 'bool'}]), ['B003'], public=True)
add('scrapy', 'empty-snapshot', dict(layers=[], operations=[{'op': 'snapshot'}]), ['B001'], public=True)
add('scrapy', 'equal-priority-and-delete', dict(layers=LAYERS, operations=[{'op': 'set', 'key': 'N', 'value': 3}, {'op': 'delete', 'key': 'N', 'priority': 19}, {'op': 'get', 'key': 'N'}, {'op': 'delete', 'key': 'N'}, {'op': 'get', 'key': 'N', 'default': 7}]), ['B002'])
for value in ['0', '1', 'true', 'False', 'no', 2]:
    add('scrapy', 'bool-' + str(value), dict(layers=[{'values': {'x': value}}], operations=[{'op': 'get', 'key': 'x', 'kind': 'bool'}]), ['B003'])
add('scrapy', 'typed-collections', dict(layers=[{'values': {'a': 'x,y', 'b': '{"x": 2}', 'c': '2.5'}}], operations=[{'op': 'get', 'key': 'a', 'kind': 'list'}, {'op': 'get', 'key': 'b', 'kind': 'dict'}, {'op': 'get', 'key': 'c', 'kind': 'float'}]), ['B003'])
add('scrapy', 'copy-isolation-and-freeze', dict(layers=LAYERS, operations=[{'op': 'copy', 'target': 'other'}, {'op': 'add', 'store': 'other', 'key': 'LIST', 'value': 'b'}, {'op': 'snapshot'}, {'op': 'snapshot', 'store': 'other'}, {'op': 'freeze'}, {'op': 'set', 'key': 'X', 'value': 1}, {'op': 'snapshot'}]), ['B004', 'B005'])
add('scrapy', 'frozen-copy', dict(layers=LAYERS, operations=[{'op': 'copy', 'target': 'locked', 'frozen': True}, {'op': 'delete', 'store': 'locked', 'key': 'N'}, {'op': 'set', 'key': 'N', 'value': 5}, {'op': 'snapshot', 'store': 'locked'}]), ['B004'])
add('scrapy', 'withbase-merge', dict(layers=[{'values': {'EXT_BASE': {'a': 1, 'b': 2}}, 'priority': 'default'}, {'values': {'EXT': {'b': None, 'c': 3}}, 'priority': 'project'}], operations=[{'op': 'withbase', 'key': 'EXT'}]), ['B006'])
add('scrapy', 'nested-priority', dict(layers=[], operations=[{'op': 'nested', 'key': 'EXT', 'layers': [{'values': {'a': 1}, 'priority': 'default'}, {'values': {'b': 2}, 'priority': 'cmdline'}]}, {'op': 'priority', 'key': 'EXT'}, {'op': 'set', 'key': 'EXT', 'value': {'a': 9}, 'priority': 'project'}, {'op': 'snapshot'}]), ['B006', 'B002'])
add('scrapy', 'setdefault-existing-null', dict(layers=[{'values': {'a': None}}], operations=[{'op': 'setdefault', 'key': 'a', 'value': 3}, {'op': 'setdefault', 'key': 'b', 'value': 4}, {'op': 'snapshot'}]), ['B002'])
add('scrapy', 'list-unique-remove', dict(layers=LAYERS, operations=[{'op': 'add', 'key': 'LIST', 'value': 'a'}, {'op': 'remove', 'key': 'LIST', 'value': 'a'}, {'op': 'remove', 'key': 'LIST', 'value': 'missing'}, {'op': 'snapshot'}]), ['B005'])

SCHEMA = {'low': {'type': 'int', 'default': 0, 'min': 0}, 'high': {'type': 'int', 'default': 10}, 'items': {'type': 'list_int'}}
RULES = [{'field': 'low', 'other': 'high', 'op': 'le'}, {'field': 'high', 'other': 'low', 'op': 'ge'}]
add('traitlets', 'normal-change', dict(schema=SCHEMA, operations=[{'op': 'set', 'field': 'low', 'value': 3}]), ['B001', 'B002'], public=True)
add('traitlets', 'invalid-type', dict(schema=SCHEMA, operations=[{'op': 'set', 'field': 'low', 'value': '3'}]), ['B003'], public=True)
add('traitlets', 'defaults', dict(schema=SCHEMA, operations=[{'op': 'snapshot'}]), ['B001'], public=True)
add('traitlets', 'batch-compress', dict(schema=SCHEMA, operations=[{'op': 'batch', 'updates': [{'field': 'low', 'value': 2}, {'field': 'high', 'value': 20}, {'field': 'low', 'value': 4}]}], rules=RULES), ['B002', 'B004'])
add('traitlets', 'batch-final-validation', dict(schema=SCHEMA, operations=[{'op': 'batch', 'updates': [{'field': 'low', 'value': 15}, {'field': 'high', 'value': 20}]}], rules=RULES), ['B004', 'B005'])
add('traitlets', 'batch-cross-rollback', dict(schema=SCHEMA, operations=[{'op': 'batch', 'updates': [{'field': 'low', 'value': 5}, {'field': 'high', 'value': 2}]}, {'op': 'set', 'field': 'low', 'value': 3}], rules=RULES), ['B004', 'B005'])
add('traitlets', 'batch-type-rollback', dict(schema=SCHEMA, operations=[{'op': 'batch', 'updates': [{'field': 'low', 'value': 2}, {'field': 'high', 'value': 'bad'}]}, {'op': 'snapshot'}]), ['B003', 'B004'])
add('traitlets', 'no-op-assignment', dict(schema=SCHEMA, operations=[{'op': 'set', 'field': 'low', 'value': 0}, {'op': 'batch', 'updates': [{'field': 'low', 'value': 3}, {'field': 'low', 'value': 0}]}]), ['B002', 'B004'])
add('traitlets', 'in-place-list-versus-assignment', dict(schema=SCHEMA, operations=[{'op': 'append', 'field': 'items', 'value': 1}, {'op': 'set', 'field': 'items', 'value': [1, 2]}, {'op': 'set', 'field': 'items', 'value': ['bad']}]), ['B003', 'B006'])
add('traitlets', 'watch-unwatch', dict(schema=SCHEMA, operations=[{'op': 'unwatch', 'fields': ['low']}, {'op': 'set', 'field': 'low', 'value': 2}, {'op': 'watch', 'fields': ['low']}, {'op': 'watch', 'fields': ['low']}, {'op': 'set', 'field': 'low', 'value': 3}]), ['B007'])
add('traitlets', 'bounded-int', dict(schema={'x': {'type': 'int', 'min': 1, 'max': 3, 'default': 1}}, operations=[{'op': 'set', 'field': 'x', 'value': 3}, {'op': 'set', 'field': 'x', 'value': 4}]), ['B003'])
add('traitlets', 'float-text-bool-none', dict(schema={'f': {'type': 'float'}, 's': {'type': 'text', 'allow_none': True}, 'b': {'type': 'bool'}}, operations=[{'op': 'set', 'field': 'f', 'value': 2}, {'op': 'set', 'field': 's', 'value': None}, {'op': 'set', 'field': 'b', 'value': True}, {'op': 'set', 'field': 'b', 'value': 'true'}]), ['B001', 'B003'])
add('traitlets', 'initial-values-before-observation', dict(schema=SCHEMA, initial={'low': 2, 'high': 5}, operations=[{'op': 'set', 'field': 'low', 'value': 4}], rules=RULES), ['B001', 'B005'])

BINDINGS = [{'key': 'config', 'kind': 'value', 'value': {'url': 'local'}}, {'key': 'repo', 'deps': ['config'], 'scope': 'singleton'}, {'key': 'handler', 'deps': ['repo']}]
add('injector', 'singleton-through-transients', dict(bindings=BINDINGS, operations=[{'op': 'get', 'key': 'handler'}, {'op': 'get', 'key': 'handler'}]), ['B001', 'B002'], public=True)
add('injector', 'missing-key', dict(bindings=[], operations=[{'op': 'get', 'key': 'missing'}]), ['B006'], public=True)
add('injector', 'value-binding', dict(bindings=BINDINGS, operations=[{'op': 'get', 'key': 'config'}]), ['B001'], public=True)
add('injector', 'singleton-identity', dict(bindings=BINDINGS, operations=[{'op': 'get', 'key': 'repo', 'save': 'a'}, {'op': 'get', 'key': 'repo', 'save': 'b'}, {'op': 'same', 'left': 'a', 'right': 'b'}]), ['B002'])
add('injector', 'transient-identity', dict(bindings=BINDINGS, operations=[{'op': 'get', 'key': 'handler', 'save': 'a'}, {'op': 'get', 'key': 'handler', 'save': 'b'}, {'op': 'same', 'left': 'a', 'right': 'b'}]), ['B002'])
add('injector', 'child-inherited-singleton', dict(bindings=BINDINGS, operations=[{'op': 'child', 'name': 'child', 'bindings': [{'key': 'config', 'kind': 'value', 'value': 'child'}]}, {'op': 'get', 'key': 'repo', 'container': 'child', 'save': 'a'}, {'op': 'get', 'key': 'repo', 'save': 'b'}, {'op': 'same', 'left': 'a', 'right': 'b'}]), ['B003', 'B002'])
add('injector', 'child-explicit-singleton', dict(bindings=BINDINGS, operations=[{'op': 'child', 'name': 'child', 'bindings': [{'key': 'repo', 'deps': ['config'], 'scope': 'singleton'}, {'key': 'config', 'kind': 'value', 'value': 'child'}]}, {'op': 'get', 'key': 'repo', 'container': 'child'}, {'op': 'get', 'key': 'repo'}]), ['B003'])
add('injector', 'parent-missing-child-satisfies', dict(bindings=[{'key': 'repo', 'deps': ['config'], 'scope': 'singleton'}], operations=[{'op': 'child', 'name': 'child', 'bindings': [{'key': 'config', 'kind': 'value', 'value': 5}]}, {'op': 'get', 'key': 'repo', 'container': 'child'}, {'op': 'get', 'key': 'repo'}]), ['B003', 'B006'])
add('injector', 'rebind-cached-singleton', dict(bindings=BINDINGS, operations=[{'op': 'get', 'key': 'repo'}, {'op': 'bind', 'binding': {'key': 'repo', 'kind': 'value', 'value': 'new', 'scope': 'singleton'}}, {'op': 'get', 'key': 'repo'}]), ['B004'])
add('injector', 'rebind-before-first-get', dict(bindings=BINDINGS, operations=[{'op': 'bind', 'binding': {'key': 'config', 'kind': 'value', 'value': 'new'}}, {'op': 'get', 'key': 'repo'}]), ['B004'])
add('injector', 'cycle-and-recovery', dict(bindings=[{'key': 'a', 'deps': ['b']}, {'key': 'b', 'deps': ['a']}], operations=[{'op': 'get', 'key': 'a'}, {'op': 'bind', 'binding': {'key': 'b', 'kind': 'value', 'value': 1}}, {'op': 'get', 'key': 'a'}]), ['B005', 'B004'])
add('injector', 'failed-singleton-not-cached', dict(bindings=[{'key': 'a', 'fail': True, 'scope': 'singleton'}], operations=[{'op': 'get', 'key': 'a'}, {'op': 'bind', 'binding': {'key': 'a', 'scope': 'singleton'}}, {'op': 'get', 'key': 'a'}]), ['B005'])
add('injector', 'multiple-dependencies-construction-order', dict(bindings=[{'key': 'a'}, {'key': 'b'}, {'key': 'c', 'deps': ['b', 'a', 'b']}], operations=[{'op': 'get', 'key': 'c'}]), ['B001', 'B002'])

def sig(name, **kwargs):
    return dict(task=name, **kwargs)
add('celery', 'partial-clone', dict(spec=sig('add', args=[2], kwargs={'x': 1}), operations=[{'op': 'clone', 'target': 'copy', 'args': [1], 'kwargs': {'x': 3}}, {'op': 'snapshot'}]), ['B001', 'B002'], public=True)
add('celery', 'immutable-partial', dict(spec=sig('add', args=[2], immutable=True), operations=[{'op': 'clone', 'target': 'copy', 'args': [1], 'options': {'queue': 'q'}}]), ['B002', 'B003'], public=True)
add('celery', 'empty-group', dict(spec={'kind': 'group', 'tasks': []}, operations=[{'op': 'snapshot'}]), ['B001'], public=True)
add('celery', 'stamp-protects-clone-options', dict(spec=sig('a'), operations=[{'op': 'stamp', 'headers': {'tenant': 'x'}}, {'op': 'clone', 'target': 'copy', 'options': {'tenant': 'y', 'queue': 'q', 'group_id': 'g'}}]), ['B003', 'B004'])
for append in [False, True]:
    add('celery', 'duplicate-stamps-' + str(append), dict(spec=sig('a'), operations=[{'op': 'stamp', 'headers': {'tenant': 'x'}}, {'op': 'stamp', 'headers': {'tenant': 'y', 'batch': [1, 2]}, 'append': append}]), ['B004'])
add('celery', 'visitor-overrides', dict(spec={'kind': 'group', 'tasks': [sig('a'), sig('b')]}, operations=[{'op': 'stamp', 'headers': {'tenant': 'base'}, 'visitor': {'group': {'group_tag': 1}, 'tasks': {'a': {'tenant': 'special'}}}}]), ['B004', 'B005'])
add('celery', 'chord-header-body-stamps', dict(spec={'kind': 'chord', 'header': [sig('a'), sig('b')], 'body': sig('sum')}, operations=[{'op': 'stamp', 'headers': {'tenant': 't'}, 'visitor': {'chord_header': {'side': 'header'}, 'chord_body': {'side': 'body'}}}]), ['B005'])
add('celery', 'nested-chain-group-stamps', dict(spec={'kind': 'chain', 'tasks': [sig('a'), {'kind': 'group', 'tasks': [sig('b'), sig('c')]}]}, operations=[{'op': 'stamp', 'headers': {'x': 1}}, {'op': 'clone', 'target': 'copy'}, {'op': 'stamp', 'store': 'copy', 'headers': {'x': 2}, 'append': True}]), ['B001', 'B002', 'B005'])
add('celery', 'link-deduplication', dict(spec=sig('a'), operations=[{'op': 'link', 'signature': sig('b')}, {'op': 'link', 'signature': sig('b')}, {'op': 'errback', 'signature': sig('e')}, {'op': 'stamp', 'headers': {'tenant': 't'}}]), ['B006', 'B004'])
add('celery', 'clone-link-independence', dict(spec=sig('a', links=[sig('b')]), operations=[{'op': 'clone', 'target': 'copy'}, {'op': 'link', 'store': 'copy', 'signature': sig('c')}, {'op': 'snapshot'}]), ['B002', 'B006'])
add('celery', 'group-immutable-propagation', dict(spec={'kind': 'group', 'tasks': [sig('a'), sig('b')]}, operations=[{'op': 'immutable', 'value': True}, {'op': 'clone', 'target': 'copy', 'args': [9]}]), ['B003'])
add('celery', 'chain-link-placement', dict(spec={'kind': 'chain', 'tasks': [sig('a'), sig('b')]}, operations=[{'op': 'link', 'signature': sig('c')}, {'op': 'errback', 'signature': sig('e')}, {'op': 'clone', 'target': 'copy'}]), ['B006', 'B002'])
add('celery', 'group-id-immutable', dict(spec=sig('a', options={'group_id': 'original', 'queue': 'old'}), operations=[{'op': 'clone', 'target': 'copy', 'options': {'group_id': 'new', 'queue': 'new'}}]), ['B003'])

# State-machine suites use actual callbacks, guards and event queues, not sleeps.
HSTATES = ['idle', {'name': 'work', 'initial': 'ready', 'children': ['ready', 'busy']}, 'done']
HTRANS = [{'trigger': 'start', 'source': 'idle', 'dest': 'work'}, {'trigger': 'run', 'source': 'work_ready', 'dest': 'work_busy', 'conditions': 'permitted'}, {'trigger': 'finish', 'source': 'work', 'dest': 'done'}]
add('transitions', 'nested-initial', dict(states=HSTATES, transitions=HTRANS, operations=[{'op': 'event', 'event': 'start'}], initial='idle'), ['B001'], public=True)
add('transitions', 'guard-false', dict(states=HSTATES, transitions=HTRANS, operations=[{'op': 'event', 'event': 'run'}], initial='work'), ['B002'], public=True)
add('transitions', 'unknown-event', dict(states=HSTATES, transitions=HTRANS, operations=[{'op': 'event', 'event': 'unknown'}], initial='idle'), ['B006'], public=True)
add('transitions', 'parent-event-in-child', dict(states=HSTATES, transitions=HTRANS, operations=[{'op': 'set', 'values': {'permitted': True}}, {'op': 'event', 'event': 'run'}, {'op': 'event', 'event': 'finish'}], initial='work'), ['B001', 'B002'])
add('transitions', 'invalid-state-event', dict(states=HSTATES, transitions=HTRANS, operations=[{'op': 'event', 'event': 'run'}, {'op': 'event', 'event': 'start'}], initial='idle'), ['B006'])
for queued in [False, True]:
    rows = [{'trigger': 'go', 'source': 'a', 'dest': 'b', 'before': 'pre', 'after': 'post'}, {'trigger': 'next', 'source': 'b', 'dest': 'c', 'before': 'nextpre'}]
    add('transitions', 'reentrant-' + str(queued), dict(states=['a', {'name': 'b', 'on_enter': 'entered'}, 'c'], transitions=rows, operations=[{'op': 'event', 'event': 'go'}], initial='a', queued=queued, callbacks={'pre': [], 'post': [], 'nextpre': [], 'entered': [{'op': 'emit', 'event': 'next'}]}), ['B003', 'B004'])
add('transitions', 'internal-versus-self', dict(states=[{'name': 'a', 'on_enter': 'enter', 'on_exit': 'exit'}], transitions=[{'trigger': 'inside', 'source': 'a', 'dest': None, 'before': 'pre', 'after': 'post'}, {'trigger': 'self', 'source': 'a', 'dest': 'a'}], operations=[{'op': 'event', 'event': 'inside'}, {'op': 'event', 'event': 'self'}], initial='a', callbacks={k: [] for k in ['enter', 'exit', 'pre', 'post']}), ['B003'])
add('transitions', 'ordered-guard-fallback', dict(states=['a', 'b', 'c'], transitions=[{'trigger': 'go', 'source': 'a', 'dest': 'b', 'conditions': 'first'}, {'trigger': 'go', 'source': 'a', 'dest': 'c', 'unless': 'blocked'}], operations=[{'op': 'event', 'event': 'go'}], initial='a'), ['B002'])
add('transitions', 'parallel-regions', dict(states=['idle', {'name': 'active', 'parallel': [{'name': 'left', 'initial': 'x', 'children': ['x', 'y']}, {'name': 'right', 'initial': 'x', 'children': ['x', 'y']}]}], transitions=[{'trigger': 'start', 'source': 'idle', 'dest': 'active'}, {'trigger': 'tick', 'source': 'active_left_x', 'dest': 'active_left_y'}, {'trigger': 'tick', 'source': 'active_right_x', 'dest': 'active_right_y'}], operations=[{'op': 'event', 'event': 'start'}, {'op': 'event', 'event': 'tick'}], initial='idle'), ['B005'])
add('transitions', 'callback-error-recovery', dict(states=['a', 'b'], transitions=[{'trigger': 'fail', 'source': 'a', 'dest': 'b', 'before': 'broken'}, {'trigger': 'go', 'source': 'a', 'dest': 'b'}], operations=[{'op': 'event', 'event': 'fail'}, {'op': 'event', 'event': 'go'}], initial='a', queued=True, callbacks={'broken': [{'op': 'raise'}]}), ['B006', 'B004'])
add('transitions', 'child-transition-before-parent', dict(states=HSTATES, transitions=HTRANS + [{'trigger': 'finish', 'source': 'work_ready', 'dest': 'work_busy'}], operations=[{'op': 'event', 'event': 'finish'}, {'op': 'event', 'event': 'finish'}], initial='work'), ['B001'])

STATES = ['a', 'b', {'name': 'c', 'final': True}]
TRANS = [{'event': 'go', 'source': 'a', 'target': 'b', 'cond': 'allowed'}, {'event': 'finish', 'source': 'b', 'target': 'c'}]
add('statemachine', 'initial-and-go', dict(states=STATES, transitions=TRANS, operations=[{'op': 'event', 'event': 'go'}], initial='a', context={'allowed': True}), ['B001', 'B002'], public=True)
add('statemachine', 'guard-refusal', dict(states=STATES, transitions=TRANS, operations=[{'op': 'event', 'event': 'go'}], initial='a'), ['B002'], public=True)
add('statemachine', 'tolerant-event', dict(states=STATES, transitions=TRANS, operations=[{'op': 'event', 'event': 'finish'}], initial='a', allow_empty=True), ['B006'], public=True)
for rtc in [False, True]:
    add('statemachine', 'reentrant-' + str(rtc), dict(states=['a', {'name': 'b', 'enter': 'entered'}, {'name': 'c', 'final': True}], transitions=[{'event': 'go', 'source': 'a', 'target': 'b', 'before': 'pre', 'after': 'post'}, {'event': 'finish', 'source': 'b', 'target': 'c', 'before': 'last'}], operations=[{'op': 'event', 'event': 'go'}], initial='a', rtc=rtc, callbacks={'pre': [], 'post': [], 'last': [], 'entered': [{'op': 'emit', 'event': 'finish'}]}), ['B003', 'B004'])
add('statemachine', 'initial-entry-visible', dict(states=[{'name': 'a', 'enter': 'init'}, {'name': 'b', 'final': True}], transitions=[{'event': 'go', 'source': 'a', 'target': 'b'}], operations=[], initial='a', callbacks={'init': [{'op': 'set', 'key': 'ready', 'value': True}]}), ['B001', 'B003'])
add('statemachine', 'internal-versus-self', dict(states=[{'name': 'a', 'enter': 'enter', 'exit': 'exit'}, {'name': 'b', 'final': True}], transitions=[{'event': 'inside', 'source': 'a', 'target': 'a', 'internal': True, 'before': 'pre', 'on': 'on', 'after': 'post'}, {'event': 'self', 'source': 'a', 'target': 'a'}, {'event': 'end', 'source': 'a', 'target': 'b'}], operations=[{'op': 'event', 'event': 'inside'}, {'op': 'event', 'event': 'self'}], initial='a', callbacks={k: [] for k in ['enter', 'exit', 'pre', 'on', 'post']}), ['B003'])
add('statemachine', 'guard-fallback', dict(states=['a', 'b', {'name': 'c', 'final': True}], transitions=[{'event': 'go', 'source': 'a', 'target': 'b', 'cond': 'first'}, {'event': 'go', 'source': 'a', 'target': 'c', 'unless': 'blocked'}, {'event': 'end', 'source': 'b', 'target': 'c'}], operations=[{'op': 'event', 'event': 'go'}], initial='a'), ['B002'])
add('statemachine', 'before-failure-state-retained', dict(states=['a', {'name': 'b', 'final': True}], transitions=[{'event': 'fail', 'source': 'a', 'target': 'b', 'before': 'bad'}, {'event': 'go', 'source': 'a', 'target': 'b'}], operations=[{'op': 'event', 'event': 'fail'}, {'op': 'event', 'event': 'go'}], initial='a', callbacks={'bad': [{'op': 'raise'}]}), ['B005'])
add('statemachine', 'entry-failure-state-changed', dict(states=['a', {'name': 'b', 'enter': 'bad'}, {'name': 'c', 'final': True}], transitions=[{'event': 'go', 'source': 'a', 'target': 'b'}, {'event': 'end', 'source': 'b', 'target': 'c'}], operations=[{'op': 'event', 'event': 'go'}, {'op': 'event', 'event': 'end'}], initial='a', callbacks={'bad': [{'op': 'raise'}]}), ['B005'])
add('statemachine', 'queue-cleared-on-error', dict(states=['a', 'b', {'name': 'c', 'final': True}], transitions=[{'event': 'go', 'source': 'a', 'target': 'b', 'after': 'bad'}, {'event': 'end', 'source': 'b', 'target': 'c'}], operations=[{'op': 'event', 'event': 'go'}, {'op': 'snapshot'}, {'op': 'event', 'event': 'end'}], initial='a', callbacks={'bad': [{'op': 'emit', 'event': 'end'}, {'op': 'raise'}]}), ['B004', 'B005'])
add('statemachine', 'guard-update-between-events', dict(states=STATES, transitions=TRANS, operations=[{'op': 'event', 'event': 'go'}, {'op': 'set', 'values': {'allowed': True}}, {'op': 'event', 'event': 'go'}, {'op': 'event', 'event': 'finish'}, {'op': 'event', 'event': 'go'}], initial='a'), ['B002', 'B006'])
