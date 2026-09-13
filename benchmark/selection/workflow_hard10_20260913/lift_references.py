"""Source-derived references. Pruning is for submissions, never agent source trees."""
import ast
import json
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TREES = ROOT / 'benchmark/sources/workflow_hard10/checkouts'
PACKAGES = {'resolvelib': 'src/resolvelib', 'injector': 'injector',
            'statemachine': 'statemachine', 'doit': 'doit', 'celery': 'celery',
            'django': 'django', 'apscheduler': 'src/apscheduler', 'scrapy': 'scrapy',
            'traitlets': 'traitlets', 'transitions': 'transitions'}

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')

def rewrite(text, package):
    # Preserve local variable names. A blind token replacement can turn
    # `celery = ...` into invalid Python, or change task identity strings.
    tree = ast.parse(text)
    class Rewrite(ast.NodeTransformer):
        def visit_ImportFrom(self, node):
            if node.level == 0 and node.module and (node.module == package or node.module.startswith(package + '.')):
                node.module = 'featurelifted._engine' + node.module[len(package):]
            return node
        def visit_Import(self, node):
            result = []
            for alias in node.names:
                if alias.name == package or alias.name.startswith(package + '.'):
                    original = alias.name
                    alias.name = 'featurelifted._engine' + original[len(package):]
                    if alias.asname is None:
                        if original == package:
                            alias.asname = package
                        else:
                            result.append(ast.Import(names=[ast.alias(name='featurelifted._engine', asname=package)]))
                    result.append(ast.Import(names=[alias]))
                else:
                    result.append(ast.Import(names=[alias]))
            return result
    tree = Rewrite().visit(tree)
    # Dynamic import strings are rewritten only for the framework that uses
    # them extensively. Canvas task names (celery.chain/group/chord) are data.
    if package == 'celery':
        class Strings(ast.NodeTransformer):
            def visit_Constant(self, node):
                if isinstance(node.value, str) and (node.value == 'celery' or node.value.startswith('celery.')) and node.value not in {'celery.chain', 'celery.group', 'celery.chord', 'celery.map', 'celery.starmap', 'celery.chunks', 'celery.accumulate', 'celery.backend_cleanup'}:
                    node.value = 'featurelifted._engine' + node.value[len('celery'):]
                return node
        tree = Strings().visit(tree)
    return ast.unparse(ast.fix_missing_locations(tree)) + '\n'

def selected_class(code, name, methods=None):
    node = next(n for n in ast.parse(code).body if isinstance(n, ast.ClassDef) and n.name == name)
    if methods is not None:
        node.body = [n for n in node.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) or n.name in methods]
    return ast.unparse(node) + '\n'

