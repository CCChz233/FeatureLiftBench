"""Regression checks for recovered usage and independent response eligibility."""
import unittest
from import_execution_effort import collect_usage, event_responses, validate_alignment, outcome_total


def usage(response_id, prompt=100, completion=10):
    return dict(response_id=response_id, prompt_tokens=prompt, completion_tokens=completion,
                cache_read_tokens=60, cache_write_tokens=0)


def state(*entries):
    return {'stats': {'usage_to_metrics': {'agent': {
        'token_usages': list(entries), 'accumulated_token_usage': {
            k:sum(e[k] for e in entries) for k in ('prompt_tokens','completion_tokens')}}}}}


def audit(tokens=None):
    return dict(timestamp='2026-09-01T00:00:00Z', status=200, prompt_tokens=tokens,
                completion_tokens=None if tokens is None else 10,
                total_tokens=None if tokens is None else tokens+10, usage_verified=tokens is not None)


class RecoveryTests(unittest.TestCase):
    def test_parent_child_usage_is_counted_once(self):
        rows, reasons = collect_usage([state(usage('a'),usage('b')),state(usage('b'))])
        self.assertFalse(reasons)
        self.assertEqual(len(rows),2)
        total,source,reasons=outcome_total([audit(),audit()],rows,reasons)
        self.assertEqual((total,source,reasons),(220,'persisted_usage',[]))

    def test_conflicting_duplicate_is_not_silently_dropped(self):
        _,reasons=collect_usage([state(usage('a')),state(usage('a',120))])
        self.assertIn('conflicting_duplicate_usage',reasons)

    def test_null_audit_can_use_persisted_response_usage(self):
        rows,reasons=collect_usage([state(usage('a'))])
        events=[dict(kind='ActionEvent',llm_response_id='a',timestamp='2026-09-01T00:00:00.1Z')]
        self.assertFalse(validate_alignment(events,[audit()],rows,reasons))
        self.assertEqual(outcome_total([audit()],rows,reasons)[0],110)

    def test_unrecorded_extra_request_invalidates_fallback(self):
        rows,reasons=collect_usage([state(usage('a'))])
        self.assertIsNone(outcome_total([audit(),audit()],rows,reasons)[0])

    def test_condensation_is_in_token_alignment_not_primary_responses(self):
        events=[dict(kind='ActionEvent',llm_response_id='a'),dict(kind='ObservationEvent'),
                dict(kind='Condensation',llm_response_id='c'),dict(kind='ActionEvent',llm_response_id='a'),
                dict(kind='MessageEvent',llm_response_id='b')]
        self.assertEqual(event_responses(events),{'a':0,'c':2,'b':4})
        self.assertEqual(event_responses(events,primary_only=True),{'a':0,'b':4})

    def test_same_call_count_does_not_prove_token_alignment(self):
        rows,reasons=collect_usage([state(usage('b'))])
        events=[dict(kind='ActionEvent',llm_response_id='a',timestamp='2026-09-01T00:00:00.1Z')]
        self.assertIn('usage_event_ids_not_bijective',validate_alignment(events,[audit()],rows,reasons))

    def test_audit_and_persistence_disagreement_rejected_for_timing(self):
        rows,reasons=collect_usage([state(usage('a',120))])
        events=[dict(kind='ActionEvent',llm_response_id='a',timestamp='2026-09-01T00:00:00.1Z')]
        self.assertIn('per_call_usage_mismatch',validate_alignment(events,[audit(100)],rows,reasons))


if __name__=='__main__':unittest.main()
