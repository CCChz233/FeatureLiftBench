"""Acquire full upstream trees; freeze exact commits before authoring tasks."""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / 'benchmark/sources/workflow_hard10'
SOURCES = {
    'resolvelib': 'sarugaku/resolvelib',
    'injector': 'python-injector/injector',
    'statemachine': 'fgmacedo/python-statemachine',
    'doit': 'pydoit/doit',
    'celery': 'celery/celery',
    'django': 'django/django',
    'apscheduler': 'agronholm/apscheduler',
    'scrapy': 'scrapy/scrapy',
    'traitlets': 'ipython/traitlets',
    'transitions': 'pytransitions/transitions',
}
# Stable supported source lines; actual immutable commit is obtained from Git.
REFS = {'resolvelib': '1.2.1', 'injector': '0.22.0', 'statemachine': 'v2.5.0',
        'doit': '0.36.0', 'celery': 'v5.5.3', 'django': '5.2.6',
        'apscheduler': '3.11.0', 'scrapy': '2.13.3',
        'traitlets': 'v5.14.3', 'transitions': '0.9.3'}

def acquire(item):
    name, repo = item
    checkout = BASE / 'checkouts' / name
    url = 'https://github.com/' + repo
    if not (checkout / '.git').is_dir():
        checkout.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--depth', '1',
                        '--branch', REFS[name], url, str(checkout)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=420)
    commit = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
    licenses = [p for p in checkout.iterdir() if p.is_file() and p.name.upper().startswith(('LICENSE', 'COPYING'))]
    record = dict(name=name, url=url, requested_ref=REFS[name], commit=commit,
                  checkout=checkout.relative_to(ROOT).as_posix(), license_candidates=[p.name for p in licenses])
    print(json.dumps(record), flush=True)
    return record

if __name__ == '__main__':
    records, failures = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {name: pool.submit(acquire, (name, repo)) for name, repo in SOURCES.items()}
        for name, future in futures.items():
            try:
                records.append(future.result())
            except Exception as exc:
                failures.append(dict(name=name, error=str(exc)))
    (HERE / 'acquisition.json').write_text(json.dumps(dict(sources=records, failures=failures), indent=2) + '\n', encoding='utf-8')
    if failures:
        print(json.dumps(failures))
        raise SystemExit(1)
