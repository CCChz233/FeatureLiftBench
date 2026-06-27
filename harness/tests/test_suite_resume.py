from __future__ import annotations

import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from featureliftbench.agent_adapters import AgentRunConfig
from featureliftbench.agent_runner import _archive_previous_run
from featureliftbench.agent_runner import _read_task_attempt
from featureliftbench.agent_runner import _task_at_max_attempts
from featureliftbench.agent_runner import load_skipped_runs
from featureliftbench.agent_runner import run_agent_on_path
from featureliftbench.agent_runner import run_agent_on_suite
from featureliftbench.agent_runner import run_agent_on_task
from featureliftbench.suite_utils import load_retained_runs
from featureliftbench.suite_utils import parse_retry_only_statuses
from featureliftbench.suite_utils import rebuild_suite_summary

import test_agent_runner

_make_task = test_agent_runner._make_task
_write_fake_usage_agent = test_agent_runner._write_fake_usage_agent


class SuiteResumeTests(unittest.TestCase):
    def test_load_retained_runs_filters_by_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            suite_dir = Path(tmp) / "suite"
            (suite_dir / "task_a").mkdir(parents=True)
            (suite_dir / "task_b").mkdir(parents=True)
            (suite_dir / "task_a" / "run.json").write_text(
                json.dumps({"task_id": "task_a", "status": "passed"}),
                encoding="utf-8",
            )
            (suite_dir / "task_b" / "run.json").write_text(
                json.dumps({"task_id": "task_b", "status": "missing_submission"}),
                encoding="utf-8",
            )
            (suite_dir / "suite.json").write_text(
                json.dumps(
                    {
                        "runs": [
                            {"task_id": "task_a", "status": "passed"},
                            {"task_id": "task_b", "status": "missing_submission"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            passed_only = load_retained_runs(suite_dir, retain_statuses=frozenset({"passed"}))
            resume_retained = load_retained_runs(
                suite_dir,
                retain_statuses=frozenset({"passed", "failed"}),
            )

            self.assertEqual(list(passed_only), ["task_a"])
            self.assertEqual(sorted(resume_retained), ["task_a"])

    def test_load_skipped_runs_still_reads_only_passed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            suite_dir = Path(tmp) / "suite"
            (suite_dir / "task_a").mkdir(parents=True)
            (suite_dir / "task_b").mkdir(parents=True)
            (suite_dir / "task_a" / "run.json").write_text(
                json.dumps({"task_id": "task_a", "status": "passed"}),
                encoding="utf-8",
            )
            (suite_dir / "task_b" / "run.json").write_text(
                json.dumps({"task_id": "task_b", "status": "failed"}),
                encoding="utf-8",
            )
            (suite_dir / "suite.json").write_text(
                json.dumps(
                    {
                        "runs": [
                            {"task_id": "task_a", "status": "passed"},
                            {"task_id": "task_b", "status": "failed"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            skipped = load_skipped_runs(suite_dir)

            self.assertEqual(list(skipped), ["task_a"])

    def test_parse_retry_only_statuses_rejects_unknown(self) -> None:
        with self.assertRaises(ValueError):
            parse_retry_only_statuses("missing_submission,unknown_status")

    def test_rebuild_suite_summary_groups_tasks_by_status(self) -> None:
        summary = rebuild_suite_summary(
            [
                {"task_id": "a", "status": "passed", "agent": {"passed": True}, "submission": {"exists": True}},
                {
                    "task_id": "b",
                    "status": "missing_submission",
                    "agent": {"passed": True},
                    "submission": {"exists": False},
                },
            ]
        )

        self.assertEqual(summary["by_status"]["passed"], 1)
        self.assertEqual(summary["by_status"]["missing_submission"], 1)
        self.assertEqual(summary["tasks_by_status"]["missing_submission"], ["b"])
        self.assertEqual(summary["recovered_submissions"], 0)

    def test_rebuild_suite_summary_counts_recovered_submissions(self) -> None:
        summary = rebuild_suite_summary(
            [
                {
                    "task_id": "a",
                    "status": "failed",
                    "agent": {"passed": True},
                    "submission": {"exists": True, "recovered": True},
                },
                {
                    "task_id": "b",
                    "status": "passed",
                    "agent": {"passed": True},
                    "submission": {"exists": True, "recovered": False},
                },
            ]
        )

        self.assertEqual(summary["recovered_submissions"], 1)

    def test_archive_previous_run_creates_attempt_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "task_a"
            output.mkdir(parents=True)
            (output / "run.json").write_text(
                json.dumps({"task_id": "task_a", "status": "failed", "attempt": 1}),
                encoding="utf-8",
            )

            next_attempt, previous = _archive_previous_run(output)

            self.assertEqual(next_attempt, 2)
            self.assertEqual(previous, str(output / "run.attempt1.json"))
            self.assertTrue((output / "run.attempt1.json").is_file())

    def test_task_at_max_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp) / "task_a"
            task_dir.mkdir()
            (task_dir / "run.json").write_text(
                json.dumps({"attempt": 2}),
                encoding="utf-8",
            )

            self.assertTrue(_task_at_max_attempts(task_dir, 2))
            self.assertFalse(_task_at_max_attempts(task_dir, 3))
            self.assertEqual(_read_task_attempt(task_dir), 2)

    def test_resume_retries_missing_submission_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "tasks"
            _make_task(dataset / "sample_a")
            _make_task(dataset / "sample_b")
            output = root / "suite_output"
            output.mkdir(parents=True)
            (output / "sample_a").mkdir()
            (output / "sample_a" / "run.json").write_text(
                json.dumps({"task_id": "sample_a", "status": "passed", "attempt": 1}),
                encoding="utf-8",
            )
            (output / "sample_b").mkdir()
            (output / "sample_b" / "run.json").write_text(
                json.dumps(
                    {"task_id": "sample_b", "status": "missing_submission", "attempt": 1}
                ),
                encoding="utf-8",
            )
            (output / "suite.json").write_text(
                json.dumps(
                    {
                        "runs": [
                            {"task_id": "sample_a", "status": "passed"},
                            {"task_id": "sample_b", "status": "missing_submission"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            fake_agent = root / "fake_agent.py"
            command = _write_fake_usage_agent(fake_agent)

            result = run_agent_on_suite(
                [dataset / "sample_a", dataset / "sample_b"],
                output,
                AgentRunConfig(agent="command", command=command, timeout_seconds=120),
                resume_dir=output,
                resume_mode=True,
                retry_only_statuses=frozenset({"missing_submission"}),
            )

            self.assertEqual(result["summary"]["passed"], 2)
            self.assertEqual(result["resume"]["retained"], 1)
            self.assertEqual(result["resume"]["retried"], 1)
            self.assertEqual(result["runs"][0]["task_id"], "sample_a")
            self.assertEqual(result["runs"][0]["status"], "passed")
            self.assertEqual(result["runs"][1]["status"], "passed")
            self.assertTrue((output / "sample_b" / "run.attempt1.json").is_file())
            rerun_json = json.loads((output / "sample_b" / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(rerun_json["attempt"], 2)

    def test_max_task_attempts_skips_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "tasks"
            _make_task(dataset / "sample_a")
            output = root / "suite_output"
            (output / "sample_a").mkdir(parents=True)
            (output / "sample_a" / "run.json").write_text(
                json.dumps({"task_id": "sample_a", "status": "missing_submission", "attempt": 2}),
                encoding="utf-8",
            )
            (output / "suite.json").write_text(
                json.dumps(
                    {
                        "runs": [
                            {"task_id": "sample_a", "status": "missing_submission"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            fake_agent = root / "fake_agent.py"
            command = _write_fake_usage_agent(fake_agent)

            result = run_agent_on_suite(
                [dataset / "sample_a"],
                output,
                AgentRunConfig(agent="command", command=command, timeout_seconds=120),
                resume_dir=output,
                resume_mode=True,
                max_task_attempts=2,
            )

            self.assertEqual(result["resume"]["retried"], 0)
            self.assertEqual(result["resume"]["skipped_max_attempts"], ["sample_a"])
            self.assertEqual(result["summary"]["missing_submissions"], 1)

    def test_extra_agent_passes_reruns_failed_task(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "tasks"
            _make_task(dataset / "sample_a")
            fake_agent = root / "fail_once_agent.py"
            command = _write_fail_once_agent(fake_agent)

            result = run_agent_on_path(
                dataset,
                root / "suite_output",
                AgentRunConfig(agent="command", command=command, timeout_seconds=120),
                extra_agent_passes=1,
            )

            self.assertEqual(result["summary"]["passed"], 1)
            self.assertEqual(result["extra_agent_passes"], 1)
            self.assertTrue((root / "suite_output" / "suite.pass1.json").is_file())
            run_json = json.loads(
                (root / "suite_output" / "sample_a" / "run.json").read_text(encoding="utf-8")
            )
            self.assertEqual(run_json["attempt"], 2)

    def test_run_agent_on_task_records_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = _make_task(root / "sample_task")
            output = root / "output"
            fake_agent = root / "fake_agent.py"
            command = _write_fake_usage_agent(fake_agent)

            first = run_agent_on_task(
                task_dir,
                output,
                AgentRunConfig(agent="command", command=command, timeout_seconds=120),
            )
            second = run_agent_on_task(
                task_dir,
                output,
                AgentRunConfig(agent="command", command=command, timeout_seconds=120),
            )

            self.assertEqual(first["attempt"], 1)
            self.assertEqual(second["attempt"], 2)
            self.assertIn("previous_attempt_json", second)

    def test_extra_agent_passes_uses_mocked_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "tasks"
            _make_task(dataset / "sample_a")
            output = root / "suite_output"
            config = AgentRunConfig(agent="command", command="echo", timeout_seconds=120)

            first_run = {
                "task_id": "sample_a",
                "status": "missing_submission",
                "attempt": 1,
                "agent": {"passed": True, "usage": {"available": False}},
                "submission": {"exists": False},
                "evaluation": {"status": "not-run", "scores": {}},
            }
            second_run = {
                "task_id": "sample_a",
                "status": "passed",
                "attempt": 2,
                "agent": {"passed": True, "usage": {"available": False}},
                "submission": {"exists": True},
                "evaluation": {"status": "passed", "scores": {"final_score": 1.0}},
            }

            with mock.patch(
                "featureliftbench.agent_runner._run_suite_tasks",
                side_effect=[[first_run], [second_run]],
            ) as run_tasks:
                result = run_agent_on_suite(
                    [dataset / "sample_a"],
                    output,
                    config,
                    extra_agent_passes=1,
                )

            self.assertEqual(run_tasks.call_count, 2)
            self.assertEqual(result["summary"]["passed"], 1)
            self.assertEqual(result["summary"]["tasks_by_status"]["passed"], ["sample_a"])


def _write_fail_once_agent(path: Path) -> str:
    path.write_text(
        "from pathlib import Path\n"
        "import json\n"
        "import sys\n"
        "submission = Path(sys.argv[1])\n"
        "agent_output = Path(sys.argv[2])\n"
        "marker = submission.resolve().parent.parent / 'fail_once.marker'\n"
        "if not marker.exists():\n"
        "    marker.write_text('1', encoding='utf-8')\n"
        "    print('skipping submission on first attempt')\n"
        "    sys.exit(0)\n"
        "package = submission / 'featurelifted'\n"
        "package.mkdir(parents=True, exist_ok=True)\n"
        "(package / '__init__.py').write_text('VALUE = 1\\n', encoding='utf-8')\n"
        "(agent_output / 'usage.json').write_text(json.dumps({\n"
        "    'assistant_steps': 1,\n"
        "    'api_calls': 1,\n"
        "    'prompt_tokens': 1,\n"
        "    'completion_tokens': 1,\n"
        "    'total_tokens': 2,\n"
        "}), encoding='utf-8')\n"
        "print('created submission')\n",
        encoding="utf-8",
    )
    return (
        f"{shlex.quote(sys.executable)} "
        f"{shlex.quote(str(path))} "
        "{submission_dir} "
        "{agent_output_dir}"
    )


if __name__ == "__main__":
    unittest.main()
