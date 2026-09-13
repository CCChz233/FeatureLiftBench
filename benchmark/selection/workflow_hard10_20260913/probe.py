"""Run authored cases against pinned native source or an isolated reference.

Native probes generate fixtures; reference probes never regenerate expectations.
"""
import argparse
from copy import deepcopy
import importlib
import importlib.util
import json
from pathlib import Path
import socket
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from cases import CASES
from lift_references import PACKAGES
APIS = dict(resolvelib='resolve_dependencies', django='plan_migrations', apscheduler='schedule_runs',
            doit='dispatch_tasks', scrapy='settings_trace', traitlets='model_trace',
            injector='container_trace', celery='canvas_trace', transitions='hierarchy_trace', statemachine='events_trace')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', choices=APIS)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    def deny(*a, **kw):
        raise RuntimeError('network disabled in source probe')
    socket.create_connection = deny
    socket.socket.connect = deny
    if args.reference:
        sys.path.insert(0, str(args.reference.resolve()))
        module = importlib.import_module('featurelifted')
        assert Path(module.__file__).resolve().is_relative_to(args.reference.resolve())
        fixtures = json.loads((HERE / 'fixtures' / (args.source + '.json')).read_text(encoding='utf-8'))
    else:
        source_root = ROOT / 'benchmark/sources/workflow_hard10/checkouts' / args.source
        sys.path.insert(0, str((source_root / PACKAGES[args.source]).parent))
        spec = importlib.util.spec_from_file_location('_hard10_adapter', HERE / 'adapters' / (args.source + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        upstream = importlib.import_module(args.source)
        assert Path(upstream.__file__).resolve().is_relative_to(source_root.resolve()), upstream.__file__
        fixtures = deepcopy(CASES[args.source])
    failures = []
    for case in fixtures:
        arguments = deepcopy(case['args'])
        try:
            actual = getattr(module, APIS[args.source])(**arguments)
            actual = json.loads(json.dumps(actual))
            assert arguments == case['args'], 'adapter mutated input'
            assert case['error'] is None, 'expected error: ' + str(case['error'])
            if args.reference:
                assert actual == case['expected'], 'reference differs from pinned source fixture'
            else:
                case['expected'] = actual
        except Exception as exc:
            if type(exc).__name__ == case['error']:
                case['expected'] = None
            else:
                failures.append(dict(name=case['name'], error=repr(exc), traceback=traceback.format_exc()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(source=args.source, native=not bool(args.reference), cases=len(fixtures), failures=failures), indent=2) + '\n', encoding='utf-8')
    if not args.reference and not failures:
        path = HERE / 'fixtures' / (args.source + '.json')
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(source=args.source, cases=len(fixtures), failures=[(f['name'], f['error']) for f in failures])))
    return bool(failures)

if __name__ == '__main__':
    raise SystemExit(main())
