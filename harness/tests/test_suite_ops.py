from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "harness"))
sys.path.insert(0, str(_REPO_ROOT / "harness" / "scripts"))

import summarize_suite_infra  # noqa: E402
import validate_suite_resume  # noqa: E402


class ValidateSuiteResumeTests(unittest.TestCase):
    def test_valid_suite_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            suite_dir = Path(tmp) / "suite"
            task_dir = suite_dir / "task_a"
            (task_dir / "submission").mkdir(parents=True)
            (task_dir / "agent").mkdir(parents=True)
            (task_dir / "eval").mkdir(parents=True)
            (task_dir / "run.json").write_text(
                json.dumps(
                    {
                        "task_id": "task_a",
                        "status": "passed",
                        "agent": {
                            "usage": {
                                "available": True,
                                "api_calls": 2,
                                "assistant_steps": 2,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            (task_dir / "agent" / "usage.json").write_text(
                json.dumps({"api_calls": 2, "assistant_steps": 2}),
                encoding="utf-8",
            )
            (task_dir / "eval" / "result.json").write_text(
                json.dumps({"sandbox": {"backend": "docker"}}),
                encoding="utf-8",
            )
            (suite_dir / "suite.json").write_text(
                json.dumps({"runs": [{"task_id": "task_a", "status": "passed"}]}),
                encoding="utf-8",
            )

            errors = validate_suite_resume.validate_suite_resume(
                suite_dir,
                require_docker_eval=True,
            )
            self.assertEqual(errors, [])

    def test_zero_steps_with_api_calls_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            suite_dir = Path(tmp) / "suite"
            task_dir = suite_dir / "task_a"
            (task_dir / "submission").mkdir(parents=True)
            (task_dir / "agent").mkdir(parents=True)
            (task_dir / "run.json").write_text(
                json.dumps(
                    {
                        "task_id": "task_a",
                        "status": "passed",
                        "agent": {
                            "usage": {
                                "available": True,
                                "api_calls": 3,
                                "assistant_steps": 0,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            (task_dir / "agent" / "usage.json").write_text(
                json.dumps({"api_calls": 3, "assistant_steps": 0}),
                encoding="utf-8",
            )
            (suite_dir / "suite.json").write_text(
                json.dumps({"runs": [{"task_id": "task_a", "status": "passed"}]}),
                encoding="utf-8",
            )

            errors = validate_suite_resume.validate_suite_resume(suite_dir)
            self.assertTrue(any("assistant_steps" in error for error in errors))


class SummarizeSuiteInfraTests(unittest.TestCase):
    def test_infra_clean_when_only_model_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            suite_dir = Path(tmp) / "suite"
            suite_dir.mkdir()
            (suite_dir / "suite.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "total": 2,
                            "passed": 1,
                            "failure_classes": {
                                "passed": 1,
                                "model_failed": 1,
                            },
                            "agent_failures": 0,
                            "docker_sandbox_failures": 0,
                            "log_limit_failures": 0,
                        },
                        "runs": [
                            {"task_id": "a", "status": "passed"},
                            {"task_id": "b", "status": "failed"},
                        ],
                        "agent_usage_totals": {"total_tokens": 100, "api_calls": 5},
                    }
                ),
                encoding="utf-8",
            )

            summary = summarize_suite_infra.summarize_suite_infra(suite_dir)
            self.assertTrue(summary["infra_clean"])
            self.assertEqual(summary["agent_usage_totals"]["total_tokens"], 100)

    def test_infra_not_clean_on_eval_infra_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            suite_dir = Path(tmp) / "suite"
            suite_dir.mkdir()
            (suite_dir / "suite.json").write_text(
                json.dumps(
                    {
                        "summary": {
                            "total": 1,
                            "passed": 0,
                            "failure_classes": {"eval_infra_failed": 1},
                            "docker_sandbox_failures": 1,
                        },
                        "runs": [{"task_id": "a", "status": "failed"}],
                    }
                ),
                encoding="utf-8",
            )

            summary = summarize_suite_infra.summarize_suite_infra(suite_dir)
            self.assertFalse(summary["infra_clean"])
            self.assertEqual(summary["infra_failure_classes"], {"eval_infra_failed": 1})


if __name__ == "__main__":
    unittest.main()
