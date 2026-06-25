from __future__ import annotations

import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path

from featureliftbench.agent_adapters import AgentRunConfig
from featureliftbench.agent_adapters import AgentRunContext
from featureliftbench.agent_adapters import MiniSweAgentAdapter
from featureliftbench.agent_runner import _collect_agent_usage
from featureliftbench.agent_runner import _is_rate_limit_failure
from featureliftbench.agent_runner import _merge_suite_runs
from featureliftbench.agent_runner import _sum_agent_usage
from featureliftbench.agent_runner import build_task_prompt
from featureliftbench.agent_runner import discover_task_dirs
from featureliftbench.agent_runner import load_skipped_runs
from featureliftbench.agent_runner import prepare_agent_workspace
from featureliftbench.agent_runner import run_agent_on_path
from featureliftbench.agent_runner import run_agent_on_task
from featureliftbench.metadata import load_metadata


class AgentRunnerTests(unittest.TestCase):
    def test_build_task_prompt_includes_workflow_and_forbidden_gate(self) -> None:
        task_dir = (
            Path(__file__).resolve().parents[2]
            / "benchmark"
            / "sanity"
            / "iniconfig__parse_config__001"
        )
        metadata = load_metadata(task_dir).data
        prompt = build_task_prompt(metadata)

        self.assertIn("## How to work", prompt)
        self.assertIn("Forbidden imports are a hard gate", prompt)
        self.assertIn("Public tests passing does not mean you are done", prompt)
        self.assertIn("final_score = functional_gate", prompt)
        self.assertIn("pytest public_tests/", prompt)

    def test_discover_task_dirs_can_filter_by_task_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "tasks"
            _make_task(dataset / "sample_a")
            _make_task(dataset / "sample_b")

            filtered = discover_task_dirs(dataset, task_ids=["sample_b"])

            self.assertEqual([path.name for path in filtered], ["sample_b"])

    def test_load_skipped_runs_reads_passed_suite_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            suite_dir = root / "prev_run"
            (suite_dir / "sample_a").mkdir(parents=True)
            (suite_dir / "sample_b").mkdir(parents=True)
            (suite_dir / "sample_a" / "run.json").write_text(
                json.dumps({"task_id": "sample_a", "status": "passed"}),
                encoding="utf-8",
            )
            (suite_dir / "sample_b" / "run.json").write_text(
                json.dumps({"task_id": "sample_b", "status": "failed"}),
                encoding="utf-8",
            )
            (suite_dir / "suite.json").write_text(
                json.dumps(
                    {
                        "runs": [
                            {"task_id": "sample_a", "status": "passed"},
                            {"task_id": "sample_b", "status": "failed"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            skipped = load_skipped_runs(suite_dir)

            self.assertEqual(list(skipped), ["sample_a"])
            self.assertEqual(skipped["sample_a"]["status"], "passed")

    def test_merge_suite_runs_preserves_dataset_order(self) -> None:
        task_dirs = [Path("tasks/sample_a"), Path("tasks/sample_b")]
        fresh_runs = [{"task_id": "sample_b", "status": "passed"}]
        skipped_runs = {"sample_a": {"task_id": "sample_a", "status": "passed"}}

        merged = _merge_suite_runs(task_dirs, fresh_runs, skipped_runs)

        self.assertEqual([run["task_id"] for run in merged], ["sample_a", "sample_b"])

    def test_rate_limit_failure_detects_429_message(self) -> None:
        result = {
            "status": "failed",
            "agent": {"reason": "HTTP 429 Too Many Requests"},
            "errors": [],
        }

        self.assertTrue(_is_rate_limit_failure(result))

    def test_rate_limit_failure_detects_exit_status(self) -> None:
        result = {
            "status": "missing_submission",
            "agent": {"usage": {"exit_status": "RateLimitError"}, "stderr_log": ""},
            "errors": ["agent did not create any files under workspace/submission"],
        }

        self.assertTrue(_is_rate_limit_failure(result))

    def test_prepare_agent_workspace_redacts_hidden_material(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = _make_task(root / "sample_task")
            metadata = load_metadata(task_dir).data
            workspace_dir = root / "output" / "workspace"

            task_file = prepare_agent_workspace(task_dir, workspace_dir, metadata)

            self.assertTrue((workspace_dir / "repo" / "sample.py").exists())
            self.assertTrue((workspace_dir / "public_tests" / "test_public.py").exists())
            self.assertTrue((workspace_dir / "submission").is_dir())
            self.assertFalse((workspace_dir / "hidden_tests").exists())
            self.assertFalse((workspace_dir / "evaluation").exists())

            redacted = json.loads((workspace_dir / "metadata.json").read_text(encoding="utf-8"))
            self.assertNotIn("scoring_reference", redacted)
            self.assertNotIn("hidden", redacted["tests"])
            self.assertEqual(redacted["entanglement"]["level"], "low")
            self.assertEqual(redacted["tests"]["public"], "public_tests/")
            task_text = task_file.read_text(encoding="utf-8")
            self.assertIn("## Entanglement Context", task_text)
            self.assertIn("COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT", task_text)

    def test_command_agent_run_creates_submission_and_evaluates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = _make_task(root / "sample_task")
            fake_agent = root / "fake_agent.py"
            command = _write_fake_usage_agent(fake_agent)

            result = run_agent_on_task(
                task_dir,
                root / "output",
                AgentRunConfig(agent="command", command=command, timeout_seconds=120),
            )

            self.assertEqual(result["status"], "passed")
            self.assertTrue(result["agent"]["passed"])
            self.assertTrue(result["submission"]["exists"])
            self.assertEqual(result["evaluation"]["status"], "passed")
            self.assertEqual(result["evaluation"]["scores"]["functional_gate"], 1.0)
            self.assertEqual(result["evaluation"]["scores"]["extraction_ratio"], 0.5)
            self.assertEqual(result["agent"]["usage"]["assistant_steps"], 3)
            self.assertEqual(result["agent"]["usage"]["total_tokens"], 125)
            self.assertNotIn("cost_usd", result["agent"]["usage"])
            self.assertTrue((root / "output" / "run.json").exists())
            run_json = json.loads((root / "output" / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(run_json["agent"]["usage"]["prompt_tokens"], 100)
            self.assertFalse((root / "output" / "workspace" / "hidden_tests").exists())

    def test_suite_json_includes_agent_usage_totals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "tasks"
            _make_task(dataset / "sample_task")
            fake_agent = root / "fake_agent.py"
            command = _write_fake_usage_agent(fake_agent)

            result = run_agent_on_path(
                dataset,
                root / "suite_output",
                AgentRunConfig(agent="command", command=command, timeout_seconds=120),
            )

            self.assertEqual(result["mode"], "suite")
            self.assertEqual(result["summary"]["passed"], 1)
            self.assertEqual(result["agent_usage_totals"]["available_runs"], 1)
            self.assertEqual(result["agent_usage_totals"]["assistant_steps"], 3)
            self.assertEqual(result["agent_usage_totals"]["total_tokens"], 125)
            self.assertEqual(result["runs"][0]["agent_usage"]["total_tokens"], 125)
            suite_json = json.loads(
                (root / "suite_output" / "suite.json").read_text(encoding="utf-8")
            )
            self.assertEqual(suite_json["agent_usage_totals"]["prompt_tokens"], 100)

    def test_suite_can_run_tasks_in_parallel(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "tasks"
            _make_task(dataset / "sample_a")
            _make_task(dataset / "sample_b")
            fake_agent = root / "fake_agent.py"
            command = _write_fake_usage_agent(fake_agent)

            result = run_agent_on_path(
                dataset,
                root / "suite_output",
                AgentRunConfig(agent="command", command=command, timeout_seconds=120),
                num_workers=2,
            )

            self.assertEqual(result["mode"], "suite")
            self.assertEqual(result["num_workers"], 2)
            self.assertEqual(result["summary"]["passed"], 2)
            self.assertEqual(result["agent_usage_totals"]["available_runs"], 2)
            self.assertEqual(result["agent_usage_totals"]["total_tokens"], 250)
            self.assertEqual([run["task_id"] for run in result["runs"]], ["sample_a", "sample_b"])
            suite_json = json.loads(
                (root / "suite_output" / "suite.json").read_text(encoding="utf-8")
            )
            self.assertEqual(suite_json["num_workers"], 2)
            self.assertEqual(suite_json["agent_usage_totals"]["assistant_steps"], 6)

    def test_collects_mini_trajectory_usage_without_cost(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            agent_output = root / "agent"
            agent_output.mkdir()
            (agent_output / "trajectory.json").write_text(
                json.dumps(
                    {
                        "messages": [
                            {"role": "system"},
                            {"role": "assistant"},
                            {"role": "user"},
                            {"role": "assistant"},
                        ],
                        "info": {
                            "exit_status": "Submitted",
                            "model_stats": {
                                "api_calls": 2,
                                "prompt_tokens": 1000,
                                "completion_tokens": 200,
                                "total_tokens": 1200,
                                "trace_tokens": 1200,
                                "billed_tokens": 1200,
                                "cost_usd": 5.0,
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )

            usage = _collect_agent_usage("mini-swe-agent", agent_output)

            self.assertTrue(usage["available"])
            self.assertEqual(usage["assistant_steps"], 2)
            self.assertEqual(usage["total_messages"], 4)
            self.assertEqual(usage["api_calls"], 2)
            self.assertEqual(usage["total_tokens"], 1200)
            self.assertEqual(usage["exit_status"], "Submitted")
            self.assertNotIn("cost_usd", usage)

    def test_missing_agent_usage_is_non_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            usage = _collect_agent_usage("command", Path(tmp) / "agent")

            self.assertFalse(usage["available"])
            self.assertIn("not found", usage["reason"])

    def test_sums_agent_usage_for_suite(self) -> None:
        runs = [
            {
                "agent": {
                    "usage": {
                        "available": True,
                        "assistant_steps": 2,
                        "api_calls": 2,
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    }
                }
            },
            {
                "agent": {
                    "usage": {
                        "available": True,
                        "assistant_steps": 3,
                        "api_calls": 3,
                        "prompt_tokens": 20,
                        "completion_tokens": 7,
                        "total_tokens": 27,
                    }
                }
            },
            {"agent": {"usage": {"available": False, "reason": "missing"}}},
        ]

        totals = _sum_agent_usage(runs)

        self.assertEqual(totals["available_runs"], 2)
        self.assertEqual(totals["missing_runs"], 1)
        self.assertEqual(totals["assistant_steps"], 5)
        self.assertEqual(totals["api_calls"], 5)
        self.assertEqual(totals["prompt_tokens"], 30)
        self.assertEqual(totals["completion_tokens"], 12)
        self.assertEqual(totals["total_tokens"], 42)

    def test_mini_adapter_builds_expected_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            context = AgentRunContext(
                workspace_dir=root / "workspace",
                task_file=root / "workspace" / "TASK.md",
                submission_dir=root / "workspace" / "submission",
                agent_output_dir=root / "agent",
                task_text="Solve this task",
            )
            adapter = MiniSweAgentAdapter()
            config = AgentRunConfig(
                agent="mini-swe-agent",
                agent_bin="mini",
                model="openai/example",
                config="mini.yaml",
                yolo=True,
            )

            command = adapter.build_command(context, config)
            report_command = adapter.build_report_command(context, config)

            self.assertEqual(command[:2], ["mini", "--task"])
            self.assertIn("Solve this task", command)
            self.assertIn("--output", command)
            self.assertIn(str(root / "agent" / "trajectory.json"), command)
            self.assertIn("--exit-immediately", command)
            self.assertIn("--model", command)
            self.assertIn("openai/example", command)
            self.assertIn("--config", command)
            self.assertIn("mini.yaml", command)
            self.assertIn("--yolo", command)
            self.assertIn("@TASK.md", report_command)
            self.assertNotIn("Solve this task", report_command)


def _make_task(task_dir: Path) -> Path:
    (task_dir / "repo").mkdir(parents=True)
    (task_dir / "repo" / "sample.py").write_text("VALUE = 1\nOTHER = 2\n", encoding="utf-8")
    (task_dir / "public_tests").mkdir()
    (task_dir / "hidden_tests").mkdir()
    (task_dir / "evaluation").mkdir()
    (task_dir / "requirements.lock").write_text("", encoding="utf-8")
    (task_dir / "evaluation" / "forbidden_imports.txt").write_text("sample\n", encoding="utf-8")
    (task_dir / "evaluation" / "oracle_manifest.json").write_text("{}", encoding="utf-8")
    (task_dir / "metadata.json").write_text(
        json.dumps(_metadata(task_dir.name)),
        encoding="utf-8",
    )
    (task_dir / "public_tests" / "test_public.py").write_text(
        "import featurelifted\n\n"
        "def test_value():\n"
        "    assert featurelifted.VALUE == 1\n",
        encoding="utf-8",
    )
    (task_dir / "hidden_tests" / "test_hidden.py").write_text(
        "from featurelifted import VALUE\n\n"
        "def test_hidden_value():\n"
        "    assert VALUE == 1\n",
        encoding="utf-8",
    )
    return task_dir


def _write_fake_usage_agent(path: Path) -> str:
    path.write_text(
        "from pathlib import Path\n"
        "import json\n"
        "import sys\n"
        "submission = Path(sys.argv[1])\n"
        "agent_output = Path(sys.argv[2])\n"
        "package = submission / 'featurelifted'\n"
        "package.mkdir(parents=True, exist_ok=True)\n"
        "(package / '__init__.py').write_text('VALUE = 1\\n', encoding='utf-8')\n"
        "(agent_output / 'usage.json').write_text(json.dumps({\n"
        "    'assistant_steps': 3,\n"
        "    'total_messages': 7,\n"
        "    'api_calls': 3,\n"
        "    'prompt_tokens': 100,\n"
        "    'completion_tokens': 25,\n"
        "    'total_tokens': 125,\n"
        "    'cost_usd': 999,\n"
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


def _metadata(task_id: str) -> dict:
    return {
        "task_id": task_id,
        "language": "python",
        "source": {
            "name": "sample",
            "url": "https://example.com/sample",
            "commit": "abc123",
            "license": "MIT",
        },
        "feature": {
            "name": "sample feature",
            "description": "A sample feature.",
            "source_entrypoints": ["sample.VALUE"],
            "included_behaviors": ["export value"],
            "excluded_behaviors": [],
        },
        "entanglement": {
            "level": "low",
            "types": ["implicit_dependency_coupling"],
            "description": "Sample task with a small import boundary.",
            "signals": ["single source entrypoint", "no framework runtime"],
        },
        "output": {
            "package": "featurelifted",
            "import": "import featurelifted",
            "callable": "featurelifted.VALUE",
            "signature": "VALUE",
        },
        "environment": {
            "python": "3.11",
            "network": False,
            "timeout_seconds": 30,
            "dependency_lock": "requirements.lock",
            "allowed_dependencies": [],
            "forbidden_dependencies": ["sample"],
            "forbidden_imports": ["sample"],
        },
        "tests": {
            "public": "public_tests/",
            "hidden": "hidden_tests/",
            "command": "pytest",
        },
        "scoring_reference": {
            "copy_all_bytes": 100,
            "copy_all_loc": 10,
            "oracle_bytes": 50,
            "oracle_loc": 5,
            "oracle_dependency_count": 0,
        },
    }


if __name__ == "__main__":
    unittest.main()
