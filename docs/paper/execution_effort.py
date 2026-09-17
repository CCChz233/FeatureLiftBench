"""Reviewed RQ2 inputs and summaries. No model calls, Docker, or LaTeX compilation.

Import a delivery once with --import-delivery; --check works from the small
curated records alone. Imported checkpoints are observations, not proof that
every transient artifact in the original execution has been recovered.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import statistics
import tarfile

from paper_inputs import ROOT, PAPER, MODELS, SHORT, MODEL_RECORDS, RESULTS, read_csv

DATA = PAPER / 'data/token_efficiency_20260917'
ARCHIVE = ROOT / 'experiments/token实验/token_efficiency_delivery_20260917T051402Z.tar.gz'
VERSION = 'execution_effort_reviewed.v1'


def yes(value):
    return str(value).lower() in ('true', '1')


def quantile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)


def distribution(values):
    return dict(n=len(values), median=quantile(values, .5),
                q1=quantile(values, .25), q3=quantile(values, .75),
                minimum=min(values) if values else None, maximum=max(values) if values else None)


def import_delivery(archive=ARCHIVE):
    """Read selected archive members as bytes; never execute delivered code."""
    with tarfile.open(archive) as handle:
        prefix = archive.name.removesuffix('.tar.gz')
        names = ('run_metrics.csv', 'calls.jsonl.gz', 'artifact_timeline.jsonl.gz',
                 'snapshot_evaluations.csv')
        data = {name: handle.extractfile(f'{prefix}/{name}').read() for name in names}
    raw = list(csv.DictReader(io.StringIO(data['run_metrics.csv'].decode())))
    calls, timelines = defaultdict(list), defaultdict(list)
    for line in gzip.decompress(data['calls.jsonl.gz']).decode().splitlines():
        item = json.loads(line)
        calls[item['run_id']].append(item)
    for line in gzip.decompress(data['artifact_timeline.jsonl.gz']).decode().splitlines():
        item = json.loads(line)
        timelines[item['run_id']].append(item)
    evaluations = {(r['run_id'], r['artifact_hash']): r for r in
                   csv.DictReader(io.StringIO(data['snapshot_evaluations.csv'].decode()))}
    records = []
    for row in raw:
        rid = row['run_id']
        requests = [c for c in calls[rid] if c['inclusion_status'] != 'duplicate']
        included = [c for c in requests if c['inclusion_status'] == 'included']
        complete = bool(requests) and len(included) == len(requests) and all(
            c['usage_verified'] is True and c['input_tokens'] is not None and
            c['output_tokens'] is not None and c['total_tokens'] == c['input_tokens'] + c['output_tokens']
            for c in included)
        total = sum(c['total_tokens'] for c in included) if complete else None
        complete = bool(complete and total > 0 and row['total_tokens'] and total == int(row['total_tokens'])
                        and row['identity_status'] == 'ok')
        record = dict(run_id=rid, configuration=row['configuration'], task_id=row['task_id'],
                      lift_type=row['lift_type'], final_pass=yes(row['final_pass']),
                      include_effort=complete, total_tokens=total if complete else None,
                      total_calls=len(requests), include_checkpoint=False,
                      post_fraction=None, post_calls=None, first_tokens=None,
                      post_input=None, post_output=None, post_cached_input=None,
                      main_accounting_post_fraction=None, stable_post_fraction=None,
                      first_event_id=None, first_hash=None, original_steps=row['original_steps'])
        reasons = []
        if not record['final_pass']:
            reasons.append('final_failure')
        if not complete:
            reasons.append('incomplete_or_unverified_token_ledger')
        if row['token_alignment_status'] != 'exact':
            reasons.append('nonexact_call_alignment')
        for flag in ('final_tree_matches', 'final_eval_matches', 'full_timeline_covered'):
            if not yes(row[flag]):
                reasons.append(flag)
        if row['identity_status'] != 'ok' or row['unresolved_states'] != '0':
            reasons.append('identity_or_evaluation_unresolved')
        if row['task_id'] == 'responses__request_matcher_core__hard3_001':
            reasons.append('documented_dependency_environment_failure')
        states = sorted(timelines[rid], key=lambda s: s['state_index'])
        if not states or any(evaluations.get((rid, s['artifact_hash']), {}).get('eval_status') != 'ok' for s in states):
            reasons.append('incomplete_checkpoint_evaluations')
        passing = [s for s in states if yes(evaluations.get((rid, s['artifact_hash']), {}).get('functional_pass'))]
        if not passing:
            reasons.append('no_observed_passing_checkpoint')
        if not reasons:
            first = passing[0]
            first_tokens = first['cumulative_tokens']
            known = [s['cumulative_tokens'] for s in states if s['cumulative_tokens'] is not None]
            if (first_tokens is None or first['token_alignment_status'] != 'exact'
                    or any(b < a for a, b in zip(known, known[1:]))):
                reasons.append('nonexact_or_nonmonotone_checkpoint_tokens')
            else:
                prefixes, current = [], 0
                for call in included:
                    current += call['total_tokens']
                    prefixes.append(current)
                indices = [i for i, value in enumerate(prefixes) if value == first_tokens]
                if len(indices) != 1:
                    reasons.append('nonunique_checkpoint_call_prefix')
                else:
                    cut = indices[0] + 1
                    later = included[cut:]
                    post = total - first_tokens
                    assert post == sum(c['total_tokens'] for c in later)
                    assert 0 <= post <= total
                    record.update(include_checkpoint=True, first_tokens=first_tokens,
                                  post_fraction=post/total, post_calls=len(later),
                                  post_input=sum(c['input_tokens'] for c in later),
                                  post_output=sum(c['output_tokens'] for c in later),
                                  first_event_id=first['event_id'], first_hash=first['artifact_hash'])
                    if all(c.get('prompt_cache_hit_tokens') is not None for c in included):
                        record['post_cached_input'] = sum(c['prompt_cache_hit_tokens'] for c in later)
                    if all(c.get('main_table_tokens') is not None for c in included):
                        main_total = sum(c['main_table_tokens'] for c in included)
                        if main_total:
                            record['main_accounting_post_fraction'] = sum(c['main_table_tokens'] for c in later)/main_total
                    if row['stable_status'] == 'exact' and row['stable_post_fraction']:
                        record['stable_post_fraction'] = float(row['stable_post_fraction'])
        record['checkpoint_exclusion'] = ';'.join(reasons)
        records.append(record)
    provenance = dict(method=VERSION, source=str(archive.relative_to(ROOT)),
                      source_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                      members_sha256={name: hashlib.sha256(value).hexdigest() for name, value in data.items()},
                      estimand='post-execution after first reconstructed evaluator-passing checkpoint',
                      sample_policy='same conservative, jointly measurable success subset in both panels',
                      accounting='input+output total; cache-hit input is included, not added twice',
                      limitations=['No claim that every transient state was captured by replay.',
                                   'No new Docker replay or model calls in this local integration.',
                                   'Small Qwen sample is descriptive only; no configuration ranking.',
                                   'Luna and GLM historical per-call usage unavailable.'])
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA/'records.json').write_text(json.dumps(records, indent=2)+'\n')
    (DATA/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    return records


def analyze(records):
    official = {(r['model'], r['task_id']): yes(r['functional_pass']) for r in read_csv(RESULTS)}
    assert len(records) == len({r['run_id'] for r in records}) == 900
    assert {(r['configuration'], r['task_id']) for r in records} == set(official)
    assert all(r['final_pass'] == official[r['configuration'], r['task_id']] for r in records)
    summaries, effort, coverage = [], [], []
    for model in MODELS:
        allrows = [r for r in records if r['configuration'] == model]
        successes = [r for r in allrows if r['final_pass']]
        selected = [r for r in allrows if r['include_checkpoint']]
        assert all(r['include_effort'] and r['final_pass'] and not r['checkpoint_exclusion'] for r in selected)
        for r in selected:
            assert abs(r['post_fraction'] - (r['total_tokens']-r['first_tokens'])/r['total_tokens']) < 1e-12
            assert r['post_input'] + r['post_output'] == r['total_tokens'] - r['first_tokens']
            assert isinstance(r['post_calls'], int) and 0 <= r['post_calls'] < r['total_calls']
        summaries.append(dict(configuration=model, short=SHORT[model], success_n=len(successes),
                              checkpoint_n=len(selected), psf=distribution([r['post_fraction'] for r in selected]),
                              calls=distribution([r['post_calls'] for r in selected]),
                              stable=distribution([r['stable_post_fraction'] for r in selected if r['stable_post_fraction'] is not None]),
                              main_accounting=distribution([r['main_accounting_post_fraction'] for r in selected if r['main_accounting_post_fraction'] is not None])))
        for passed in (True, False):
            subset = [r for r in allrows if r['final_pass'] == passed]
            valid = [r for r in subset if r['include_effort']]
            effort.append(dict(configuration=model, short=SHORT[model], outcome='pass' if passed else 'fail',
                               assigned_n=len(subset), usable_n=len(valid),
                               tokens=distribution([r['total_tokens'] for r in valid])))
        for lift in ('all', 'Direct', 'Adapted', 'Composite'):
            for included in (True, False):
                subset = [r for r in successes if (lift == 'all' or r['lift_type'] == lift)
                          and r['include_checkpoint'] == included]
                coverage.append(dict(configuration=model, lift_type=lift, included=included, n=len(subset),
                                     token_summary=distribution([r['total_tokens'] for r in subset if r['include_effort']])))
    return dict(method=VERSION, rows=900, summaries=summaries, effort=effort, coverage=coverage,
                point_data=[r for r in records if r['include_checkpoint']])


def load_analysis():
    records = json.loads((DATA/'records.json').read_text())
    return analyze(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-delivery', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    records = import_delivery() if args.import_delivery else json.loads((DATA/'records.json').read_text())
    result = analyze(records)
    serialized = json.dumps(result, indent=2)+'\n'
    if args.check:
        assert (DATA/'analysis.json').read_text() == serialized, 'Stale execution-effort analysis'
    else:
        (DATA/'analysis.json').write_text(serialized)
    print(json.dumps({r['short']: dict(n=r['checkpoint_n'], psf=r['psf']['median'], calls=r['calls']['median'])
                      for r in result['summaries']}, indent=2))


if __name__ == '__main__':
    main()
