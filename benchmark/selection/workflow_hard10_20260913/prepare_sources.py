"""Re-use the audited exact-Git-blob archiver for this separately named batch."""
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
old = ROOT / 'benchmark/selection/workflow_hard_pilot_20260912/prepare_sources.py'
code = old.read_text(encoding='utf-8').replace('workflow_hard_pilot', 'workflow_hard10').replace('workflow-pilot-', 'workflow-hard10-')
namespace = {'__file__': str(HERE / 'prepare_sources.py'), '__name__': 'hard10_archiver'}
exec(compile(code, str(old), 'exec'), namespace)

def extract_development_tree(archive, target):
    # Avoid Windows directory-rename locks. The canonical archive is unchanged;
    # runtime Main still uses the harness extractor and verifies its digest.
    base = (ROOT / 'benchmark/sources/workflow_hard10/trees').resolve()
    target = target.resolve()
    if not target.is_relative_to(base):
        raise ValueError('Unexpected extraction destination')
    with tarfile.open(archive, 'r:gz') as tf:
        for member in tf:
            path = target / member.name
            if not path.resolve().is_relative_to(target):
                raise ValueError('Unsafe archive path')
            if member.issym():
                if not (path.parent / member.linkname).resolve().is_relative_to(target):
                    raise ValueError('Unsafe symlink target')
                path.parent.mkdir(parents=True, exist_ok=True)
                # Windows development view stores a link marker, as Git with
                # core.symlinks=false does. Canonical tar retains real symlinks;
                # this view is never used as Main source-integrity evidence.
                if not path.exists() and not path.is_symlink():
                    path.write_text(member.linkname, encoding='utf-8')
                continue
            if not member.isfile():
                raise ValueError('Development extraction requires regular tracked files')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(tf.extractfile(member).read())

namespace['safe_extract_archive'] = extract_development_tree
licenses = {'resolvelib': ('ISC', 'LICENSE'), 'injector': ('BSD-3-Clause', 'COPYING'),
            'statemachine': ('MIT', 'LICENSE'), 'doit': ('MIT', 'LICENSE'),
            'celery': ('BSD-3-Clause', 'LICENSE'), 'django': ('BSD-3-Clause', 'LICENSE'),
            'apscheduler': ('MIT', 'LICENSE.txt'), 'scrapy': ('BSD-3-Clause', 'LICENSE'),
            'traitlets': ('BSD-3-Clause', 'LICENSE'), 'transitions': ('MIT', 'LICENSE')}
if __name__ == '__main__':
    records = json.loads((HERE / 'acquisition.json').read_text(encoding='utf-8'))['sources']
    results = []
    for record in records:
        record['license'], record['license_path'] = licenses[record['name']]
        result = namespace['prepare'](record)
        result['development_tree_note'] = 'Windows view; symlink markers possible. Full-Repository Main must extract the canonical archive on Linux.'
        results.append(result)
        print(json.dumps({k: result[k] for k in ['name', 'commit', 'tracked_file_count', 'python_loc']}), flush=True)
    (HERE / 'source_evidence.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
