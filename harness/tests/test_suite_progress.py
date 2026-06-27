from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from featureliftbench.suite_progress import SuiteBatchProgressManager
from featureliftbench.suite_progress import format_mini_task_status
from featureliftbench.suite_progress import parse_mini_progress_from_log
from featureliftbench.suite_progress import parse_mini_token_total_from_trajectory


class SuiteProgressTests(unittest.TestCase):
    def test_parse_mini_progress_from_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "stdout.log"
            log_path.write_text(
                "Loading agent config from 'mini.yaml'\n"
                "\n"
                "[red][bold]mini-swe-agent[/bold] (step [bold]3[/bold], [bold]1200 tokens[/bold]):[/red]\n"
                "assistant content\n",
                encoding="utf-8",
            )

            status = parse_mini_progress_from_log(log_path)

            self.assertEqual(status, "Step 3 (1200 toks)")

    def test_parse_mini_progress_from_log_cost_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "stdout.log"
            log_path.write_text(
                "mini-swe-agent (step 1, $0.00):\n"
                "assistant content\n"
                "mini-swe-agent (step 12, $0.00):\n",
                encoding="utf-8",
            )

            status = parse_mini_progress_from_log(log_path)

            self.assertEqual(status, "Step 12")

    def test_parse_mini_token_total_from_trajectory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            trajectory_path = Path(tmp) / "trajectory.json"
            trajectory_path.write_text(
                json.dumps(
                    {
                        "messages": [
                            {
                                "role": "assistant",
                                "extra": {
                                    "response": {
                                        "usage": {
                                            "prompt_tokens": 1000,
                                            "completion_tokens": 200,
                                        }
                                    }
                                },
                            },
                            {
                                "role": "assistant",
                                "extra": {
                                    "response": {
                                        "usage": {
                                            "prompt_tokens": 5000,
                                            "completion_tokens": 700,
                                        }
                                    }
                                },
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            tokens = parse_mini_token_total_from_trajectory(trajectory_path)

            self.assertEqual(tokens, 6900)

    def test_format_mini_task_status_adds_trajectory_tokens(self) -> None:
        status, tokens = format_mini_task_status(step_status="Step 12", tokens=6900)

        self.assertEqual(status, "Step 12 (6,900 toks)")
        self.assertEqual(tokens, 6900)

    def test_task_lifecycle_updates_completed_count(self) -> None:
        manager = SuiteBatchProgressManager(num_tasks=2)
        manager.on_task_start("task_a")
        manager.update_task_status("task_a", "Step 1 (10 toks)", tokens=10)
        manager.on_task_end("task_a", "passed")
        manager.on_task_start("task_b")
        manager.on_task_end("task_b", "failed")

        self.assertEqual(manager.n_completed, 2)
        self.assertEqual(manager._instances_by_exit_status["passed"], ["task_a"])
        self.assertEqual(manager._instances_by_exit_status["failed"], ["task_b"])


if __name__ == "__main__":
    unittest.main()
