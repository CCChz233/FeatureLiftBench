"""Reviewed RQ2 inputs and summaries. No model calls, Docker, or LaTeX compilation.

Import the raw delivery once with --import-raw-delivery; --check works from the small
curated records alone. Imported checkpoints are observations, not proof that
every transient artifact in the original execution has been recovered.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from paper_inputs import PAPER, MODELS, SHORT, RESULTS, read_csv

DATA = PAPER / 'data/token_efficiency_20260917'
VERSION = 'execution_effort_recovered.v2'


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
        responses = [r for r in allrows if r['include_response']]
        assert all(r['final_pass'] and not r['response_exclusion'] for r in responses)
        assert all(type(r['post_responses']) is int and 0 <= r['post_responses'] < r['total_primary_responses'] for r in responses)
        assert all(r['include_effort'] and r['final_pass'] and not r['checkpoint_exclusion'] for r in selected)
        for r in selected:
            assert abs(r['post_fraction'] - (r['total_tokens']-r['first_tokens'])/r['total_tokens']) < 1e-12
            assert r['post_input'] + r['post_output'] == r['total_tokens'] - r['first_tokens']
            assert r['include_response']
            assert 0 <= r['post_fraction'] <= 1
        summaries.append(dict(configuration=model, short=SHORT[model], success_n=len(successes),
                              checkpoint_n=len(selected), response_n=len(responses), psf=distribution([r['post_fraction'] for r in selected]),
                              responses=distribution([r['post_responses'] for r in responses]),
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
                point_data=[r for r in records if r['include_checkpoint']],
                response_point_data=[r for r in records if r['include_response']])


def load_analysis():
    records = json.loads((DATA/'records.json').read_text())
    return analyze(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-raw-delivery', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.import_raw_delivery:
        from import_execution_effort import import_raw_delivery
        records, provenance = import_raw_delivery()
        provenance['method'] = VERSION
        DATA.mkdir(parents=True, exist_ok=True)
        (DATA/'records.json').write_text(json.dumps(records, indent=2)+'\n')
        (DATA/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    else:
        records = json.loads((DATA/'records.json').read_text())
    result = analyze(records)
    serialized = json.dumps(result, indent=2)+'\n'
    if args.check:
        assert (DATA/'analysis.json').read_text() == serialized, 'Stale execution-effort analysis'
    else:
        (DATA/'analysis.json').write_text(serialized)
    print(json.dumps({r['short']: dict(n=r['checkpoint_n'], psf=r['psf']['median'], response_n=r['response_n'], responses=r['responses']['median'])
                      for r in result['summaries']}, indent=2))


if __name__ == '__main__':
    main()
