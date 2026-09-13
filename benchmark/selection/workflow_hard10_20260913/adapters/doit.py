from copy import deepcopy
from collections import deque
from doit.task import Task
from doit.control import TaskControl
from doit.exceptions import InvalidTask, InvalidCommand, InvalidDodoFile


def dispatch_tasks(tasks, selected, *, outcomes=None):
    outcomes = outcomes or {}
    records = deepcopy(tasks)
    allowed = ('task_dep', 'file_dep', 'targets', 'setup', 'calc_dep')
    objects = [Task(r['name'], [], **{k: r[k] for k in allowed if k in r}) for r in records]
    try:
        control = TaskControl(objects)
        control.process(list(selected))
        dispatcher = control.task_dispatcher()
        class StableReady(deque):
            def popleft(self):
                node = min(self, key=lambda n: n.task.name)
                self.remove(node)
                return node
        # A record planner needs reproducible ties across processes. Native
        # waiting sets have no order; only simultaneously ready ties change.
        dispatcher.ready = StableReady(dispatcher.ready)
        generator = dispatcher.generator
        processed = None
        trace = []
        for _ in range(10000):
            try:
                node = generator.send(processed)
            except StopIteration:
                break
            if node == 'hold on':
                raise ValueError('unresolved dispatcher wait')
            task = node.task
            choice = outcomes.get(task.name, {})
            if node.bad_deps:
                status = 'failure'
            elif node.ignored_deps:
                status = 'ignore'
            else:
                status = choice.get('status', 'done')
            if task.setup_tasks and node.run_status is None and status == 'done':
                node.run_status = 'run'
                phase = 'select'
            else:
                node.run_status = status
                phase = 'complete'
                if status == 'done':
                    task.values = deepcopy(choice.get('values', {}))
            trace.append({'name': task.name, 'phase': phase, 'status': node.run_status,
                          'bad_deps': sorted(n.task.name for n in node.bad_deps),
                          'ignored_deps': sorted(n.task.name for n in node.ignored_deps),
                          'task_dep': list(task.task_dep)})
            processed = node
        else:
            raise ValueError('dispatcher did not converge')
        return trace
    except (InvalidTask, InvalidCommand, InvalidDodoFile) as exc:
        raise ValueError('invalid task graph') from exc
