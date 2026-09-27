#!/usr/bin/env python3
"""Prepare a frozen DSE suite, inspect readiness, or evaluate it in Docker.

Preparation only reads public_spec, dependency locks and pinned source archives.
Evaluation is a separate operation and never modifies prepared submissions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'harness'))
from featureliftbench import direct_source_extraction as dse
from featureliftbench.source_archive import materialize_snapshot, source_indexes
from featureliftbench.freeze import file_manifest, manifest_digest

SELECTION = ROOT / 'docs/paper-workbench/experiments/source_ablation_40.json'
REGISTRY = ROOT / 'benchmark/sources/registry.json'
REFERENCE = ROOT / 'archive/paper_unrelated_20260914/benchmark/references/python200_prime_compactness.json'
WHEELS = ROOT / 'archive/paper_unrelated_20260914/benchmark/vendor-wheels'


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def identity(path):
    files = file_manifest([path], root=path)
    return {'sha256': manifest_digest({'files': files}), 'file_count': len(files)}


def preflight(image=None):
    facts = {'docker_available': False, 'image_available': False,
             'wheels_available': WHEELS.is_dir(), 'wheel_count': len(list(WHEELS.glob('*.whl'))),
             'reference_registry_available': REFERENCE.is_file(),
             'formal_evaluation_ready': False}
    try:
        result = subprocess.run(['docker', 'version', '--format', '{{.Server.Version}}'],
                                capture_output=True, text=True, timeout=20)
        facts['docker_available'] = result.returncode == 0
        facts['docker_diagnostic'] = result.stderr.strip()[-1500:]
        if result.returncode == 0:
            facts['docker_version'] = result.stdout.strip()
        if result.returncode == 0 and image:
            inspected = subprocess.run(['docker', 'image', 'inspect', image], capture_output=True, text=True, timeout=20)
            facts['image_available'] = inspected.returncode == 0
            if inspected.returncode == 0:
                row = json.loads(inspected.stdout)[0]
                facts['image'] = {k: row.get(k) for k in ['Id', 'RepoTags', 'RepoDigests', 'Architecture', 'Os']}
    except (OSError, subprocess.TimeoutExpired) as exc:
        facts['docker_diagnostic'] = str(exc)
    facts['formal_evaluation_ready'] = all(facts[k] for k in ['docker_available', 'image_available', 'wheels_available', 'reference_registry_available'])
    return facts


def prepare(output, api_review=None):
    if output.exists():
        raise SystemExit('Refusing to overwrite existing suite; use a new output path.')
    output.mkdir(parents=True)
    selection = json.loads(SELECTION.read_text())
    review = json.loads(api_review.read_text()) if api_review else None
    if review:
        if review['selection_sha256'] != dse.sha(SELECTION):
            raise SystemExit('API review selection identity mismatch.')
        if set(review['tasks']) != {r['task_id'] for r in selection['tasks']}:
            raise SystemExit('API review must retain all selected tasks.')
        shutil.copyfile(api_review, output / 'api_review.json')
    registry = json.loads(REGISTRY.read_text())
    _, snapshots = source_indexes(registry)
    records, sources = [], {}
    for row in selection['tasks']:
        tid = row['task_id']
        snap = snapshots[tid]
        sid = snap['source_snapshot_id']
        if sid not in sources:
            dest = output / 'sources' / sid
            materialize_snapshot(snap, dest, root=ROOT)
            sources[sid] = dest
        task = ROOT / row['task_path']
        metadata = json.loads((task / 'metadata.json').read_text())
        record = {'task_id': tid, 'lift_type': row['lift_type'], 'source_snapshot_id': sid,
                  'source_archive_sha256': snap['archive_sha256'], 'source_tree_sha256': snap['source_tree_sha256'],
                  'public_spec_sha256': hashlib.sha256(json.dumps(metadata['public_spec'], sort_keys=True).encode()).hexdigest(),
                  'dependency_lock_sha256': dse.sha(task / 'requirements.lock')}
        aliases = {}
        if review:
            audited = review['tasks'][tid]
            for key in ['source_snapshot_id', 'source_archive_sha256', 'public_spec_sha256']:
                if audited[key] != record[key]:
                    raise SystemExit(f'API review {key} mismatch: {tid}')
            aliases = audited['aliases']
            for name, target_symbol in aliases.items():
                decision = audited['api_reviews'][name]
                if decision['decision'] != 'direct_alias' or decision['source_symbol'] != target_symbol:
                    raise SystemExit(f'Alias lacks reviewed decision: {tid}/{name}')
            for decision in audited['api_reviews'].values():
                for evidence in decision.get('source_evidence', []):
                    path = (sources[sid] / evidence['path']).resolve()
                    if not path.is_relative_to(sources[sid].resolve()) or dse.sha(path) != evidence['sha256']:
                        raise SystemExit(f'API review source evidence changed: {tid}')
            record['api_review_scope'] = audited['review_scope']
        target = output / 'tasks' / tid
        try:
            result = dse.extract(sources[sid], metadata['public_spec'], target / 'submission', reviewed_aliases=aliases)
            record.update(result)
        except (OSError, SyntaxError, UnicodeError, ValueError) as exc:
            record.update(generation_status='generator_error', error=f'{type(exc).__name__}: {exc}', functional_status='not_evaluated')
        if (target / 'submission').is_dir():
            record['submission_identity'] = identity(target / 'submission')
        dump(target / 'preparation.json', record)
        records.append(record)
        print(f"{len(records)}/40 {tid}: {record['generation_status']}; unresolved API {len(record.get('unresolved_api', {}))}", flush=True)
    summary = {'schema': 'featureliftbench.dse_preparation.v1', 'algorithm': dse.VERSION,
               'created_at': datetime.now(timezone.utc).isoformat(),
               'selection_sha256': dse.sha(SELECTION), 'algorithm_sha256': dse.sha(Path(dse.__file__)),
               'runner_sha256': dse.sha(Path(__file__)), 'task_count': len(records),
               'lift_types': dict(Counter(r['lift_type'] for r in records)),
               'generation_statuses': dict(Counter(r['generation_status'] for r in records)),
               'all_entrypoints_resolved_tasks': sum(not r.get('unresolved_entrypoints', ['error']) for r in records),
               'all_top_level_api_mapped_tasks': sum(not r.get('unresolved_api', {'error': True}) for r in records),
               'functional_outcomes': 'not_evaluated', 'tasks': records}
    summary['api_review_sha256'] = dse.sha(output / 'api_review.json') if review else None
    # Preserve the implementation as well as its digest for future reproduction.
    for path in [Path(dse.__file__), Path(__file__), ROOT / 'harness/scripts/analyze_direct_source_extraction.py']:
        dest = output / 'implementation' / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    dump(output / 'prepared_suite.json', summary)
    dump(output / 'environment_preflight.json', preflight())
    print(json.dumps({k: v for k, v in summary.items() if k != 'tasks'}, indent=2))


def evaluate(output, image, expected_id):
    if not image or not expected_id:
        raise SystemExit('Evaluation requires --image and --expected-image-id; image identity must be selected explicitly.')
    ready = preflight(image)
    dump(output / 'environment_preflight.json', ready)
    if not ready['formal_evaluation_ready']:
        raise SystemExit('Docker/image/dependency preflight not ready; no task has been evaluated.')
    if ready['image']['Id'] != expected_id:
        raise SystemExit('Evaluator image ID mismatch; no task has been evaluated.')
    suite = json.loads((output / 'prepared_suite.json').read_text())
    if dse.sha(SELECTION) != suite['selection_sha256'] or dse.sha(Path(dse.__file__)) != suite['algorithm_sha256']:
        raise SystemExit('Prepared selection/algorithm identity changed; use a separately named experiment.')
    if dse.sha(Path(__file__)) != suite['runner_sha256']:
        raise SystemExit('Prepared runner identity changed; create a separately identified suite.')
    if suite.get('api_review_sha256') and dse.sha(output / 'api_review.json') != suite['api_review_sha256']:
        raise SystemExit('Frozen API review changed; no task has been evaluated.')
    if (output / 'evaluation_started.json').exists():
        raise SystemExit('An evaluation attempt already started. Preserve it; no automatic rerun is allowed.')
    for record in suite['tasks']:
        task = ROOT / 'benchmark/tasks' / record['task_id']
        public = json.loads((task / 'metadata.json').read_text())['public_spec']
        if hashlib.sha256(json.dumps(public, sort_keys=True).encode()).hexdigest() != record['public_spec_sha256']:
            raise SystemExit('Public contract changed: ' + record['task_id'])
        if dse.sha(task / 'requirements.lock') != record['dependency_lock_sha256']:
            raise SystemExit('Dependency lock changed: ' + record['task_id'])
        sub = output / 'tasks' / record['task_id'] / 'submission'
        if 'submission_identity' in record and identity(sub) != record['submission_identity']:
            raise SystemExit('Submission changed: ' + record['task_id'])
    os.environ['FEATURELIFTBENCH_REFERENCE_REGISTRY'] = str(REFERENCE)
    os.environ['FEATURELIFTBENCH_SOURCE_REGISTRY'] = str(REGISTRY)
    os.environ['FEATURELIFTBENCH_SOURCE_CACHE'] = str(ROOT / 'benchmark/sources/archives')
    from featureliftbench import docker_eval
    # Use the existing archived wheelhouse without moving or changing benchmark assets.
    docker_eval.VENDOR_WHEELS_DIR = WHEELS
    dump(output / 'evaluation_started.json', {'image': ready['image'], 'time': datetime.now(timezone.utc).isoformat(),
                                            'prepared_suite_sha256': dse.sha(output / 'prepared_suite.json')})
    rows = []
    for record in suite['tasks']:
        tid = record['task_id']; target = output / 'tasks' / tid
        if record['generation_status'] != 'generated':
            rows.append({'task_id': tid, 'lift_type': record['lift_type'], 'outcome': 'generation_failure', 'gates': None})
            continue
        result = docker_eval.evaluate_submission_docker(ROOT / 'benchmark/tasks' / tid, target / 'submission', target / 'eval', image=image)
        row = {'task_id': tid, 'lift_type': record['lift_type'], 'raw_result': str(Path('tasks') / tid / 'eval/result.json'),
               'functional_gate': (result.get('scores') or {}).get('functional_gate'),
               'gates': {k: result.get(k) for k in ['build_pass', 'public_tests_pass', 'hidden_tests_pass', 'isolation_pass']},
               'status': result.get('status'), 'errors': result.get('errors')}
        rows.append(row)
        dump(output / 'evaluation_results.json', {'assigned': 40, 'completed_records': len(rows), 'results': rows,
                                                'note': 'Raw outcomes; infrastructure failures require separate adjudication before paper analysis.'})
        print(tid, row['status'], flush=True)
    dump(output / 'evaluation_results.json', {'assigned': 40, 'completed_records': len(rows), 'results': rows,
                                            'note': 'Raw outcomes; infrastructure failures require separate adjudication before paper analysis.'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'preflight', 'evaluate'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--image')
    parser.add_argument('--expected-image-id')
    parser.add_argument('--api-review', type=Path, help='Frozen public-source review and name-only alias map (prepare only)')
    args = parser.parse_args()
    output = args.output.resolve()
    if not any(output.is_relative_to(ROOT / base) for base in ['reports', 'experiments']):
        raise SystemExit('Output must be under reports/ or experiments/.')
    if args.command == 'prepare':
        prepare(output, args.api_review)
    elif args.command == 'evaluate':
        evaluate(output, args.image, args.expected_image_id)
    else:
        result = preflight(args.image); dump(output / 'environment_preflight.json', result); print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
