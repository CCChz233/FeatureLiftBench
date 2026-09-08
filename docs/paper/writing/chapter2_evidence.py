"""Index existing Chapter 2 evidence; no evaluation, network, or task mutation."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    base = 'artifacts/research_analysis/python200_prime/'
    paths = [base + name + '.json' for name in [
        'current_benchmark_freeze', 'current_candidate_freeze',
        'current_repair_semantic_review_v2_closed',
        'current_repair_maintainer_adjudication_v2']]
    paths += ['reports/audits/python200_prime_oracle_revalidation/summary.json',
              'benchmark/references/python200_prime_compactness.json',
              'artifacts/research_analysis/python200_hard_task_taxonomy.csv',
              'benchmark/selection/hard50_expansion_20260827.json']
    freeze, candidate, review, adjudication, oracle, refs = map(read, paths[:6])
    with (ROOT / paths[6]).open(encoding='utf-8-sig', newline='') as stream:
        taxonomy = {row['task_id']: row for row in csv.DictReader(stream)}
    tasks = freeze['tasks']
    assert len(tasks) == 200
    assert set(tasks) == set(candidate['tasks']) == set(refs['tasks']) == set(taxonomy)
    assert candidate['candidate_id'] == oracle['candidate_id']
    assert oracle['summary'] == freeze['oracle_revalidation']['summary']
    assert oracle['summary']['passed_runs'] == 600
    assert review['reviewed_task_count'] == 38 and adjudication['task_count'] == 6
    assert not review['independent_human_review'] and not review['gold']
    inventory = []
    for task_id, task in sorted(tasks.items()):
        folder = 'tasks' if task['stratum'] == 'python150' else 'hard50'
        metadata_path = f'benchmark/{folder}/{task_id}/metadata.json'
        task_path = f'benchmark/{folder}/{task_id}/TASK.md'
        metadata = read(metadata_path)
        spec_hash = hashlib.sha256(json.dumps(metadata['public_spec'], sort_keys=True,
            separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()
        statement_hash = hashlib.sha256((ROOT / task_path).read_text(
            encoding='utf-8').encode('utf-8')).hexdigest()
        assert spec_hash == task['spec_hash'], task_id
        assert statement_hash == task['generated_task_hash'], task_id
        reference = refs['tasks'][task_id]
        assert reference['reference_tree_sha256'] == task['reference_tree']['sha256']
        label = taxonomy[task_id]
        inventory.append({
            'task_id': task_id, 'release_stratum': task['stratum'],
            'construction_group_150': label['construction_split_150'],
            'source_repo_id': task['source_repo_id'],
            'source_snapshot_id': task['source_snapshot_id'],
            'source_commit': task['source_resolved_commit'],
            'spec_hash': spec_hash, 'reference_kind': task['reference_kind'],
            'reference_python_loc': reference['python_loc'],
            'historical_lift_type': label['lift_type'],
            'historical_lift_label_status': label['lift_label_status'],
            'historical_feature_family': label['feature_family_v2'],
            'taxonomy_version': label['taxonomy_version'],
            'taxonomy_source_commit': label['source_commit'],
            'taxonomy_commit_matches_freeze': label['source_commit'] == task['source_resolved_commit'],
        })
    strata = {}
    for group in ['python150', 'hard50', 'complete']:
        rows = [v for v in tasks.values() if group == 'complete' or v['stratum'] == group]
        strata[group] = dict(tasks=len(rows), repositories=len({v['source_repo_id'] for v in rows}),
                            snapshots=len({v['source_snapshot_id'] for v in rows}))
    result = {
        'scope': 'Existing local records and public task content; no new executions or archive verification.',
        'strata': strata, 'candidate_recorded_gates': candidate['pre_runtime_gates'],
        'oracle_recorded_summary': oracle['summary'],
        'repair_llm_review_tasks': review['reviewed_task_count'],
        'repair_maintainer_proxy_adjudication_tasks': adjudication['task_count'],
        'independent_human_review': False,
        'current_public_spec_and_statement_matches': len(inventory),
        'frozen_reference_registry_matches': len(inventory),
        'historical_feature_families': dict(Counter(r['historical_feature_family'] for r in inventory)),
        'historical_label_status': dict(Counter(r['historical_lift_label_status'] for r in inventory)),
        'taxonomy_commit_match_count': sum(r['taxonomy_commit_matches_freeze'] for r in inventory),
        'limitations': [
            'Historical taxonomy is joined by task ID, not revalidated against every current source snapshot.',
            'Hard-50 lift labels have planned_ledger status, not completed annotation status.',
            'Public-content matches do not certify complete task trees or semantic fairness.',
            'Recorded oracle runs do not certify equivalence to every retained agent runtime.',
        ],
        'source_files': [{'path': p, 'sha256': digest(p)} for p in paths],
    }
    (HERE / 'chapter2_task_inventory.json').write_text(json.dumps({
        'release_manifest': paths[0], 'release_manifest_sha256': digest(paths[0]),
        'annotation_note': result['limitations'][:2], 'tasks': inventory,
    }, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (HERE / 'chapter2_evidence.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'strata': strata, 'current_public_content_matches': len(inventory),
                      'taxonomy_commit_matches': result['taxonomy_commit_match_count']}))


if __name__ == '__main__':
    main()
