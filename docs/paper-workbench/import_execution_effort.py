"""Import immutable raw evidence for RQ2 without running recorded code or commands.

Reads seven checksum-verified archives. Retains only derived measurements and
source hashes in the paper; raw logs remain in the supplied local delivery.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

from paper_inputs import ROOT, MODELS

RAW_DELIVERY = ROOT / 'experiments/token实验/token_efficiency_raw_20260917T072646Z'


def stamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return (parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed).timestamp()


def jsonlines(data):
    return [json.loads(line) for line in data.decode().splitlines() if line.strip()]


def positive_usage(row, input_key='prompt_tokens', output_key='completion_tokens'):
    return (all(type(row.get(k)) is int and row[k] >= 0 for k in (input_key, output_key))
            and row[input_key] + row[output_key] > 0)


def collect_usage(base_states):
    """Include both agent and condenser, preserving response IDs and real zeros."""
    records, reasons = [], []
    for state in base_states:
        for role, metric in state.get('stats', {}).get('usage_to_metrics', {}).items():
            entries = metric.get('token_usages', [])
            records.extend(dict(entry, role=role) for entry in entries)
            for key in ('prompt_tokens', 'completion_tokens'):
                if sum(entry.get(key, 0) for entry in entries) != metric.get('accumulated_token_usage', {}).get(key, 0):
                    reasons.append('persisted_accumulation_mismatch')
    # Parent metrics may already contain child-agent usage. A shared response
    # is one call; deduplicate only when its numeric token components agree.
    unique = {}
    for entry in records:
        response_id = entry.get('response_id')
        if response_id in unique:
            keys = ('prompt_tokens', 'completion_tokens', 'cache_read_tokens', 'cache_write_tokens')
            if any(entry.get(k) != unique[response_id].get(k) for k in keys):
                reasons.append('conflicting_duplicate_usage')
        else:
            unique[response_id] = entry
    records = list(unique.values())
    ids = [entry.get('response_id') for entry in records]
    if not records:
        reasons.append('persisted_usage_missing')
    if not all(ids) or len(set(ids)) != len(ids):
        reasons.append('missing_or_duplicate_usage_response_id')
    if not all(positive_usage(entry) for entry in records):
        reasons.append('invalid_persisted_usage')
    return records, sorted(set(reasons))


def event_responses(events, primary_only=False):
    """First appearance of each response; token alignment includes Condensation."""
    result = {}
    for index, event in enumerate(events):
        if primary_only and event.get('kind') not in ('ActionEvent', 'MessageEvent'):
            continue
        if event.get('llm_response_id'):
            result.setdefault(event['llm_response_id'], index)
    return result


def validate_alignment(events, audit, usages, persistence_reasons):
    reasons = list(persistence_reasons)
    first = event_responses(events)
    by_id = {row.get('response_id'): row for row in usages}
    if set(first) != set(by_id):
        reasons.append('usage_event_ids_not_bijective')
    if len(audit) != len(first):
        reasons.append('audit_response_count_mismatch')
    if not reasons:
        for (response_id, index), call in zip(first.items(), audit):
            usage = by_id[response_id]
            try:
                adjacent = 0 <= stamp(events[index]['timestamp']) - stamp(call['timestamp']) < 2
            except (KeyError, ValueError, TypeError):
                adjacent = False
            if not adjacent:
                reasons.append('audit_event_timestamp_not_adjacent')
            if str(call.get('status')) != '200':
                reasons.append('non_200_audit_call')
            for key in ('prompt_tokens', 'completion_tokens'):
                if call.get(key) is not None and call[key] != usage[key]:
                    reasons.append('per_call_usage_mismatch')
            if call.get('total_tokens') is not None and call['total_tokens'] != usage['prompt_tokens'] + usage['completion_tokens']:
                reasons.append('per_call_total_mismatch')
    return sorted(set(reasons))


def outcome_total(audit, usages, persistence_reasons):
    """Total-only eligibility does not require recovery of an artifact boundary."""
    numeric = bool(audit) and all(positive_usage(c) and c.get('usage_verified') is True
                                  and c.get('total_tokens') == c['prompt_tokens'] + c['completion_tokens']
                                  and str(c.get('status')) == '200' for c in audit)
    if numeric:
        return sum(c['total_tokens'] for c in audit), 'provider_audit', []
    reasons = list(persistence_reasons)
    if len(audit) != len(usages):
        reasons.append('persisted_usage_audit_count_mismatch')
    if not audit or any(str(c.get('status')) != '200' for c in audit):
        reasons.append('missing_or_non_200_audit')
    # Do not silently substitute a partly observed ledger with conflicting totals.
    for audit_key, usage_key in [('prompt_tokens', 'prompt_tokens'), ('completion_tokens', 'completion_tokens')]:
        if audit and all(c.get(audit_key) is not None for c in audit):
            if sum(c[audit_key] for c in audit) != sum(c[usage_key] for c in usages):
                reasons.append('audit_persistence_total_mismatch')
    if reasons:
        return None, None, sorted(set(reasons))
    return sum(u['prompt_tokens'] + u['completion_tokens'] for u in usages), 'persisted_usage', []


def derive_record(run, raw, analysis, source_hashes):
    events, audit = jsonlines(raw['events']), jsonlines(raw['audit'])
    states = [json.loads(data) for data in raw['bases']]
    usages, persist_reasons = collect_usage(states)
    metric = json.loads(analysis['metrics.json'])
    timeline = sorted(jsonlines(analysis['artifact_timeline.jsonl']), key=lambda x: x['state_index'])
    evaluations = json.loads(analysis['snapshot_evaluations.json'])
    total, total_source, effort_reasons = outcome_total(audit, usages, persist_reasons)
    assert run['official_final_pass'] == str(metric['final_pass']).lower()
    assert metric['identity_status'] == 'ok'
    first = event_responses(events)
    primary = event_responses(events, primary_only=True)
    record = dict(run_id=run['run_id'], configuration=run['configuration'], task_id=run['task_id'],
                  lift_type=metric['lift_type'], final_pass=metric['final_pass'],
                  include_effort=total is not None, total_tokens=total, total_source=total_source,
                  effort_exclusion=';'.join(effort_reasons), include_checkpoint=False,
                  include_response=False, post_fraction=None, post_responses=None,
                  total_primary_responses=len(primary), total_audit_calls=len(audit),
                  first_tokens=None, post_input=None, post_output=None, post_cached_input=None,
                  main_accounting_post_fraction=None, stable_post_fraction=None,
                  first_event_id=None, first_hash=None, source_hashes=source_hashes)
    reasons = []
    if not record['final_pass']:
        reasons.append('final_failure')
    for flag in ('full_timeline_covered', 'final_tree_matches', 'final_eval_matches'):
        if metric.get(flag) is not True:
            reasons.append(flag)
    if metric.get('unresolved_states') != 0:
        reasons.append('unresolved_checkpoint_evaluation')
    if not timeline or any(evaluations.get(s['artifact_hash'], {}).get('eval_status') != 'ok' for s in timeline):
        reasons.append('incomplete_checkpoint_evaluations')
    passing = [s for s in timeline if evaluations.get(s['artifact_hash'], {}).get('functional_pass') is True]
    if not passing:
        reasons.append('no_observed_passing_checkpoint')
    timestamps = [stamp(e['timestamp']) for e in events if e.get('timestamp')]
    if timestamps != sorted(timestamps):
        reasons.append('nonmonotonic_event_timestamps')
    ids = [e.get('id') for e in events]
    if len(set(ids)) != len(ids):
        reasons.append('duplicate_event_ids')
    actions = {e.get('id'):e for e in events if e.get('kind') == 'ActionEvent'}
    for e in events:
        if e.get('kind') == 'ObservationEvent' and e.get('action_id') not in actions:
            reasons.append('unmatched_observation')
    cut = None
    if passing:
        checkpoint = passing[0]
        matches = [i for i,e in enumerate(events) if e.get('id') == checkpoint['event_id']]
        if len(matches) != 1 or events[matches[0]].get('kind') != 'ObservationEvent':
            reasons.append('missing_checkpoint_observation')
        else:
            cut = matches[0]
            rid = checkpoint['llm_response_id']
            if rid not in first or first[rid] > cut:
                reasons.append('invalid_producing_response_boundary')
            record.update(first_event_id=checkpoint['event_id'], first_hash=checkpoint['artifact_hash'])
    if not reasons:
        record.update(include_response=True, post_responses=sum(i > cut for i in primary.values()))
    alignment_reasons = validate_alignment(events, audit, usages, persist_reasons)
    token_reasons = list(reasons) + alignment_reasons
    if total is None:
        token_reasons.append('incomplete_token_total')
    if not token_reasons:
        by_id = {u['response_id']: u for u in usages}
        ledger_total = sum(u['prompt_tokens']+u['completion_tokens'] for u in usages)
        assert total == ledger_total
        later = [by_id[rid] for rid,index in first.items() if index > cut]
        post_input = sum(u['prompt_tokens'] for u in later)
        post_output = sum(u['completion_tokens'] for u in later)
        record.update(include_checkpoint=True, post_input=post_input, post_output=post_output,
                      first_tokens=total-post_input-post_output, post_fraction=(post_input+post_output)/total)
        if all(type(u.get('cache_read_tokens')) is int for u in usages):
            record['post_cached_input'] = sum(u['cache_read_tokens'] for u in later)
        # Compute stable-pass sensitivity from the reconstructed states, not old token prefixes.
        last_fail = max((i for i,s in enumerate(timeline) if not evaluations[s['artifact_hash']]['functional_pass']), default=-1)
        stable = timeline[last_fail+1] if last_fail+1 < len(timeline) else None
        if stable and stable['event_id'] in ids:
            stable_cut = ids.index(stable['event_id'])
            stable_post = sum(by_id[rid]['prompt_tokens']+by_id[rid]['completion_tokens'] for rid,index in first.items() if index > stable_cut)
            record['stable_post_fraction'] = stable_post/total
        if run['configuration'] in ('deepseek-v4-pro','deepseek-v4-flash') and all(
            type(c.get('prompt_cache_miss_tokens')) is int and type(c.get('completion_tokens')) is int for c in audit):
            main_total = sum(c['prompt_cache_miss_tokens']+c['completion_tokens'] for c in audit)
            main_post = sum(c['prompt_cache_miss_tokens']+c['completion_tokens'] for (_,index),c in zip(first.items(),audit) if index > cut)
            record['main_accounting_post_fraction'] = main_post/main_total if main_total else None
    record['response_exclusion'] = ';'.join(sorted(set(reasons)))
    record['checkpoint_exclusion'] = ';'.join(sorted(set(token_reasons)))
    return record


def import_raw_delivery(delivery=RAW_DELIVERY):
    """Read only data members from hash-verified archives; never extract or run code."""
    runs = list(csv.DictReader((delivery/'run_index.csv').open()))
    assert len(runs) == len({r['run_id'] for r in runs}) == 900
    by_prefix = {r['source_run_dir']:r['run_id'] for r in runs}
    raw = {r['run_id']:dict(bases=[]) for r in runs}
    analysis = {r['run_id']:{} for r in runs}
    hashes = {r['run_id']:{} for r in runs}
    archive_hashes = {}
    for line in (delivery/'SHA256SUMS').read_text().splitlines():
        expected, name = line.split()
        path = delivery/name
        with path.open('rb') as stream:
            actual = hashlib.file_digest(stream,'sha256').hexdigest()
        assert actual == expected, f'Archive checksum mismatch: {name}'
        archive_hashes[name] = actual
        with tarfile.open(path, 'r|gz') as archive:
            for member in archive:
                if not member.isfile():
                    continue
                parts = PurePosixPath(member.name).parts
                assert not member.name.startswith('/') and '..' not in parts
                if name.endswith('_analysis.tar.gz'):
                    if len(parts) != 5 or parts[:2] != ('analysis','per_run'):
                        continue
                    rid = '/'.join(parts[2:4])
                    if rid in analysis and parts[4] in ('metrics.json','artifact_timeline.jsonl','snapshot_evaluations.json'):
                        data = archive.extractfile(member).read()
                        analysis[rid][parts[4]] = data
                        hashes[rid][member.name] = hashlib.sha256(data).hexdigest()
                else:
                    prefix = '/'.join(parts[:6])
                    rid = by_prefix.get(prefix)
                    if not rid or len(parts) < 8 or parts[6] != 'agent':
                        continue
                    suffix = '/'.join(parts[7:])
                    key = {'openhands_events.jsonl':'events','context_audit.jsonl':'audit'}.get(suffix)
                    is_base = suffix.startswith('openhands_persistence/conversations/') and suffix.endswith('/base_state.json')
                    if key or is_base:
                        data = archive.extractfile(member).read()
                        if is_base: raw[rid]['bases'].append(data)
                        else: raw[rid][key] = data
                        hashes[rid][member.name] = hashlib.sha256(data).hexdigest()
    records = [derive_record(r,raw[r['run_id']],analysis[r['run_id']],hashes[r['run_id']]) for r in runs]
    provenance = dict(source=delivery.relative_to(ROOT).as_posix(), archives_sha256=archive_hashes,
                      run_index_sha256=hashlib.sha256((delivery/'run_index.csv').read_bytes()).hexdigest(),
                      token_source='complete provider audit or complete persisted agent+condenser usage; exact response IDs for token timing',
                      sample_policy='independent token and primary-response samples, both conditional on final success',
                      response_definition='new unique response IDs in ActionEvent/MessageEvent after checkpoint observation; excludes condenser and HTTP retries',
                      accounting='prompt+completion including cached prompt once; token totals include recorded condenser usage',
                      limitations=['Reconstructed observed checkpoints, not every transient state.',
                                   'No new Docker replay or model calls.',
                                   'Configuration-specific recoverable subsets do not establish adjusted rankings.'])
    return records, provenance
