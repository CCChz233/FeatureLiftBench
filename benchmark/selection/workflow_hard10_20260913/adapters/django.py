from types import SimpleNamespace
from django.db.migrations.graph import MigrationGraph
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.exceptions import CircularDependencyError, NodeNotFoundError


def plan_migrations(migrations, applied, targets, *, clean_start=False):
    graph = MigrationGraph()
    keys = [(r['app'], r['name']) for r in migrations]
    if len(set(keys)) != len(keys):
        raise ValueError('duplicate migration')
    for key in keys:
        graph.add_node(key, key)
    try:
        for row, key in zip(migrations, keys):
            for dependency in row.get('dependencies', []):
                graph.add_dependency(key, key, tuple(dependency), skip_validation=True)
            for later in row.get('run_before', []):
                graph.add_dependency(key, tuple(later), key, skip_validation=True)
        graph.validate_consistency()
        graph.ensure_not_cyclic()
        selected = [tuple(t) for t in targets]
        applied_set = {tuple(t) for t in applied}
        if any(k not in graph.nodes for k in applied_set):
            raise ValueError('unknown applied migration')
        if any(k[1] is not None and k not in graph.nodes for k in selected):
            raise ValueError('unknown target')
        runner = MigrationExecutor.__new__(MigrationExecutor)
        runner.loader = SimpleNamespace(graph=graph, applied_migrations=dict.fromkeys(applied_set), replace_migrations=False)
        plan = runner.migration_plan(selected, clean_start=clean_start)
        return [{'app': key[0], 'name': key[1], 'backwards': backwards} for key, backwards in plan]
    except (CircularDependencyError, NodeNotFoundError) as exc:
        raise ValueError('invalid migration graph') from exc
