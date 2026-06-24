from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from featureliftbench.suite_progress import SuiteBatchProgressManager
from featureliftbench.suite_progress import parse_mini_progress_from_log


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
