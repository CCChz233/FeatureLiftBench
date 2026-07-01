from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from featureliftbench.openhands_usage import MAX_ALLOWED_PROMPT_TOKENS
from featureliftbench.openhands_usage import parse_events_jsonl
from featureliftbench.openhands_usage import write_usage_from_events


class OpenHandsUsageTests(unittest.TestCase):
    def test_parse_events_jsonl_aggregates_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "openhands_events.jsonl"
            events_path.write_text(
                "\n".join(
                    [
                        "OpenHands CLI terminal UI may not work correctly",
                        json.dumps(
                            {
                                "type": "assistant_message",
                                "usage": {
                                    "prompt_tokens": 100,
                                    "completion_tokens": 20,
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "assistant_message",
                                "message": {
                                    "usage": {
                                        "prompt_tokens": 50,
                                        "completion_tokens": 10,
                                    }
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            usage = parse_events_jsonl(events_path)

            self.assertEqual(usage["prompt_tokens"], 150)
            self.assertEqual(usage["completion_tokens"], 30)
            self.assertEqual(usage["api_calls"], 2)
            self.assertFalse(usage["context_audit"]["usage_unverified"])
            self.assertEqual(usage["context_audit"]["token_source"], "openhands_jsonl")
            self.assertEqual(usage["context_audit"]["max_prompt_tokens_per_call"], 100)

    def test_parse_events_jsonl_marks_context_violation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "openhands_events.jsonl"
            events_path.write_text(
                json.dumps(
                    {
                        "type": "assistant_message",
                        "usage": {
                            "prompt_tokens": MAX_ALLOWED_PROMPT_TOKENS + 1,
                            "completion_tokens": 1,
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            usage = parse_events_jsonl(events_path)

            self.assertTrue(usage["context_audit"]["context_violation"])

    def test_parse_events_jsonl_without_usage_is_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            events_path = Path(tmp) / "openhands_events.jsonl"
            events_path.write_text(
                json.dumps({"type": "system", "message": "hello"}) + "\n",
                encoding="utf-8",
            )

            usage = parse_events_jsonl(events_path)

            self.assertTrue(usage["context_audit"]["usage_unverified"])
            self.assertFalse(usage["context_audit"]["available"])

    def test_write_usage_from_events_writes_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            events_path = root / "openhands_events.jsonl"
            output_path = root / "openhands_usage.json"
            events_path.write_text(
                json.dumps(
                    {
                        "type": "assistant_message",
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            written = write_usage_from_events(events_path, output_path)

            self.assertIsNotNone(written)
            self.assertTrue(output_path.is_file())
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["prompt_tokens"], 10)
            self.assertFalse(payload["context_audit"]["usage_unverified"])


if __name__ == "__main__":
    unittest.main()
