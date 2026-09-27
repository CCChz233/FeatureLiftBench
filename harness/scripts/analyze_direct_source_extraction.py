#!/usr/bin/env python3
"""Static diagnostics for prepared DSE artifacts; never runs submissions/tests.

This is all-generated-artifact source overlap, not the paper's success-only Copy.
The trigram index only removes impossible matches; retained comparisons use the
existing minimum-three-line SequenceMatcher metric unchanged.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'harness'))
from featureliftbench.compactness import _python_files, _copied_line_indices
from featureliftbench.metrics import count_python_loc
from featureliftbench.direct_source_extraction import sha


def trigrams(lines):
    return zip(lines, lines[1:], lines[2:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, required=True)
    args = parser.parse_args()
    suite = args.suite.resolve()
    if not any(suite.is_relative_to(ROOT / p) for p in ['experiments', 'reports']):
        raise SystemExit('Expected an experiments/ or reports/ suite')
    prepared = json.loads((suite / 'prepared_suite.json').read_text())
    rows = []
    for record in prepared['tasks']:
        tid = record['task_id']
        source = suite / 'sources' / record['source_snapshot_id']
        submission = suite / 'tasks' / tid / 'submission'
        if not submission.is_dir():
            rows.append({'task_id': tid, 'status': 'no_submission', 'functional_status': 'not_evaluated'})
            continue
        sources = _python_files(source)
        index = defaultdict(set)
        for i, item in enumerate(sources):
            for tri in set(trigrams(item.normalized)):
                index[tri].add(i)
        copied = 0
        for artifact in _python_files(submission):
            candidates = set()
            for tri in trigrams(artifact.normalized):
                candidates.update(index.get(tri, ()))
            n, _ = _copied_line_indices([artifact], [sources[i] for i in sorted(candidates)])
            copied += n
        denominator = count_python_loc(submission)
        syntax = []
        for p in sorted(submission.rglob('*.py')):
            try:
                compile(p.read_bytes(), str(p.relative_to(submission)), 'exec')
            except (SyntaxError, ValueError) as exc:
                syntax.append({'path': str(p.relative_to(submission)), 'error': str(exc)})
        row = {'task_id': tid, 'lift_type': record['lift_type'], 'generation_status': record['generation_status'],
               'entrypoints_unresolved': len(record.get('unresolved_entrypoints', [])),
               'top_level_api_unmapped': len(record.get('unresolved_api', {})),
               'python_files': len(list(submission.rglob('*.py'))), 'normalized_python_loc': denominator,
               'overlapping_loc': copied, 'all_artifact_source_overlap': copied / denominator if denominator else None,
               'syntax_errors': syntax, 'functional_status': 'not_evaluated'}
        rows.append(row)
        print(f"{len(rows)}/40 {tid}: static overlap={row['all_artifact_source_overlap']:.3f}; syntax errors={len(syntax)}", flush=True)
    result = {'metric': 'all_generated_artifact_source_overlap', 'minimum_matching_lines': 3,
              'metric_scope': 'All generated artifacts; NOT success-conditioned Copy and NOT functional correctness.',
              'prepared_suite_sha256': sha(suite / 'prepared_suite.json'),
              'tasks': rows, 'functional_results_available': False,
              'syntax_error_tasks': sum(bool(r.get('syntax_errors')) for r in rows),
              'generation_statuses': dict(Counter(r.get('generation_status', r.get('status')) for r in rows))}
    (suite / 'static_diagnostics.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