def build(name, output, *, full_copy=False):
    source = TREES / name
    package = source / PACKAGES[name]
    dest = output / 'featurelifted'
    dest.mkdir(parents=True, exist_ok=True)
    used = []
    if name == 'django' and not full_copy:
        graph = (package / 'db/migrations/graph.py').read_text(encoding='utf-8')
        graph = graph.replace('from django.db.migrations.state import ProjectState\n', '')
        graph = graph.replace('from .exceptions import CircularDependencyError, NodeNotFoundError', 'from .exceptions import CircularDependencyError, NodeNotFoundError')
        tree = ast.parse(graph)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == 'MigrationGraph':
                node.body = [n for n in node.body if not isinstance(n, ast.FunctionDef) or n.name not in {'make_state'}]
        write(dest / '_engine/db/migrations/graph.py', ast.unparse(tree) + '\n')
        executor = (package / 'db/migrations/executor.py').read_text(encoding='utf-8')
        write(dest / '_engine/db/migrations/executor.py', selected_class(executor, 'MigrationExecutor', {'migration_plan'}))
        errors = (package / 'db/migrations/exceptions.py').read_text(encoding='utf-8')
        write(dest / '_engine/db/migrations/exceptions.py', selected_class(errors, 'CircularDependencyError') + selected_class(errors, 'NodeNotFoundError'))
        for directory in ['_engine', '_engine/db', '_engine/db/migrations']:
            write(dest / directory / '__init__.py', '')
        used = ['django/db/migrations/graph.py', 'django/db/migrations/executor.py', 'django/db/migrations/exceptions.py']
    elif name == 'scrapy' and not full_copy:
        code = (package / 'settings/__init__.py').read_text(encoding='utf-8')
        code = code[:code.index('\nclass Settings(BaseSettings):')]
        code = code.replace('from scrapy.settings import default_settings\n', '').replace('from scrapy.utils.misc import load_object\n', '')
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == 'BaseSettings':
                node.body = [n for n in node.body if not isinstance(n, ast.FunctionDef) or n.name not in {'setmodule', 'replace_in_component_priority_dict', 'set_in_component_priority_dict', 'setdefault_in_component_priority_dict'}]
        write(dest / '_engine/settings/__init__.py', ast.unparse(tree) + '\n')
        write(dest / '_engine/__init__.py', '')
        used = ['scrapy/settings/__init__.py']
    elif name == 'celery' and not full_copy:
        canvas = ast.parse((package / 'canvas.py').read_text(encoding='utf-8'))
        removed = {'__call__', 'delay', 'apply', 'apply_async', 'freeze', '__invert__',
                   'run', 'prepare_steps', '_freeze_group_tasks', '_freeze_tasks',
                   '_prepared', '_apply_tasks', '_freeze_gid', '_freeze_unroll',
                   '_freeze_tasks', '_get_task_names', '_failed_join_report'}
        body = []
        for node in canvas.body:
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('celery'):
                continue
            if isinstance(node, ast.ClassDef):
                node.body = [n for n in node.body if not isinstance(n, ast.FunctionDef) or n.name not in removed]
                node.body = [n for n in node.body if not (isinstance(n, ast.Assign) and isinstance(n.value, ast.Name) and n.value.id in removed)]
            body.append(node)
        helpers = '''from types import SimpleNamespace
from collections import UserList
from itertools import islice, tee, zip_longest
from vine import promise
from kombu.utils.functional import is_list, maybe_list
class CallableSignature(metaclass=ABCMeta):
    pass
abstract = SimpleNamespace(CallableSignature=CallableSignature)
current_app = None
class Celery:
    def __init__(self, *args, **kwargs):
        self.conf = SimpleNamespace(task_protocol=2)
'''
        functional = ast.parse((package / 'utils/functional.py').read_text(encoding='utf-8'))
        selected = {'_regen', 'regen', 'seq_concat_item', 'seq_concat_seq', 'chunks'}
        for node in functional.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in selected:
                helpers += ast.unparse(node) + '\n'
        helpers += '_chunks = chunks\n'
        helpers += selected_class((package / 'utils/objects.py').read_text(encoding='utf-8'), 'getitem_property')
        text_tree = ast.parse((package / 'utils/text.py').read_text(encoding='utf-8'))
        for node in text_tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in {'remove_repeating_from_task', 'remove_repeating', 'truncate'}:
                helpers += ast.unparse(node) + '\n'
        # Helpers need the retained standard-library imports (not app boot).
        imports = [n for n in body if isinstance(n, (ast.Import, ast.ImportFrom))]
        remainder = [n for n in body if not isinstance(n, (ast.Import, ast.ImportFrom))]
        text = '\n'.join(ast.unparse(n) for n in imports) + '\n' + helpers + '\n' + '\n'.join(ast.unparse(n) for n in remainder)
        write(dest / '_engine/canvas.py', text + '\n')
        write(dest / '_engine/__init__.py', 'from .canvas import Celery\n')
        used = ['celery/canvas.py', 'celery/utils/functional.py', 'celery/utils/objects.py', 'celery/utils/text.py']
    else:
        for file in package.rglob('*'):
            if not file.is_file() or any(p in {'__pycache__', 'tests'} for p in file.relative_to(package).parts):
                continue
            if file.suffix in {'.pyc', '.pyo'}:
                continue
            rel = file.relative_to(package)
            if not full_copy:
                if name == 'transitions' and rel.as_posix() not in {'__init__.py', 'core.py', 'version.py', 'extensions/nesting.py'}:
                    continue
                if name == 'traitlets' and rel.parts[0] not in {'__init__.py', 'traitlets.py', '_version.py', 'utils'}:
                    continue
                if name == 'apscheduler' and rel.parts[0] not in {'__init__.py', 'util.py', 'job.py', 'triggers'}:
                    continue
                if name == 'statemachine' and rel.parts[0] in {'contrib'}:
                    continue
            target = dest / '_engine' / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if file.suffix == '.py':
                write(target, rewrite(file.read_text(encoding='utf-8'), name))
                used.append(file.relative_to(source).as_posix())
            else:
                shutil.copyfile(file, target)
        if name == 'transitions' and not full_copy:
            write(dest / '_engine/extensions/__init__.py', '')
        if name == 'doit' and not full_copy:
            write(dest / '_engine/__init__.py', '__version__ = (0, 36, 0)\n')
        if name == 'apscheduler' and not full_copy:
            write(dest / '_engine/__init__.py', '__version__ = "3.11.0"\nversion = "3.11.0"\n')
    adapter = (HERE / 'adapters' / (name + '.py')).read_text(encoding='utf-8')
    write(dest / '__init__.py', rewrite(adapter, name))
    evidence = next(s for s in json.loads((HERE / 'source_evidence.json').read_text(encoding='utf-8')) if s['name'] == name)
    shutil.copyfile(source / evidence['license_path'], dest / 'UPSTREAM_LICENSE')
    write(output / 'pyproject.toml', '[build-system]\nrequires = ["setuptools>=68"]\nbuild-backend = "setuptools.build_meta"\n[project]\nname = "featurelifted"\nversion = "0.1.0"\nrequires-python = ">=3.12"\n[tool.setuptools.packages.find]\ninclude = ["featurelifted*"]\n')
    return used
